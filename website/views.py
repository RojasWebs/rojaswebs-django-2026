from datetime import timedelta
import logging

import resend
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import DatabaseError, transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_safe

from .forms import ContactForm
from .models import ContactThrottle, Post

logger = logging.getLogger(__name__)
# Keep provider timeouts below the application worker timeout.
resend.default_http_client = resend.RequestsClient(timeout=10)


def allow_contact(request, email):
    now = timezone.now()
    identity = request.META.get('REMOTE_ADDR', '') + '|' + email.casefold()
    key = salted_hmac('rojaswebs-contact', identity).hexdigest()
    ContactThrottle.objects.filter(expires_at__lte=now).delete()
    with transaction.atomic():
        ContactThrottle.objects.get_or_create(key=key, defaults={'expires_at': now + timedelta(hours=1)})
        return bool(ContactThrottle.objects.filter(key=key, count__lt=5).update(count=F('count') + 1))


@sensitive_post_parameters()
@require_http_methods(['GET', 'POST', 'HEAD'])
def home(request):
    form = ContactForm(request.POST if request.method == 'POST' else None)
    status = 200
    if request.method == 'POST':
        if not form.is_valid():
            status = 400
        elif form.cleaned_data['website']:
            messages.success(request, 'Thanks! Your message has been sent.')
            return redirect(reverse('website:home') + '#contact')
        else:
            data = form.cleaned_data
            try:
                allowed = allow_contact(request, data['email'])
            except DatabaseError:
                logger.warning('Contact submission temporarily unavailable.')
                allowed = None
            if allowed is None:
                form.add_error(None, 'Messaging is temporarily unavailable. Please try again later.')
                status = 503
            elif not allowed:
                form.add_error(None, 'Too many attempts. Please try again in an hour.')
                status = 429
            elif not settings.RESEND_API_KEY:
                form.add_error(None, 'Messaging is temporarily unavailable. Please try again later.')
                status = 503
            else:
                try:
                    resend.api_key = settings.RESEND_API_KEY
                    result = resend.Emails.send({
                        'from': settings.CONTACT_FROM_EMAIL,
                        'to': [settings.CONTACT_TO_EMAIL],
                        'reply_to': data['email'],
                        'subject': 'RojasWebs website inquiry',
                        'text': f"Name: {data['name']}\nEmail: {data['email']}\n\nMessage:\n{data['message']}",
                    })
                    if not isinstance(result, dict) or not result.get('id'):
                        raise ValueError('No delivery acceptance.')
                except Exception:
                    # Never log provider errors, credentials, or submitted content.
                    logger.warning('Contact email delivery failed.')
                    form.add_error(None, 'Your message could not be sent. Please try again later.')
                    status = 503
                else:
                    messages.success(request, 'Thanks! Your message has been sent.')
                    return redirect(reverse('website:home') + '#contact')
    response = render(request, 'website/home.html', {
        'form': form, 'latest_posts': Post.objects.published()[:3],
    }, status=status)
    response['Cache-Control'] = 'no-store'
    return response


@require_safe
def blog(request):
    posts = Paginator(Post.objects.published(), 6).get_page(request.GET.get('page'))
    return render(request, 'website/blog.html', {'page_obj': posts})


@require_safe
def post_detail(request, slug):
    post = get_object_or_404(Post.objects.published(), slug=slug)
    return render(request, 'website/post_detail.html', {'post': post})
