from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from booksapp.serializers import *
from booksapp.models import *
from booksapp.mathmodel import *
from rest_framework.decorators import api_view,permission_classes
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from booksapp.permissions import *
from hahaton import settings
import redis
import uuid
import requests
import wikipediaapi

session_storage = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def getUser(request):
    try:
        ssid = request.COOKIES["session_id"]
        username = session_storage.get(ssid)
        user = CustomUser.objects.get(username = username.decode("utf-8"))
    except:
        return None
    return user

def get_best_books(request,format=None):
    start_id = int(request.GET.get("start_id"))
    books = Book.objects.all().order_by('-rating')[start_id:start_id+10]
    serializer = PartBookSerializer(books,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['Get'])
def get_books(request, format=None):
    book_name = request.GET.get("book_name")
    best_flag = request.GET.get("best")
    if best_flag:
        return get_best_books(request)
    start_id = int(request.GET.get("start_id"))
    if not book_name:
        books = Book.objects.all()[start_id:start_id+10]
    else:
        books = Book.objects.filter(name__icontains = book_name)[start_id:start_id+10]
    serializer = PartBookSerializer(books,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['Get'])
def get_book(request,id,format=None):
    book = get_object_or_404(Book,id=id)
    serializer = FullBookSerializer(book)
    data = serializer.data
    
    return Response(data,status=status.HTTP_200_OK)

@api_view(["Post"])
@permission_classes([IsAuthenticated])
def rate_book(request,id,format=None):
    book = get_object_or_404(Book,id=id)
    user = getUser(request)
    try:
        rate = BookRating.objects.get(book_id = book, user_id = user)
    except BookRating.DoesNotExist:
        rate = BookRating.objects.create(book_id = book, user_id = user)
    rate.rating = request.data['rating']
    rate.save()
    newRating = Book.objects.get_book_rating(book)
    book.rating = round(newRating,2)
    book.save()
    data = PartBookSerializer(book).data
    return Response(data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['Post'])
@permission_classes([AllowAny])
def registration(request, format=None):
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Put'])
@permission_classes([IsAuthenticated])
def put_user(request, id, format=None):
    user = get_object_or_404(CustomUser, id=id)
    serializer = UserSerializer(user, data=request.data, partial=True)
    user_client = getUser(request)
    if user != user_client and not user_client.is_staff:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Post'])
@permission_classes([AllowAny])
def authentication(request, format=None):
    username = request.data.get('username')
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        random_key = uuid.uuid4()
        session_storage.set(str(random_key), username)
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie("session_id", random_key)
        return response
    else:
        return Response("authentication failed",status=status.HTTP_400_BAD_REQUEST)

@api_view(['Post'])
@permission_classes([IsAuthenticated])
def deauthorization(request,format=None):
    ssid = request.COOKIES["session_id"]
    session_storage.delete(ssid)
    response = Response({'status': 'Success'})
    response.delete_cookie("session_id")
    return response

@api_view(['Get'])
def fetch_book_text(request, id):
    book_url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        return Response(response.text, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        print(f"Не удалось загрузить текст книги: {e}")
        return Response({"error": "Не удалось загрузить текст книги."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get'])
def get_books_by_author(request, id):
    books = Book.objects.filter(author_id = id)
    serializer = PartBookSerializer(books,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['Get'])
@permission_classes([IsAuthenticated])
def get_recommendations(request, format=None):
    user = getUser(request)
    author_vector, genre_vector = get_user_vectors(user)
    books_with_weights = []

    author_ids = [i for i, x in enumerate(author_vector) if x != 0]
    genre_ids = [i for i, x in enumerate(genre_vector) if x != 0]

    books = Book.objects.filter(
        models.Q(author_id__in=author_ids) | models.Q(genre_id__in=genre_ids)
    ).distinct() 

    for book in books:
        weight = get_book_weight(author_vector, genre_vector, book)
        books_with_weights.append((book, weight))

    books_with_weights.sort(key=lambda x: x[1], reverse=True)
    top_books = [book for book, _ in books_with_weights[:20]]

    serializer = PartBookSerializer(top_books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['Get'])
def get_author_description(request, id):
    author = Author.objects.filter(id=id).first()

    if author is None:
        return Response({"error": "Автор не найден."}, status=status.HTTP_404_NOT_FOUND)

    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent="booksapp/1.0 (https://mybookapp.com; myemail@example.com)"
    )

    page = wiki_wiki.page(author.name)

    if page.exists():
        return Response({"description": page.text}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Статья о данном авторе не найдена."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['Get'])
@permission_classes([IsAuthenticated])
def get_user_books(request):
    user = getUser(request)
    user_rates = BookRating.objects.filter(user_id = user)
    serializer = BookRatingSerializer(user_rates,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)