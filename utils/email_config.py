from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import environ

env = environ.Env(
    DEBUG=(bool, False)
)


def send_email(email, subject, values, template):
    try:
        # from_email = "Sparetan {0}".format(env("DEFAULT_FROM_EMAIL"))
        from_email = env("DEFAULT_FROM_EMAIL")
        htmly = get_template(template_name=template)
        html_content = htmly.render(values)
        msg = EmailMultiAlternatives(
            subject, '', from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return True

    except Exception as ex:
        print("Email failed to send " + str(ex))
        return False
