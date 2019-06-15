from  postgres:latest
COPY backup.sql /docker-entrypoint-initdb.d/
EXPOSE 5432
