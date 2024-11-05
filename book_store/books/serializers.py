from rest_framework import serializers

from .models import Author, Book


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class BookSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Book
        # fields = ["id", "title", "author", "count"]
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, fields=["title"])

    class Meta:
        model = Author
        # fields = ["id", "first_name", "last_name", "books"]
        fields = "__all__"
