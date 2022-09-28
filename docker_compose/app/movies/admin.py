from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating', 'created', 'modified')

    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    # Фильтрация в списке
    list_filter = ('type',)
