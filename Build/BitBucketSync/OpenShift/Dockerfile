FROM python:3.7
WORKDIR /BitBucketSync

COPY ./Build/BitBucketSync/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Source/Python/ .
COPY ./Test/Python/ .

COPY ./Build/BitBucketSync/server-ssl.conf .
RUN openssl req --batch -config server-ssl.conf -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

RUN rm -rf ${HOME}/.ssh
RUN mkdir ${HOME}/.ssh
RUN chmod go-rwx ${HOME}/.ssh
COPY ./Build/BitBucketSync/ssh_config.txt ${HOME}/.ssh/config
RUN printenv BITBUCKET_SSH_KEY | sed 's/\\n/\n/g' > ${HOME}/.ssh/id_rsa
RUN chmod go-rwx ${HOME}/.ssh/id_rsa
RUN printenv BITBUCKET_SSH_KEY | sed 's/\\n/\n/g' > /BitBucketSync/id_rsa

EXPOSE 8080