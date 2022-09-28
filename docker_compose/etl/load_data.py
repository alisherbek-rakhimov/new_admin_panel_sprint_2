import contextlib
import os
import sqlite3
import sys
from dataclasses import astuple
from sqlite3 import DatabaseError
from typing import Any, Dict, Iterable, List, Tuple, Type, Generator
from loguru import logger
import logging

import psycopg2
from dateutil.parser import parse
from psycopg2 import sql
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values, execute_batch

from my_dataclasses import (Filmwork, Genre, GenreFilmwork, Person,
                            PersonFilmwork, TheBaseDataclass,
                            dataclass_factory)
from settings import dsn, db_path

sqlite3.register_converter("timestamp", lambda b: parse(b.decode('utf-8')))
# person table has incorrect naming for timestamp
sqlite3.register_converter("timestam", lambda b: parse(b.decode('utf-8')))


class PostgresLoader:
    def __init__(self, pg_conn: _connection):
        self.conn = pg_conn

    def load_one_table(self, d_class: Type[TheBaseDataclass]):
        curs = self.conn.cursor()

        columns = sql.SQL(', ').join(map(sql.Identifier, d_class.pg_attrs()))

        query = sql.SQL(
            '''SELECT {columns} from {table_name} order by id desc'''
        ).format(columns=columns, table_name=sql.Identifier(d_class.table_name()))

        curs.execute(query)

        return curs.fetchall()

    def close_conn(self):
        self.conn.close()


class SQLiteLoader:
    def __init__(self, sqlite_conn: sqlite3.Connection):
        self.conn = sqlite_conn
        self.batch_size = 100

    def extract_data_from(self, d_class, as_dataclass=True):
        if as_dataclass:
            self.conn.row_factory = dataclass_factory(d_class)

        curs = self.conn.cursor()

        query = f'''SELECT {d_class.sqlite_attrs()} from {d_class.table_name()} order by id desc;'''

        try:
            curs.execute(query)
        except sqlite3.Error as e:
            raise e
        while True:
            rows = curs.fetchmany(size=self.batch_size)
            if not rows:
                break
            yield from rows

    # def load_one_table(self, d_class, as_dataclass=True):
    #     if as_dataclass:
    #         self.conn.row_factory = dataclass_factory(d_class)
    #
    #     curs = self.conn.cursor()
    #
    #     query = f'''SELECT {d_class.sqlite_attrs()} from {d_class.table_name()} order by id desc;'''
    #
    #     curs.execute(query)
    #
    #     return curs.fetchall()

    # def load_movies(self, d_classes: List[Type[TheBaseDataclass]]) -> Dict[Type[TheBaseDataclass], list[Any]]:
    def load_movies(self, d_classes: List[Type[TheBaseDataclass]]) -> Generator:
        for d_class in d_classes:
            yield self.extract_data_from(d_class)

    def close_conn(self):
        self.conn.close()


class PostgresSaver:
    def __init__(self, pg_conn: _connection):
        self.conn = pg_conn

    def save_all_data(self, d_classes: List[Type[TheBaseDataclass]], data_generator):
        curs = self.conn.cursor()

        for d_class in d_classes:
            columns = sql.SQL(', ').join(map(sql.Identifier, d_class.pg_attrs()))

            tupled_generator: Generator[Tuple[Any]] = (astuple(row) for row in next(data_generator))

            insert_sql = sql.SQL(
                "INSERT INTO {table_name} ({columns}) VALUES %s ON CONFLICT (id) DO NOTHING;"
            ).format(columns=columns, table_name=sql.Identifier(d_class.table_name()))

            execute_values(curs, insert_sql, tupled_generator)
            pg_conn.commit()

    def truncate_tables(self, d_classes: Iterable[Type[TheBaseDataclass]]):
        curs = self.conn.cursor()
        table_names = (d_class.table_name() for d_class in d_classes)

        table_names = sql.SQL(', ').join(map(sql.Identifier, table_names))

        query = sql.SQL("TRUNCATE TABLE {table_names};").format(table_names=table_names)
        curs.execute(query.as_string(pg_conn))
        pg_conn.commit()


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    sqlite_loader = SQLiteLoader(sqlite_conn)
    postgres_saver = PostgresSaver(pg_conn)

    d_classes = [Filmwork, Person, Genre, GenreFilmwork, PersonFilmwork]

    postgres_saver.truncate_tables(d_classes)

    data_generator = sqlite_loader.load_movies(d_classes)

    postgres_saver.save_all_data(d_classes, data_generator)


if __name__ == '__main__':
    # logger.add(sys.stderr, format="{time} {level} {message}", level="ERROR")

    try:
        with contextlib.closing(
                sqlite3.connect(f'file:{db_path}?mode=ro', detect_types=sqlite3.PARSE_DECLTYPES, uri=True)
        ) as sqlite_conn, contextlib.closing(psycopg2.connect(**dsn, cursor_factory=DictCursor)) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
    except DatabaseError as e:
        logger.error(e)
    except psycopg2.OperationalError as e:
        logging.error(e)
