from django.db import models
from django.contrib.auth.models import User
from main.models import Article
from django.db.models.signals import post_save
from django.dispatch import receiver


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(max_length=250, null=True, blank=True)
    conf_num = models.CharField(max_length=20)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    clicked_articles = models.ManyToManyField(Article, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Newsletter(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=150)
    contents = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.subject + " " + self.created_at.strftime("%B %d, %Y")

    def send(self, request):
        #contents = self.contents.read().decode('utf-8')
        subscribers = Subscriber.objects.filter(confirmed=True)
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        for sub in subscribers:
            message = Mail(
                    from_email='alimardan_akhmedov@hotmail.com',
                    to_emails=sub.email,
                    subject=self.subject,
                    html_content=self.contents + (
                        '<br><a href="{}?email={}&conf_num={}">Unsubscribe</a>.').format(
                            request.build_absolute_uri('/delete/'),
                            sub.email,
                            sub.conf_num))
            sg.send(message)            