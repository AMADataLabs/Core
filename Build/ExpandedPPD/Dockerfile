# Build Example:
#    docker build -t expanded-ppd -f ./Build/ExpandedPPD/Dockerfile ./

FROM python:3.7
WORKDIR /ExpandedPPD
ENV PYTHONPATH=/app

COPY ./Build/ExpandedPPD/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/ExpandedPPD ./Build/ExpandedPPD
COPY ./Source ./Source
RUN ./Script/bundle-app -i --directory ./ ExpandedPPD

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

# COPY ./Test/Python/ .

# EXPOSE 8080