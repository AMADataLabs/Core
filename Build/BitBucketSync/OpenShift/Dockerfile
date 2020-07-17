FROM python:3.7
WORKDIR /BitBucketSync

COPY ./Build/BitBucketSync/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Source/Python/ .
COPY ./Test/Python/ .

COPY ./Build/BitBucketSync/server-ssl.conf .
RUN openssl req --batch -config server-ssl.conf -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

RUN rm -rf /BitBucketSync/.ssh
RUN mkdir /BitBucketSync/.ssh
RUN chmod go-rwx /BitBucketSync/.ssh
COPY ./Build/BitBucketSync/ssh_config.txt /BitBucketSync/.ssh/config
RUN printenv BITBUCKET_SSH_KEY > /BitBucketSync/.ssh/id_rsa
RUN RUN chmod go-rwx /BitBucketSync/.ssh/id_rsa

EXPOSE 8080