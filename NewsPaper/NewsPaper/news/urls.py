from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import (
    NewsList,
    NewsDetail,
    PostCreateAR,
    PostCreateNW,
    PostSearchView,
    PostEditNW,
    PostDeleteNW,
    PostEditAR,
    PostDeleteAR,
    AddPost,
    NewslLogin,
    RegisterView,
    LogoutView,
    be_author,
    subscribe_sport,
    subscribe_culture,
    subscribe_education,
    subscribe_politics
)

urlpatterns = [
    path("", NewsList.as_view(), name="post_list"),
    path("<int:pk>", NewsDetail.as_view(), name="post_detail"),
    path("search/", PostSearchView.as_view()),
    path("addpost", AddPost.as_view()),
    path("create/", PostCreateNW.as_view(), name="post_createNW"),
    path("create2/", PostCreateAR.as_view(), name="post_createAR"),
    path("<int:pk>/edit/", PostEditNW.as_view(), name="post_editNW"),
    path("<int:pk>/edit2/", PostEditAR.as_view(), name="post_editAR"),
    path("<int:pk>/delete/", PostDeleteNW.as_view(), name="post_deleteNW"),
    path("<int:pk>/delete2/", PostDeleteAR.as_view(), name="post_deleteAR"),
    path("login", NewslLogin.as_view()),
    path("signup", RegisterView.as_view(template_name="signup.html")),
    path("logout", LogoutView.as_view(template_name="news.html")),
    path("accounts/", include("allauth.urls")),
    path("upgrade/", be_author),
    path("subscribe/sport", subscribe_sport),
    path("subscribe/culture", subscribe_culture),
    path("subscribe/education", subscribe_education),
    path("subscribe/politics", subscribe_politics),
]
