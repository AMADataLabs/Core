FROM ubuntu:18.04

RUN apt update

RUN apt install -y gnupg wget xvfb curl openjdk-8-jdk


RUN echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu bionic main" > /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-bionic.list
RUN apt-key adv --keyserver hkp://keys.gnupg.net:80 --recv-keys BA6932366A755776

RUN apt update

RUN apt install -y python3.7 python3.7-dev
