"""
send_daily_email.py

Personal, single-recipient version: runs once a day (triggered by the
GitHub Actions workflow in .github/workflows/daily-feast-email.yml),
checks today's date against the Catholic feast calendar, and -- if
today is a feast, solemnity, or saint's day -- emails you the details.

No Flask, no database, no signup form. Just a script and a schedule.

Supports two ways to send email, so you don't need to sign up for a
paid/limited service just to email yourself once a day:

  1. SMTP (e.g. Gmail with an App Password) -- set EMAIL_HOST, EMAIL_PORT,
     EMAIL_USER, EMAIL_PASSWORD. This is the simplest option if you
     already have a Gmail account.
  2. SendGrid API -- set SENDGRID_API_KEY, FROM_EMAIL instead.

If SENDGRID_API_KEY is set, SendGrid is used; otherwise it falls back
to SMTP. You only need to fill in one of the two sets of credentials.

All of these values come from GitHub Actions "Secrets" when run in CI
(Settings -> Secrets and variables -> Actions), or from a local `.env`
file when you test it on your own machine.
"""

import os
import sys
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from liturgical_calendar import get_feast

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_NAME = os.getenv("FROM_NAME", "Catholic Calendar")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

TIMEZONE = os.getenv("TIMEZONE", "Africa/Lagos")
SEND_ON_ORDINARY_DAYS = os.getenv("SEND_ON_ORDINARY_DAYS", "false").strip().lower() == "true"


# ---------------------------------------------------------------------------
# Message building
# ---------------------------------------------------------------------------
def build_message(feast: dict, today: datetime) -> tuple[str, str]:
    date_str = today.strftime("%A, %B %d")
    dos = "\n".join(f"  + {item}" for item in feast["dos"])
    donts = "\n".join(f"  - {item}" for item in feast["donts"])

    subject = f"{feast['name']} \u2014 {date_str}"
    body = (
        f"\u271d\ufe0f {date_str}\n"
        f"Today: {feast['name']}\n"
        f"({feast['rank']})\n\n"
        f"{feast['blurb']}\n\n"
        f"DO:\n{dos}\n\n"
        f"DON'T:\n{donts}\n\n"
        f'"{feast["verse_text"]}"\n'
        f"\u2014 {feast['verse_ref']}"
    )
    return subject, body


def build_ordinary_day_message(today: datetime) -> tuple[str, str]:
    date_str = today.strftime("%A, %B %d")
    subject = f"An ordinary day \u2014 {date_str}"
    body = (
        f"\u271d\ufe0f {date_str}\n"
        "Today has no major feast on the Church calendar -- an ordinary "
        "weekday in Ordinary Time or a particular season.\n\n"
        "Take a moment for prayer, and consider today's Mass readings "
        "in your missal or on a site like universalis.com."
    )
    return subject, body


# ---------------------------------------------------------------------------
# Sending
# ---------------------------------------------------------------------------
def send_via_sendgrid(subject: str, body: str) -> None:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    if not (TO_EMAIL and FROM_EMAIL):
        raise RuntimeError("TO_EMAIL and FROM_EMAIL must both be set.")

    message = Mail(
        from_email=(FROM_EMAIL, FROM_NAME),
        to_emails=TO_EMAIL,
        subject=subject,
        plain_text_content=body,
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    log.info("SendGrid response: status=%s", response.status_code)


def send_via_smtp(subject: str, body: str) -> None:
    if not (TO_EMAIL and EMAIL_USER and EMAIL_PASSWORD):
        raise RuntimeError("TO_EMAIL, EMAIL_USER, and EMAIL_PASSWORD must all be set.")

    msg = MIMEMultipart()
    msg["From"] = f"{FROM_NAME} <{EMAIL_USER}>"
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())

    log.info("Email sent via SMTP to %s", TO_EMAIL)


def send_email(subject: str, body: str) -> None:
    if SENDGRID_API_KEY:
        send_via_sendgrid(subject, body)
    else:
        send_via_smtp(subject, body)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not TO_EMAIL:
        log.error("TO_EMAIL is not set. Add it as a repo secret (or in .env for local testing).")
        sys.exit(1)

    now = datetime.now(ZoneInfo(TIMEZONE))
    log.info("Checking feast calendar for %s (timezone=%s)", now.date(), TIMEZONE)

    feast = get_feast(now.date())

    if feast:
        log.info("Today is: %s", feast["name"])
        subject, body = build_message(feast, now)
    elif SEND_ON_ORDINARY_DAYS:
        log.info("No feast today; SEND_ON_ORDINARY_DAYS is true, sending a plain reminder.")
        subject, body = build_ordinary_day_message(now)
    else:
        log.info("No feast today and SEND_ON_ORDINARY_DAYS is false. Nothing to send.")
        return

    send_email(subject, body)


if __name__ == "__main__":
    main()
