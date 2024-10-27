from django.contrib import admin
from booksapp import views
from django.urls import include, path
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('books/', views.get_books, name='books-list'),
    path('books/<int:id>/', views.get_book, name='book-detail'),
    path('books/<int:id>/rate_book/', views.rate_book, name='book-rate'),
    path('books/recommendations/',views.get_recommendations, name='recommendations'),

    path('users/registration/',views.registration,name='registration'),
    path('users/books/',views.get_user_books,name='get_user_books'),
    path('users/<int:id>/',views.put_user,name='put_user'),
    path('users/authentication/',views.authentication,name='authentication'),
    path('users/deauthorization/',views.deauthorization,name='deauthorization'),

    path('books/<int:id>/fetch/',views.fetch_book_text,name='fetch'),
    path('books/<int:id>/fetch_pages/',views.fetch_book_text_by_pages,name='fetch_pages'),
    path('authors/<int:id>/books/',views.get_books_by_author,name='get_books_by_author'),
    path('authors/<int:id>/', views.get_author, name='get_author_description'),
    path('authors/<int:id>/description/', views.get_author_description, name='get_author_description'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),

]