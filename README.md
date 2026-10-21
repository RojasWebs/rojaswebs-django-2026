# RojasWebs

RojasWebs is my personal developer portfolio and an ongoing Django project built to showcase my work and document my growth as a web developer.

## About

The site is built with Django and self-hosted on Linux.

Current features include:

- Responsive portfolio layout
- Project links
- GitHub and LinkedIn links
- Working contact form
- Production deployment
- Web traffic monitoring
- Automated threat detection
- Web Application Firewall protection

## Tech Stack

- Python
- Django
- HTML
- CSS
- JavaScript
- Gunicorn
- Nginx
- Linux
- Cloudflare
- CrowdSec
- Git / GitHub

## Production Architecture

The production site uses a layered architecture:

**Cloudflare → Nginx → Security Layer → Gunicorn → Django**

Backend application services are not directly exposed to the public Internet.

## Security

Security measures include:

- Reverse-proxy isolation
- Real-client IP handling
- Behavioral threat detection
- Nginx remediation
- CrowdSec AppSec / Web Application Firewall
- Protected runtime secrets
- HTTPS through Cloudflare

Sensitive production configuration, credentials, API keys, IP addresses, internal hostnames, and infrastructure details are not stored in this repository.

## Development Process

This project has been developed through hands-on coding, testing, debugging, deployment, and security configuration.

AI-assisted technical guidance has also been used during development and troubleshooting. Configuration changes and tests are reviewed and performed manually.

## Local Development

These commands are for developers who want to run the project locally. They are not required for the live production site.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the Django setup

```bash
python manage.py migrate
python manage.py check
```

### Start the local development server

```bash
python manage.py runserver
```

Then open the local development site at:

`http://127.0.0.1:8000/`

> `127.0.0.1` is the local loopback address. It refers only to the computer running Django and is not a public Internet address.

## Main Project Files

- `website/templates/website/home.html`
- `website/static/website/css/style.css`
- `website/static/website/js/main.js`

## Links

- Website: [RojasWebs.com](https://rojaswebs.com)
- GitHub: [RojasWebs](https://github.com/RojasWebs)

## Status

Actively developed and maintained.


## Contact form and blog

The contact form uses Resend. Set `RESEND_API_KEY` in the server's private environment. Optional `CONTACT_FROM_EMAIL` and `CONTACT_TO_EMAIL` override the existing verified sender and destination. The sender must be authorized by Resend. Never commit API keys or private environment files. The form validates bounded inputs, preserves input on errors, requires CSRF protection, and applies a database-backed submission limit and honeypot. It only confirms delivery after Resend accepts the request; verify actual inbox receipt after deployment. Logs contain generic delivery status only, never provider errors or message contents.

Open `/admin/` and select **Posts** to write a blog entry. New entries default to **Draft**. Supply a title, unique slug, and plain-text body; blank lines separate paragraphs. Set **Published** to make it public. Leaving the publication date blank publishes immediately; a future date schedules it. Draft and scheduled entries stay out of public pages and RSS until their publication time. Entries are available at `/blog/`, with RSS at `/blog/feed/`. No sample posts are published automatically.

Before deployment, back up the existing database and private environment. Install the repository's pinned dependencies, then run `python manage.py check`, `python manage.py test website`, `python manage.py migrate`, and `python manage.py collectstatic --noinput`. Confirm the `website_post` and `website_contactthrottle` tables actually exist before restarting the application service. Retain the existing service, proxy, domain, and secret configuration. Test a real contact inquiry and confirm receipt; check a draft stays private and a published post appears. If an admin account is needed, create it interactively with `python manage.py createsuperuser` and keep its credentials private.
