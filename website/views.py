import os

import resend
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render


def home(request):
    send_error = False

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        try:
            validate_email(email)
        except ValidationError:
            return render(
                    request,
                    "website/home.html",
                    {
                        "email_error": "Please enter a valid email address.",
                        "form_name": name,
                        "form_email": email,
                        "form_message": message,
                    },
                )

            if name and email and message:
                try:
                    resend.api_key = os.environ["RESEND_API_KEY"]

                    resend.Emails.send(
                        {
                            "from": "RojasWebs Contact Form <contact@rojaswebs.com>",
                            "to": ["contact.rojaswebspas.diaphragm633@passmail.net"],
                            "reply_to": email,
                            "subject": f"RojasWebs contact from {name}",
                            "text": (
                                f"Name: {name}\n"
                                f"Email: {email}\n\n"
                                f"Message:\n{message}"
                            ),
                        }
                    )

                    messages.success(request, "Thanks! Your message has been sent.")
                    return redirect("/#contact")

                except Exception as exc:
                    print(f"Contact form email error: {exc}")
                    send_error = True

    return render(
        request,
        "website/home.html",
        {"send_error": send_error},
    )