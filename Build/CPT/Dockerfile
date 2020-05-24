FROM python:3.7 AS Base
WORKDIR /app

RUN apt update
RUN apt install -y python3.7-venv


FROM Base as PythonDependencies
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /app/requirements.txt


FROM PythonDependencies as App
WORKDIR /app

COPY app/ .
