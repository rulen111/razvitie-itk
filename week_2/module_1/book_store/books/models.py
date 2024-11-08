from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Author's first name")
    last_name = models.CharField(max_length=50, verbose_name="Author's last name")

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(max_length=250, verbose_name="Book's title")
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE, verbose_name="Book's Author")
    count = models.PositiveSmallIntegerField(default=1, verbose_name="Stock")

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return self.title
