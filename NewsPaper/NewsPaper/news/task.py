import datetime
from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from NewsPaper import settings
from .models import (
    Post,
    Subscriber,
    AuthorCategory,
    Author,
    Category,
    RegisterForm,
    PostCategory,
)


@shared_task
def send_mail_every_week():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=5)
    posts = Post.objects.filter(time_create__gte=last_week).order_by("-time_create")
    categories = set(posts.values_list("categories__name", flat=True))
    for cat in categories:
        subscribers = set(Subscriber.objects.filter(category__name=cat))
        subscribers_emails = [s.user.email for s in subscribers]
        posts_send = posts.filter(categories__name=cat)

        html_content = render_to_string(
            "daily_post.html",
            {
                "link": f"{settings.SITE_URL}/news/",
                "posts": posts_send,
            },
        )
        msg = EmailMultiAlternatives(
            subject="Статьи за неделю",
            body="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers_emails,
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def send_notifications(preview, pk, title, subscribers_email):
    html_content = render_to_string(
        "post_created_email.html",
        {"text": preview, "link": f"{settings.SITE_URL}/news/{pk}"},
    )
    msg = EmailMultiAlternatives(
        subject=title,
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_email,
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def new_post_notify(post):
    email_list = []

    for i in post.category.all():
        for j in AuthorCategory.objects.filter(category=i):
            email_list.append(j.author.user.email)

    send_mail(
        subject=f"New post {post.title}",
        message=f"{post.title} | {post.author} | {post.create_data} | {post.preview()}"
        + f"\nhttp://127.0.0.1:8000/news/{post.id}",
        from_email="test.for.sm@yandex.ru",
        recipient_list=email_list,
    )


@shared_task
def weekly_mail():

    all_category = ["sport", "politics", "education", "culture"]
    for i in all_category:
        email_list = []
        posts_id = []
        posts_list = ""

        for j in AuthorCategory.objects.filter(
            category=Category.objects.get(category=i)
        ):
            if j.author.user.email not in email_list:
                email_list.append(j.author.user.email)

        for n in PostCategory.objects.filter(category=Category.objects.get(category=i)):
            if n.post.create_data.timestamp() > (
                datetime.datetime.now().timestamp() - 604800
            ):
                posts_id.append(n.post.id)

        for my_post in posts_id:
            posts_list += f"\nhttp://127.0.0.1:8000/news/{my_post}"

        print(email_list)
        print(posts_id)
        print(posts_list)
        if posts_list:
            send_mail(
                subject=f"Тew posts this week",
                message=posts_list,
                from_email="test.for.sm@yandex.ru",
                recipient_list=email_list,
            )
