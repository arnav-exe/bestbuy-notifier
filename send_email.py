import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email, subject, body):
    msg = EmailMessage()

    msg["From"] = os.getenv("SENDER_ADDRESS")
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content("HTML required")
    msg.add_alternative(body, subtype="html")

    with smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as server:
        server.starttls()
        server.login(
            os.getenv("SENDER_ADDRESS"),
            os.getenv("SENDER_PASSWORD")
        )
        server.send_message(msg)


if __name__ == "__main__":
    to = os.getenv("RECIPIENT_ADDRESS")
    subject = "Test email"
    body = """
    <a href="https://api.bestbuy.com/click/-/6575404/pdp">Click this link</a>
    """

    try:
        send_email(to, subject, body)
    except Exception as e:
        SystemExit(e)

    print("sent!")
