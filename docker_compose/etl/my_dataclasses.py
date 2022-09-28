import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Iterable, Type


class TheBaseDataclass(ABC):
    @staticmethod
    @abstractmethod
    def table_name():
        pass


class AttrsMixin:
    @classmethod
    def pg_attrs(cls: Type[dataclass]):
        attrs_ = []
        for field_ in fields(cls):
            if field_.name == 'created_at':
                attrs_.append('created')
            elif field_.name == 'updated_at':
                attrs_.append('modified')
            else:
                attrs_.append(field_.name)
        return attrs_

    @classmethod
    def sqlite_attrs(cls: Type[dataclass]) -> Iterable:
        return ', '.join([field_.name for field_ in fields(cls)])



@dataclass(slots=True, frozen=True, kw_only=True)
class Genre(TheBaseDataclass, AttrsMixin):
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def table_name():
        return 'genre'


@dataclass(slots=True, frozen=True, kw_only=True)
class Filmwork(TheBaseDataclass, AttrsMixin):
    id: uuid.UUID
    title: str
    description: str
    creation_date: datetime
    rating: float
    type: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def table_name():
        return 'film_work'


@dataclass(slots=True, kw_only=True, frozen=True)
class Person(TheBaseDataclass, AttrsMixin):
    id: uuid.UUID
    full_name: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def table_name():
        return 'person'


@dataclass(slots=True, kw_only=True, frozen=True)
class PersonFilmwork(TheBaseDataclass, AttrsMixin):
    film_work_id: uuid.uuid4
    person_id: uuid.uuid4
    id: uuid.UUID
    role: str
    created_at: datetime

    @staticmethod
    def table_name():
        return 'person_film_work'


@dataclass(slots=True, kw_only=True, frozen=True)
class GenreFilmwork(TheBaseDataclass, AttrsMixin):
    film_work_id: uuid.uuid4
    genre_id: uuid.uuid4
    id: uuid.UUID
    created_at: datetime

    @staticmethod
    def table_name():
        return 'genre_film_work'


def dataclass_factory(cls):
    def factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return cls(**d)

    return factory
