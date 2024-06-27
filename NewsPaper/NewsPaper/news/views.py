from django.http import HttpResponseRedirect, request
from django.shortcuts import render
from datetime import datetime
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
)
from .forms import PostForm
from django.urls import reverse_lazy
from .filters import PostFilter
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from .models import (
    Post,
    Subscriber,
    Category,
    AuthorCategory,
    Author,
    RegisterForm,
    PostCategory,
)
from .filters import PostSearch, PostFilter
from .tasks import new_post_notify

# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД


class NewsList(ListView):
    model = Post
    ordering = "title"
    template_name = "News.html"
    context_object_name = "news"
    extra_context = {"title": "Новости"}
    author = "author"
    # queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    # Переопределяем функцию получения списка товаров
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.filterset = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostSearch(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_date(self, **kwargs):
        context = super().get_context_date(**kwargs)
        context["filterset"] = self.filterset
        return context

    def post_search(request):
        f = PostSearch(request.GET, queryset=Post.objects.all())
        return render(request, "news_search.html", {"filter": f})

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_date(**kwargs)
    #     context["limit_for_listing"] = (
    #         Paginator(list(Post.objects.all()), 5).num_pages - 2
    #     )
    #     context["all_posts"] = Post.objects.all()
    #     context["is_not_author"] = not self.request.user.groups.filter(
    #         name="authors"
    #     ).exists()
    #     context["anonymous"] = self.request.user.is_authenticated
    #     if self.request.user.is_authenticated:
    #         context["author"] = Author.objects.filter(
    #             user=User.objects.get(username=self.request.user)
    #         )
    #     if self.request.user.is_authenticated:
    #         if Author.objects.filter(user=User.objects.get(username=self.request.user)):
    #             all_category = ["sport", "politics", "education", "culture"]
    #             for i in AuthorCategory.objects.filter(
    #                 author=Author.objects.get(
    #                     user=User.objects.get(username=self.request.user)
    #                 )
    #             ):
    #                 if i.category.category in all_category:
    #                     all_category.remove(i.category.category)
    #             context["all_category"] = all_category
    #     return context


class NewsDetail(DetailView):
    model = Post
    template_name = "onenews.html"
    context_object_name = "onenews"

    def get_context_date(self, **kwargs):
        context = super().get_context_date(**kwargs)
        context["is_not_author"] = not self.request.user.groups.filter(
            name="authors"
        ).exists()
        context["time_now"] = datetime.UTC()
        return context


class PostSearchView(ListView):
    model = Post
    template_name = "search.html"
    context_object_name = "NewsSearch"
    paginate_by = 10
    ordering = ["-id"]
    queryset = Post.objects.all()

    def get_filter(self):
        return PostSearch(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_date(self, **kwargs):
        return {
            **super().get_context_date(**kwargs),
            "filter": self.get_filter(),
        }


# class AddPost(LoginRequiredMixin, PermissionRequiredMixin, ListView):
#     model = Post
#     template_name = "addpost.html"
#     permission_required = "backend.add_post"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["authors"] = Author.objects.all()
#         context["categories"] = Category.objects.all()
#         context["new_post_id"] = len(Post.objects.all()) + 1
#         return context
#
#     def post(self, request, *args, **kwargs):
#         title = request.POST["title"]
#         content = request.POST["content"]
#         author = request.POST["author"]
#         post_type = request.POST["post_type"]
#         my_category = request.POST["category"]
#         post = Post(
#             author=Author.objects.get(user=author),
#             title=title,
#             content=content,
#             post_type=post_type,
#         )
#         post.save()
#         post.category.add(Category.objects.get(category=my_category))
#         new_post_notify.delay(post)
#         return HttpResponseRedirect(f"{post.id}")


class PostCreateAR(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ("news.add_post",)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = "articles_edit.html"

    def form_valid(self, form):
        post = form.save(commit=True)
        post.categoryType = "AR"
        return super().form_valid(form)


class PostCreateNW(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ("news.add_post",)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = "news_edit.html"

    def form_valid(self, form):
        post = form.save(commit=True)
        post.categoryType = "NW"
        return super().form_valid(form)


class PostEditNW(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Post
    permission_required = ("news.add_post",)
    raise_exception = True
    form_class = PostForm
    context_object_name = "post"
    template_name = "news_edit.html"


class PostDeleteNW(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ("news.add_post",)
    raise_exception = True
    model = Post
    template_name = "news_delete.html"
    success_url = reverse_lazy("post_list")


class PostEditAR(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ("news.add_post",)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = "articles_edit.html"


class PostDeleteAR(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ("news.add_post",)
    raise_exception = True
    model = Post
    template_name = "articles_delete.html"
    success_url = reverse_lazy("post_list")

class NewsLogin(LoginView):
    template_name = 'login.html'

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    success_url = '/'


@login_required
@csrf_protect
def subscriptions(request):
    """

    :type request: object
    """
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        category = Category.objects.get(id=category_id)
        action = request.POST.get("action")

        if action == "subscriber":
            Subscriber.objects.create(user=request.user, category=category)
        elif action == "unsubscribe":
            Subscriber.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscriber.objects.filter(
                user=request.user,
                category=OuterRef("pk"),
            )
        )
    ).order_by("pk")
    return render(
        request,
        "subscriptions.html",
        {"categories": categories_with_subscriptions},
    )

# @login_required
# def be_author(request):
#     user = request.user
#     Author.objects.create(user = user)
#     authors_group = Group.objects.get(name='authors')
#     if not request.user.groups.filter(name='authors').exists():
#         authors_group.user_set.add(user)
#     return redirect('/')
#
# def subscribe_sport(request):
#     user = request.user
#     Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "sport"))
#     return redirect('/')
#
# def subscribe_politics(request):
#     user = request.user
#     Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "politics"))
#     return redirect('/')
#
# def subscribe_education(request):
#     user = request.user
#     Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "education"))
#     return redirect('/')
#
# def subscribe_culture(request):
#     user = request.user
#     Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "culture"))
#     return redirect('/')

# class FilteredPost(ListView):
#     model = Post
#     template_name = "search.html"
#     context_object_name = "posts"
#     ordering = ["-create_data"]
#     filterset_class = None
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
#         return self.filterset.qs.all()
#
#     def get_page_param(self):
#         page_param = self.request.GET.get("page", None)
#         return page_param
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["filterset"] = self.filterset
#         context["authors"] = Author.objects.all()
#         context["paginate"] = self.paginate_by
#         context["all_posts"] = Post.objects.all()
#         context["page_param"] = self.get_page_param()
#         context["limit_for_listing"] = (
#             Paginator(list(Post.objects.all()), 5).num_pages - 2
#         )
#         return context
