from django.contrib import admin

from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name"]
    readonly_fields = ["id"]
    ordering = ["first_name", "last_name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "count"]
    readonly_fields = ["id"]
    ordering = ["author", "title"]
