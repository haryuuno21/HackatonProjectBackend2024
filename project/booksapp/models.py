from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,UserManager
from django.utils.timezone import now

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'

    objects = UserManager()


class BookManager(models.Manager):
    def get_book_rating(self, book):
        return BookRating.objects.filter(book_id = book.id).aggregate(models.Avg("rating"))['rating__avg']
    
    def get_books_rating(self):
        return BookRating.objects.annotate(models.Avg("BookRating"))

class Book(models.Model):
    book_name = models.CharField(max_length=100, verbose_name="Название книги")
    author_name = models.CharField(max_length=100, verbose_name="Автор",null=True)
    description = models.TextField(verbose_name="Описание книги",null=True)
    tags = models.TextField(verbose_name = "теги",null=True)
    rating = models.FloatField(default=0.0)
    photo_url = models.URLField(null=True)

    objects = BookManager()

    class Meta:
        db_table = "book"

class BookRating(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.IntegerField(verbose_name="Рейтинг",null=True)
    class Meta:
        db_table = "rating"
        constraints = [
            models.UniqueConstraint(fields=['book_id', 'user_id'], name='unique_book_rating')
        ]
