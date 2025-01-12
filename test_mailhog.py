import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create message
msg = MIMEMultipart('alternative')
msg['Subject'] = 'Direct SMTP Test'
msg['From'] = 'test@example.com'
msg['To'] = 'user@example.com'

# Create the body of the message
text = "Hello, this is a test email sent directly via SMTP"
html = """\
<html>
  <head></head>
  <body>
    <p>Hello, this is a test email sent directly via SMTP</p>
  </body>
</html>
"""

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

print('Connecting to SMTP server...')
s = smtplib.SMTP('127.0.0.1', 1026)
print('Connected. Sending message...')
s.set_debuglevel(1)  # Add debugging output
s.send_message(msg)
print('Message sent. Closing connection...')
s.quit()
print('Done!') 