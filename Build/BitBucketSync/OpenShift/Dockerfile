FROM python:3.7
WORKDIR /BitBucketSync

COPY ./Build/BitBucketSync/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Python binary and source dependencies
RUN apt-get update -qq && \
 DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
 tini \
 build-essential \
 ca-certificates \
 cmake \
 curl \
 git \
 make \
 locales \
 locales-all \
 libcurl4-openssl-dev \
 libffi-dev \
 libsqlite3-dev \
 libzmq3-dev \
 pandoc \
 sqlite3 \
 texlive-fonts-recommended \
 texlive-latex-base \
 texlive-latex-extra \
 zlib1g-dev && \
 apt-get clean && \
 rm -rf /var/lib/apt/lists/*

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install nss_wrapper.
RUN curl -SL -o nss_wrapper.tar.gz https://ftp.samba.org/pub/cwrap/nss_wrapper-1.1.2.tar.gz && \
 mkdir nss_wrapper && \
 tar -xC nss_wrapper --strip-components=1 -f nss_wrapper.tar.gz && \
 rm nss_wrapper.tar.gz && \
 mkdir nss_wrapper/obj && \
 (cd nss_wrapper/obj && \
 cmake -DCMAKE_INSTALL_PREFIX=/usr/local -DLIB_SUFFIX=64 .. && \
 make && \
 make install) && \
 rm -rf nss_wrapper

COPY ./Source/Python/ .
COPY ./Test/Python/ .

COPY ./Build/BitBucketSync/server-ssl.conf .
RUN openssl req --batch -config server-ssl.conf -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

ENV HOME /BitBucketSync

COPY ./Build/BitBucketSync/OpenShift/entrypoint.sh ${HOME}/entrypoint.sh
RUN chmod +x ${HOME}/entrypoint.sh

# RUN adduser --disabled-password --uid 1001 --gid 0 --home ${HOME} --no-create-home --gecos "BitBucketSync" bitbucketsync

# RUN chown -Rf 1001 ${HOME}

# USER 1001

# RUN rm -rf ${HOME}/.ssh
# RUN mkdir ${HOME}/.ssh
# RUN chmod go-rwx ${HOME}/.ssh
# COPY ./Build/BitBucketSync/ssh_config.txt ${HOME}/.ssh/config
# RUN printenv BITBUCKET_SSH_KEY | sed 's/\\n/\n/g' > ${HOME}/.ssh/id_rsa
# RUN chmod go-rwx ${HOME}/.ssh/id_rsa

# ENTRYPOINT ["${HOME}/entrypoint.sh"]

# EXPOSE 8080