import threading

from django.core.mail import EmailMultiAlternatives


class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list, fail_silently, html):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(subject=self.subject, body=self.message, from_email=self.from_email, to=self.recipient_list)
        if self.html:
            msg.attach_alternative(self.html, "text/html")
        msg.send(self.fail_silently)


def async_send_mail(subject, message, from_email, recipient_list, fail_silently=False, html=None, *args, **kwargs):
    EmailThread(subject, message, from_email, recipient_list, fail_silently, html).start()