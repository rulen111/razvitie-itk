from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ["author__id"]

    @action(methods=["post"], detail=True)
    def buy(self, request, pk):
        book = self.get_object()
        count = book.count - 1
        serializer = BookSerializer(book, data={"count": count}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": f"Successfully bought '{book.title}'"})
        else:
            return Response(
                {"error": "Not enough items in stock"},
                status=status.HTTP_400_BAD_REQUEST
            )
