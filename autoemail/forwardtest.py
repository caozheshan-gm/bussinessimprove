import imaplib
import smtplib
from email.parser import BytesParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr, make_msgid
from datetime import datetime

# 邮箱配置
IMAP_SERVER = 'p220s.chinaemail.cn'
IMAP_PORT = 143
SMTP_SERVER = 's220s.chinaemail.cn'
SMTP_PORT = 25

EMAIL_ACCOUNT = 'unibear01@unibear.com'
EMAIL_PASSWORD = '2024UB#@$$$Sales888'
FORWARD_TO_EMAIL = '1654115747@qq.com'

# 连接到IMAP服务器并获取未读邮件
def fetch_unseen_emails():
    with imaplib.IMAP4(IMAP_SERVER) as mail:
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')  # 选择收件箱

        # 搜索所有未读邮件
        status, email_ids = mail.search(None, 'UNSEEN')
        email_ids = email_ids[0].split()

        if not email_ids:
            print("没有未读邮件")
            return []

        unseen_emails = []
        for email_id in email_ids:
            status, data = mail.fetch(email_id, '(RFC822)')
            raw_email = data[0][1]
            msg = BytesParser().parsebytes(raw_email)
            unseen_emails.append(msg)
        
        return unseen_emails

# 转发邮件，包括文本、HTML、附件等
def forward_email(msg):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        
        # 创建转发邮件
        # forward_msg['Date'] = formataddr(('Sender', datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')))

        forward_msg = MIMEMultipart()
        forward_msg['From'] = EMAIL_ACCOUNT
        forward_msg['To'] = FORWARD_TO_EMAIL
        forward_msg['Subject'] = "Fwd: " + msg['Subject']

        

        # 如果邮件是多部分的，遍历所有部分并将其转发
        if msg.is_multipart():
            for part in msg.walk():  # 使用 walk() 代替 iter_parts()
                # 如果部分是文本或HTML，直接添加
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    forward_msg.attach(MIMEText(payload, 'plain', 'utf-8'))
                elif part.get_content_type() == 'text/html':
                    payload = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    forward_msg.attach(MIMEText(payload, 'html', 'utf-8'))
                # 如果是附件或图片等其他类型，转发为附件
                else:
                    part_filename = part.get_filename()
                    if part_filename:  # 确保该部分有文件名
                        attachment = MIMEBase(part.get_content_type(), part.get_content_subtype())
                        attachment.set_payload(part.get_payload(decode=True))
                        encoders.encode_base64(attachment)
                        attachment.add_header('Content-Disposition', f'attachment; filename="{part_filename}"')
                        forward_msg.attach(attachment)
        else:
            # 如果邮件不是多部分的，直接附加邮件正文
            payload = msg.get_payload(decode=True).decode('utf-8', errors='replace')
            forward_msg.attach(MIMEText(payload, 'plain', 'utf-8'))
        
        # 发送邮件
        server.sendmail(EMAIL_ACCOUNT, FORWARD_TO_EMAIL, forward_msg.as_string())
        print(f"邮件已转发: {msg['Subject']}")

   

        # 保存到已发送邮件文件夹
        save_sent_email(forward_msg)

# 将转发的邮件存储到已发送邮件文件夹
def save_sent_email(forward_msg):
    with imaplib.IMAP4(IMAP_SERVER) as mail:
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('INBOX.AUTOFORWARD')  # 选择“已发送”文件夹（针对Bossmail，假设已发送文件夹为 'Sent'）
        try:
            mail.append('INBOX.AUTOFORWARD', '(\Seen)', None, forward_msg.as_string().encode('utf-8'))  # 存储到已发送文件夹
            print("邮件已保存到已发送文件夹")
        except Exception as e:
            print(f"保存邮件到已发送文件夹时发生错误: {e}")
# 主程序
if __name__ == "__main__":
    unseen_emails = fetch_unseen_emails()  # 获取未读邮件
    for email in unseen_emails:
        forward_email(email)  # 转发未读邮件
