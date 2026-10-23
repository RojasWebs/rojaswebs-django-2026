from datetime import timedelta
from unittest.mock import patch

from django.contrib import admin
from django.db import DatabaseError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import ContactThrottle, Post


@override_settings(RESEND_API_KEY='test-key', CONTACT_FROM_EMAIL='site@example.com', CONTACT_TO_EMAIL='inbox@example.com')
class ContactTests(TestCase):
    def setUp(self):
        self.data = {'name': 'Test Visitor', 'email': 'visitor@example.com', 'message': 'A general project inquiry.', 'website': ''}
        self.sender = patch('website.views.resend.Emails.send', return_value={'id': 'accepted'})
        self.send = self.sender.start()
        self.addCleanup(self.sender.stop)

    def test_valid_inquiry_reaches_provider_and_redirects(self):
        response = self.client.post('/', self.data)
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)
        params = self.send.call_args.args[0]
        self.assertEqual(params['to'], ['inbox@example.com'])
        self.assertEqual(params['reply_to'], 'visitor@example.com')
        self.assertEqual(params['from'], 'site@example.com')
        self.assertIn(self.data['message'], params['text'])
        self.assertEqual(self.send.call_count, 1)
        self.assertContains(self.client.get('/'), 'Your message has been sent')

    def test_invalid_inputs_never_send_and_preserve_values(self):
        for changes in ({'name': ''}, {'email': 'bad'}, {'message': 'x' * 5001}):
            response = self.client.post('/', {**self.data, **changes})
            self.assertEqual(response.status_code, 400)
            self.assertContains(response, 'visitor@example.com' if 'email' not in changes else 'bad', status_code=400)
        self.send.assert_not_called()

    def test_honeypot_never_sends(self):
        self.assertEqual(self.client.post('/', {**self.data, 'website': 'spam'}).status_code, 302)
        self.send.assert_not_called()

    def test_csrf_enforced(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post('/', self.data).status_code, 403)
        self.send.assert_not_called()

    def test_provider_error_is_private_and_preserves_input(self):
        self.send.side_effect = RuntimeError('private-provider-secret')
        with self.assertLogs('website.views', level='WARNING') as logs:
            response = self.client.post('/', self.data)
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, self.data['message'], status_code=503)
        self.assertNotContains(response, 'private-provider-secret', status_code=503)
        self.assertNotIn('private-provider-secret', ''.join(logs.output))

    def test_unaccepted_provider_response_is_not_success(self):
        self.send.return_value = {}
        with self.assertLogs('website.views', level='WARNING'):
            self.assertEqual(self.client.post('/', self.data).status_code, 503)

    @override_settings(RESEND_API_KEY='')
    def test_missing_key_fails_without_sending(self):
        self.assertEqual(self.client.post('/', self.data).status_code, 503)
        self.send.assert_not_called()

    def test_rate_limit_and_shared_proxy_clients(self):
        for _ in range(5):
            self.assertEqual(self.client.post('/', self.data).status_code, 302)
        self.assertEqual(self.client.post('/', self.data).status_code, 429)
        self.assertEqual(self.client.post('/', {**self.data, 'email': 'another@example.com'}).status_code, 302)
        ContactThrottle.objects.update(expires_at=timezone.now())
        self.assertEqual(self.client.post('/', self.data).status_code, 302)

    def test_database_failure_does_not_expose_error(self):
        with patch('website.views.allow_contact', side_effect=DatabaseError('private database detail')):
            with self.assertLogs('website.views', level='WARNING'):
                response = self.client.post('/', self.data)
        self.assertEqual(response.status_code, 503)
        self.assertNotContains(response, 'private database detail', status_code=503)
        self.send.assert_not_called()


class BlogTests(TestCase):
    def setUp(self):
        self.draft = Post.objects.create(title='Private draft', slug='private-draft', body='Unpublished content')
        self.future = Post.objects.create(title='Future post', slug='future-post', body='Scheduled content', status='published', published_at=timezone.now() + timedelta(days=1))
        self.public = Post.objects.create(title='A published post', slug='published-post', body='First paragraph.\n\nSecond paragraph.', status='published', category='Django')

    def test_only_published_due_posts_are_public(self):
        for url in ('/', '/blog/', '/blog/feed/'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, self.public.title)
            self.assertNotContains(response, self.draft.title)
            self.assertNotContains(response, self.future.title)
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(self.future.get_absolute_url()).status_code, 404)

    def test_article_renders_paragraphs_and_escapes_html(self):
        self.public.body = '<script>alert("test")</script>\n\nAnother paragraph.'
        self.public.save()
        response = self.client.get(self.public.get_absolute_url())
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(')
        self.assertContains(response, '<p>Another paragraph.</p>', html=True)

    def test_publish_defaults_to_now(self):
        self.assertIsNotNone(self.public.published_at)
        self.assertIsNone(self.draft.published_at)

    def test_empty_blog(self):
        self.public.delete()
        self.assertContains(self.client.get('/blog/'), 'A new chapter starts here.')

    def test_blog_pagination(self):
        for i in range(7):
            Post.objects.create(title=f'Post {i}', slug=f'post-{i}', body='Blog text', status='published')
        response = self.client.get('/blog/')
        self.assertEqual(len(response.context['page_obj']), 6)
        self.assertEqual(len(self.client.get('/blog/?page=2').context['page_obj']), 2)

    def test_admin_registration_and_login_required(self):
        self.assertIn(Post, admin.site._registry)
        response = self.client.get('/admin/website/post/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_post_rejects_submission_and_link_resolves(self):
        self.assertEqual(reverse('website:blog'), '/blog/')
        self.assertEqual(self.client.post(self.public.get_absolute_url(), {}).status_code, 405)


class ThemeTests(TestCase):
    def test_theme_controls_are_available_on_home_and_blog(self):
        for url in ('/', '/blog/'):
            response = self.client.get(url)
            self.assertContains(response, 'class="theme-toggle"')
            self.assertContains(response, 'aria-label="Switch to light mode"')
            self.assertContains(response, 'rojaswebs-theme')
            self.assertContains(response, 'name="theme-color"')

    def test_dark_mode_is_the_script_default(self):
        response = self.client.get('/')
        self.assertContains(response, 'let theme = "dark"')
