import threading

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class EmailThread(threading.Thread):
    def __init__(self, subject, html_template, context, from_email, recipient_list):
        super().__init__()
        self.subject = subject
        self.html_template = html_template
        self.context = context
        self.recipient_list = recipient_list
        self.from_email = from_email

    def run(self):
        html_content = render_to_string(self.html_template, self.context)

        email = EmailMessage(
            subject=self.subject,
            body=html_content,
            from_email=self.from_email,
            to=self.recipient_list
        )

        email.content_subtype = 'html'
        email.send()


def async_send_mail(subject, html_template, context, from_email, recipient_list,  *args, **kwargs):
    EmailThread(subject, html_template, context,  from_email, recipient_list).start()