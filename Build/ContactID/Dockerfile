# Build Example:
#    docker build -t one-view -f ./Build/OneView/Dockerfile --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -ti one-view -e DOTENV_PATH=ppd.env python -c "import awslambda; print(awslambda.handler(None, None))"

FROM python:3.7
WORKDIR /ContactID
ENV PYTHONPATH=/ContactID:/ContactID/site-packages
ENV CLASSPATH=/ContactID
#ENV AWS_SHARED_CREDENTIALS_FILE=/ContactID/.aws/credentials
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/ContactID/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt


COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/ContactID ./Build/ContactID
COPY ./Source ./Source

ARG template_vars
RUN echo $template_vars
COPY ./Build/ContactID/*.env ./

RUN find ./ -name "*.env" -exec \
   ./Script/render-template \
    --template {} \
    --file {} \
   --vars pythonpath=/ContactID,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ ContactID

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source



