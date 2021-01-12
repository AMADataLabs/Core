# Build Example:
#    docker build -t OneView -f ./Build/OneView/Dockerfile.alembic ./

FROM python:3.7
WORKDIR /OneView
ENV PYTHONPATH=/OneView

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
alembic==1.4.2 \
pandas==1.0.1 \
psycopg2-binary==2.8.5 \
setuptools==41.0.0 \
sqlalchemy==1.3.13

COPY ./Build/OneView/alembic ./Build/OneView/alembic
COPY ./Build/OneView/alembic.ini ./Build/OneView/alembic.ini
COPY ./Source/Python/datalabs/access ./datalabs/access
COPY ./Source/Python/datalabs/model/masterfile/oneview.py ./datalabs/model/masterfile/oneview.py
COPY ./Source/Python/datalabs/__init__.py ./datalabs/a__init__.py
COPY ./Source/Python/datalabs/sqlalchemy.py ./datalabs/sqlalchemy.py
COPY ./Script/migrate-database ./migrate-database
COPY ./Script/run.py ./run.py
COPY ./Script/repo.py ./repo.py
