import django.forms
from django_filters import FilterSet, CharFilter, DateFilter, ModelChoiceFilter, DateTimeFilter
from .models import Post, Author, Category
from django.forms import DateTimeInput

class PostSearch(FilterSet):
    dateCreation = DateFilter(
        lookup_expr='gte',
        widget=django.forms.DateInput(attrs={'type': 'date'})
    )
    title = CharFilter(
        field_name='title',
        lookup_expr = 'icontains',
        label = 'Название статьи'
    )

    author = ModelChoiceFilter(
        field_name='author',
        queryset = Author.objects.all(),
        lookup_expr=('exact'),
        label = 'Автор'
    )

    class Meta:
        model = Post
        fields = []
        # ('date', 'title', 'author')

class PostFilter(FilterSet):

    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='по названию',

    )
    postCategory = ModelChoiceFilter(
        field_name='postcategory__category_through',
        queryset=Category.objects.all(),
        label='по категории',
        empty_label='любая'
    )

    datePost = DateTimeFilter(
        field_name='date_post',
        lookup_expr='gt',
        label='позже указываемой даты',
        widget=DateTimeInput(format='%Y-%m-%d', attrs={'type': 'datetime-local'}),
    )