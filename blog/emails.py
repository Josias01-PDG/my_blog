import json
import urllib.error
import urllib.request

from django.conf import settings
from django.utils.html import escape, linebreaks

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


class EmailError(Exception):
    """Erreur lors de l'envoi d'un email."""


def send_email(to_email, subject, html_content):
    if not settings.BREVO_API_KEY or not settings.NEWSLETTER_FROM_EMAIL:
        raise EmailError("BREVO_API_KEY ou NEWSLETTER_FROM_EMAIL n'est pas configuré.")

    payload = {
        "sender": {
            "name": settings.NEWSLETTER_FROM_NAME,
            "email": settings.NEWSLETTER_FROM_EMAIL,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }
    request = urllib.request.Request(
        BREVO_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": "jo-blog/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise EmailError(f"Brevo a refusé l'envoi ({exc.code}) : {detail}") from exc
    except urllib.error.URLError as exc:
        raise EmailError(f"Connexion à Brevo impossible : {exc.reason}") from exc


def render_newsletter_html(newsletter, unsubscribe_url=None):
    body = linebreaks(newsletter.content, autoescape=True)
    footer = ""
    if unsubscribe_url:
        footer = (
            '<p style="font-size:12px;color:#777;">Tu reçois cet email car tu es inscrit '
            'à la newsletter de Jo-blog. '
            f'<a href="{escape(unsubscribe_url)}">Se désinscrire</a></p>'
        )
    return f"""<!DOCTYPE html>
<html lang="fr">
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #222;">
<h1 style="font-size: 22px;">{escape(newsletter.subject)}</h1>
{body}
<hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
<p style="font-size:12px;color:#777;"><a href="{escape(settings.SITE_URL)}">Jo-blog</a></p>
{footer}
</body>
</html>"""