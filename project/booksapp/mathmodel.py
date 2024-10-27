import numpy as np
from booksapp import models
from django.shortcuts import get_object_or_404



def get_author_vector(book_id):
    authors_count = models.Genre.objects.count()
    vector = np.zeros(authors_count)
    book = get_object_or_404(book, id = book_id)
    vector[] = 1 
    return vector

def get_genres_vector(book_id):