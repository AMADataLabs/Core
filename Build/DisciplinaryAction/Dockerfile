# Build Example:
#    docker build -t disciplinary-action -f ./Build/DisciplinaryAction/Dockerfile ./

FROM python:3.7
WORKDIR /DisciplinaryAction

COPY ./Build/DisciplinaryAction/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/DisciplinaryAction ./Build/DisciplinaryAction
COPY ./Source ./Source
RUN ./Script/bundle-app -i --directory ./ DisciplinaryAction

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

# COPY ./Test/Python/ .

# EXPOSE 8080