# Build Example:
#    docker build -t scheduled-job-poc -f ./Build/ScheduledJobPoC/Dockerfile ./

FROM python:3.7
RUN apt update
RUN apt install -y vim

WORKDIR /ScheduledJobPoC

COPY ./Build/ScheduledJobPoC/requirements.txt .
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

ENV HOME /ScheduledJobPoC

RUN adduser --disabled-password --uid 1001 --gid 0 --home ${HOME} --no-create-home --gecos "ScheduledJobPoC" mockuser

COPY ./Build/BitBucketSync/OpenShift/entrypoint.sh entrypoint.sh
RUN chmod +x ${HOME}/entrypoint.sh

RUN chown -Rf 1001 ${HOME}
RUN chmod go+rwx ${HOME}

COPY ./Build/ScheduledJobPoC/put_foo.py .
RUN touch foo
RUN chmod go+r foo
