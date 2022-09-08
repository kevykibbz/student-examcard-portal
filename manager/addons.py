from django.http import BadHeaderError
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .tokens import create_token
from django.conf import settings
import threading
from installation.models import SiteConstants
from django.core.cache import cache
from smtplib import SMTPException
#threads
class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)
    def run(self):
        try:
            self.email.send()
        except SMTPException as e:
            print('error sending mail'+e)
        except BadHeaderError:
            print('Invalid header found')
        except:
            print('Error sending mail')


#send email
def send_email(subject,email,message,template):
    mail_subject=subject
    html_content=render_to_string(template,message)
    text_content=strip_tags(html_content)
    to_email=email
    email=EmailMultiAlternatives(mail_subject,text_content,settings.EMAIL_HOST_USER,[to_email])
    email.attach_alternative(html_content,'text/html')
    EmailThread(email).start()

#site constants
def getSiteData():
    if cache.get('obj_key'):
        return cache.get('obj_key')
    else:
        obj=SiteConstants.objects.values()[0]
        cache.set('obj_key',obj)
        return obj

#get user initials
def get_initials(fullname):
    name_list=fullname.split()
    initials=''
    for name in name_list:
        initials+=name[0].upper()
        return initials

#social links
def sociallinks():
    return {
                    "facebook":
                                {
                                "username":"kevy.kibbz",
                                "link":"https://web.facebook.com/kevy.kibbz/"
                                },
                    "twitter":
                                {
                                "username":"Kevin36285655",
                                "link":"https://twitter.com/Kevin36285655"
                                },
                    "instagram":
                                {
                                "username":"kevviey",
                                "link":"ttps://www.instagram.com/kevviey/"
                                },
                    "github":
                                {
                                "username":"kevin",
                                "link":"https://github.com"
                                },
                    "whatsapp":
                                {
                                "username":"kevin",
                                "link":"https://wa.link/r9fxm4"
                                },
                    "linkedin":
                                {
                                "username":"chill-cash-260aba206",
                                "link":"https://www.linkedin.com/in/chill-cash-260aba206/"
                                },
                    "youtube":
                                {
                                "username":"kevin kibebe",
                                "link":"https://youtube.com"
                                },
                    }