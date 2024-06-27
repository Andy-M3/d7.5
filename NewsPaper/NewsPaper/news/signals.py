from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Subscriber, PostCategory, Post, AuthorCategory, Category
from .tasks import send_notifications
import datetime

@receiver(m2m_changed, sender=PostCategory)
def notify_post_created(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.categories.all()
        subscribers_emails = []
        for cat in categories:
            subscribers = Subscriber.objects.filter(category=cat)
            subscribers_emails += [s.user.email for s in subscribers]

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers_emails)

@receiver(post_save, sender = Post)
def new_post_notify(sender, instance, created, **kwargs):
    if created:
        email_list = []
        for i in Post.objects.get(id = instance.id).category.all():
            for j in AuthorCategory.objects.filter(category = i):
                email_list.append(j.author.user.email)

        send_mail(
            subject = f"New post {instance.title}",
            message = f'{instance.title} | {instance.author} | {instance.create_data} | {instance.preview()}' + f'\nhttp://127.0.0.1:8000/news/{instance.id}',
            from_email='test.for.sm@yandex.ru',
            recipient_list = email_list
        )

        all_category = ["sport", "politics", "education", "culture"]
        for i in all_category:
            email_list = []
            posts_id = []
            posts_list = ""


            for j in AuthorCategory.objects.filter(category = Category.objects.get(category = i)):
                if j.author.user.email not in email_list:
                    email_list.append(j.author.user.email)

            for n in PostCategory.objects.filter(category = Category.objects.get(category = i)):
                if n.post.create_data.timestamp() > (datetime.datetime.now().timestamp() - 604800):
                    posts_id.append(n.post.id)

            for my_post in posts_id:
                posts_list += f'\nhttp://127.0.0.1:8000/news/{my_post}'

            print(email_list)
            print(posts_id)
            print(posts_list)
            if posts_list:
                send_mail(
                    subject = f"Тew posts this week",
                    message = posts_list,
                    from_email='test.for.sm@yandex.ru',
                    recipient_list = email_list
                )
