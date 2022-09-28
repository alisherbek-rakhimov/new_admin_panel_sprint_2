from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import UUIDMixin, TimeStampedMixin


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=False)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=False, null=True)
    creation_date = models.DateField(_('creation_date'), db_index=True, null=True)
    rating = models.FloatField(_('rating'), blank=False, null=False,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])

    class Type(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv_show', _('tv_show')

    type = models.CharField(
        _('type'),
        max_length=7,
        choices=Type.choices,
        default=Type.MOVIE,
    )

    genres = models.ManyToManyField(Genre, through='GenreFilmwork', related_name="filmworks")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworkds')


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"

        constraints = [
            models.UniqueConstraint(fields=['film_work', 'genre'], name='unique_film_work_genre_idx')
        ]

    def __str__(self):
        return f'{self.film_work!s} belongs to {self.genre!s}'


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    filmworks = models.ManyToManyField(Filmwork, through='PersonFilmwork', related_name="persons")

    class Meta:
        db_table = "content\".\"person"

        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class RoleType(models.TextChoices):
        ACTOR = 'actor', _('actor')
        PRODUCER = 'producer', _('producer')
        DIRECTOR = 'director', _('director')

    role = models.TextField(_('role'), choices=RoleType.choices, null=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"

        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique_role_film_work_person_idx')
        ]

    def __str__(self):
        return f'{self.person!s} played at {self.film_work!s}'
