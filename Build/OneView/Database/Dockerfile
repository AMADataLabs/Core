# Build Example:
#    docker build -t oneview-db -f ./Build/OneView/Database/Dockerfile ./
# Run Example:
#    docker run -ti oneview-db ./migrate-database upgrade -H <DB host>  -n <DB name> -u <DB user> -p <DB password> OneView

FROM python:3.9.5
WORKDIR /OneView
ENV PYTHONPATH=/OneView

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
alembic==1.4.2 \
pandas==1.0.1 \
psycopg2-binary==2.8.5 \
setuptools==41.0.0 \
sqlalchemy==1.3.13

COPY ./Script/migrate-database ./migrate-database
COPY ./Script/run.py ./run.py
COPY ./Script/repo.py ./repo.py
COPY ./Source/Python/datalabs/access ./datalabs/access
COPY ./Source/Python/datalabs/__init__.py ./datalabs/__init__.py
COPY ./Source/Python/datalabs/sqlalchemy.py ./datalabs/sqlalchemy.py

COPY ./Source/Python/datalabs/model/masterfile/oneview.py ./datalabs/model/masterfile/oneview.py

# NOTE: migrate-database expects to find Build/ in ../, so /Build is correct
COPY ./Build/OneView/alembic /Build/OneView/alembic
COPY ./Build/OneView/alembic.ini /Build/OneView/alembic.ini
