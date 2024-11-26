import imaplib
import settings

# Email settings
EMAIL_01 = settings.EMAIL_ONE
EMAIL_PASSWORD = settings.EMAIL_ONE_PASSWORD
IMAP_SERVER = "p220s.chinaemail.cn"
IMAP_PORT = 143

# Function to detect unseen email numbers
def check_unseen_emails():
    with imaplib.IMAP4(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(EMAIL_01, EMAIL_PASSWORD)
        mail.select("INBOX")
        
        # Search for unseen emails
        status, messages = mail.search(None, "UNSEEN")
        
        # If no unseen emails, return 0
        if status != "OK":
            print("Failed to retrieve emails.")
            return 0
        
        email_ids = messages[0].split()
        return len(email_ids)

# Check and print the number of unseen emails
unseen_count = check_unseen_emails()
print(f"Number of unseen emails: {unseen_count}")