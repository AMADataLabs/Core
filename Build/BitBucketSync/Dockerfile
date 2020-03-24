FROM python:3.7 AS Base
WORKDIR /BitBucketSync

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pipenv


FROM Base as PythonDependencies
WORKDIR /BitBucketSync

COPY ./Environment/BitBucketSync/Pipfile .

RUN pipenv install


FROM PythonDependencies as Code
WORKDIR /BitBucketSync

COPY ./Source/Python/ .
COPY ./Test/Python/ .
COPY ./Environment/BitBucketSync/.env .
COPY ./Environment/Master/settings.py .

COPY ./Build/BitBucketSync/server-ssl.conf .
RUN openssl req --batch -config server-ssl.conf -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

RUN mkdir /root/.ssh
RUN chmod go-rwx /root/.ssh
RUN echo -e "Host bitbucket.ama-assn.org\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config
RUN echo -e "Host bitbucket.org\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config
