import imaplib
import smtplib
from email.mime.text import MIMEText
from email.header import decode_header
from email.parser import BytesParser
from email.policy import default
import itchat
from youdao_translate import get_translation

import settings

# Email settings
EMAIL_01 = settings.EMAIL_ONE
EMAIL_02 = "1654115747@qq.com"
EMAIL_PASSWORD = settings.EMAIL_ONE_PASSWORD
IMAP_SERVER = "p220s.chinaemail.cn"
SMTP_SERVER = "s220s.chinaemail.cn"
IMAP_PORT = 143
SMTP_PORT = 25


plain_text = ""
translated_text = ""
original_subject = ""

# Function to check emails
def check_emails():
    global plain_text, translated_text, original_subject

    with imaplib.IMAP4(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(EMAIL_01, EMAIL_PASSWORD)
        mail.select("INBOX")
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        for email_id in email_ids:
            status, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]

            # Parse the email
            email_message = BytesParser(policy=default).parsebytes(raw_email)
            plain_text = email_message.get_body(preferencelist=('plain')).get_content()
            original_subject = email_message['Subject']
            if original_subject:
                original_subject = decode_header(original_subject)[0][0]
                if isinstance(original_subject, bytes):
                    original_subject = original_subject.decode()
            
            # Translate email content
            translated_text = youdao_translate(plain_text)
            
            # Send email content and translation to WeChat
            send_to_wechat(plain_text, translated_text, original_subject)

# Youdao Translation Function
def youdao_translate(text):
    get_translation(text)


# Send email content to WeChat
def send_to_wechat(plain_text, translated_text, original_subject):
    itchat.send(f"Original Subject: {original_subject}\n\nOriginal Email:\n{plain_text}\n\nTranslated Email:\n{translated_text}", toUserName='filehelper')

# Handle WeChat replies
@itchat.msg_register(itchat.content.TEXT)
def wechat_reply(msg):
    global plain_text, translated_text, original_subject

    if msg.text.lower() == "yes":
        forward_email(plain_text, translated_text, original_subject)
        itchat.send("Email forwarded to EMAIL_02.", toUserName='filehelper')
    elif msg.text.lower().startswith("yes("):
        # Extract the custom title text
        custom_title = msg.text[4:-1].strip()
        new_subject = f"{original_subject}---{custom_title}"
        forward_email(plain_text, translated_text, new_subject)
        itchat.send(f"Email forwarded to EMAIL_02 with updated subject: {new_subject}.", toUserName='filehelper')
    elif msg.text.lower() == "no":
        itchat.send("Email discarded.", toUserName='filehelper')
    elif msg.text.lower().startswith("update"):
        new_text = msg.text[7:].strip()
        itchat.send(f"Are you sure for:\n{new_text}", toUserName="filehelper")
        # Await confirmation for updated text
        translated_text = new_text
    else:
        itchat.send("Invalid response. Please type 'yes', 'yes(...)', 'no', or 'update(...)'", toUserName="filehelper")

# Forward email
def forward_email(original, translated, subject):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_01, EMAIL_PASSWORD)
        msg = MIMEText(f"Original:\n{original}\n\nTranslated:\n{translated}", "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = EMAIL_01
        msg["To"] = EMAIL_02
        server.sendmail(EMAIL_01, EMAIL_02, msg.as_string())

# Start WeChat and email checking
def main():
    itchat.auto_login(hotReload=True)
    itchat.run()

    # Periodically check emails
    check_emails()

if __name__ == "__main__":
    main()
