from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        verbose_name = 'Categorie'

    def __str__(self):
        return self.title


class Article(models.Model):
    selected_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    text_field = models.TextField(blank=True, null=True)
    article_image = models.ImageField(upload_to='media')
    created = models.DateTimeField(default=timezone.now)
    author = models.CharField(max_length=250, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=250)
    top = models.BooleanField(default=False)
    clicked_users = models.ManyToManyField(User, blank=True)
    clicks = models.PositiveIntegerField("Views", default=0)
    text = models.FileField(null=True, blank=True, upload_to='media')

    class Meta:
        verbose_name = 'Article'

    def __str__(self):
        return self.title


class Search(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    searched = models.DateField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Searche'

    def __str__(self):
        return self.title
