from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,UserManager
from django.utils.timezone import now

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'

    objects = UserManager()

class Author(models.Model):
    name = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authors'

class BookManager(models.Manager):
    def get_book_rating(self, book):
        return BookRating.objects.filter(book_id = book.id).aggregate(models.Avg("rating"))['rating__avg']
    
    def get_books_rating(self):
        return BookRating.objects.annotate(models.Avg("BookRating"))

class Genre(models.Model):
    genre_name = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genres'


class Book(models.Model):
    name = models.TextField(blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)
    author = models.ForeignKey(Author, models.DO_NOTHING, blank=True, null=True)
    genre = models.ForeignKey(Genre, models.DO_NOTHING, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)

    objects = BookManager()

    class Meta:
        managed = False
        db_table = 'books'

class BookRating(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.IntegerField(verbose_name="Рейтинг",null=True)


    class Meta:
        db_table = "rating"
        constraints = [
            models.UniqueConstraint(fields=['book_id', 'user_id'], name='unique_book_rating')
        ]