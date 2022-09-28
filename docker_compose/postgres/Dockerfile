FROM postgres:13

ENV POSTGRES_PASSWORD 123qwe
ENV POSTGRES_USER app
ENV POSTGRES_DB movies_database

COPY ./schema_creation.sh /docker-entrypoint-initdb.d/schema_creation.sh

EXPOSE 5432