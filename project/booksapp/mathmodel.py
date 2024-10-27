import numpy as np
from booksapp.models import *
from django.db.models import Max


author_k = 1.5

def get_user_vectors(user):
    readBooks = BookRating.objects.filter(user_id = user)
    authors_count = Author.objects.aggregate(Max('id'))['id__max']
    genres_count = Genre.objects.aggregate(Max('id'))['id__max']
    author_vector = np.zeros(authors_count+1)
    genre_vector = np.zeros(genres_count+1)
    for readBook in readBooks:
        rating = readBook.rating
        book = Book.objects.get(id = readBook.book_id.id)
        author_vector[book.author.id] += rating - 2
        genre_vector[book.genre.id] += rating - 2

    return (author_vector,genre_vector)

def get_book_weight(author_vector, genre_vector, book):
    norm_author = np.linalg.norm(author_vector)
    norm_genre = np.linalg.norm(genre_vector)

    if norm_author == 0:
        cos_author = 0
    else:
        cos_author = author_vector[book.author.id]/norm_author
    if norm_genre == 0:
        cos_genre = 0
    else:
        cos_genre = genre_vector[book.genre.id]/norm_genre

    weight = (cos_author*author_k+cos_genre)/author_k

    return weight