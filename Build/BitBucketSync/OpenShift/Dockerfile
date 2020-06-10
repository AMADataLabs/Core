FROM python:3.7
WORKDIR /BitBucketSync

COPY ./Build/BitBucketSync/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Source/Python/ .
COPY ./Test/Python/ .

COPY ./Build/BitBucketSync/server-ssl.conf .
RUN openssl req --batch -config server-ssl.conf -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

RUN rm -rf /root/.ssh
RUN mkdir /root/.ssh
RUN chmod go-rwx /root/.ssh
COPY ./Build/BitBucketSync/ssh_config.txt /root/.ssh/config
