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
    path('books/best/',views.get_best_books,name='best-books-list'),

    path('users/registration/',views.registration,name='registration'),
    path('users/<int:id>/',views.put_user,name='put_user'),
    path('users/authentication/',views.authentication,name='authentication'),
    path('users/deauthorization/',views.deauthorization,name='deauthorization'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]