# Build from Build/Master

FROM ubuntu:18.04 as DevEnv
WORKDIR /Build

ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./Script ./Script
COPY ./Source/Bash ./Source/Bash
RUN ./Script/setup-development-environment


FROM DevEnv as VirtualEnv
WORKDIR /Build

COPY ./Build ./Build
RUN ./Script/setup-virtual-environment Master


FROM VirtualEnv as Tools

RUN apt install -y xvfb curl openjdk-8-jdk jq git

