FROM ubuntu:18.04 as Python

RUN apt update
RUN apt install -y gnupg

RUN echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu bionic main" > /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-bionic.list
RUN apt-key adv --keyserver hkp://keys.gnupg.net:80 --recv-keys BA6932366A755776

RUN apt update
RUN apt install -y python3.7 python3.7-dev python3-pip


FROM Python as Requirements

RUN pip3 install --upgrade pip
RUN pip3 install PyYAML==5.3.1


FROM Requirements as Tools

RUN apt install -y xvfb curl openjdk-8-jdk jq git

