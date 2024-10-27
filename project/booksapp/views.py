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
    return Response({'status': 'Success'})

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

