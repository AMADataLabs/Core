# Build Example:
#    docker build -t cpt -f ./Build/CPT/Dockerfile --build-arg --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -ti cpt -e DOTENV_PATH=get_descriptors.env python -c "import awslambda; print(awslambda.handler(None, None))"

FROM python:3.7

WORKDIR /CPT

COPY ./Build/CPT/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

ARG template_vars
ARG event=None
ARG context=None

ENV PYTHONPATH=/CPT:/CPT/site-packages
ENV AWS_SHARED_CREDENTIALS_FILE=/CPT/.aws/credentials
ENV AWS_DEFAULT_REGION=us-east-1
ENV EVENT=$event
ENV CONTEXT=$context

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/CPT ./Build/CPT
COPY ./Source ./Source

RUN echo $template_vars
COPY ./Build/CPT/*.env ./
RUN find ./ -name "*.env" -exec \
    ./Script/render-template \
    --template {} \
    --file {} \
    --vars pythonpath=/CPT,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ CPT

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

COPY ./Build/CPT/credentials ${AWS_SHARED_CREDENTIALS_FILE}

# ENTRYPOINT python -c "import awslambda; print(awslambda.handler($EVENT, $CONTEXT))"
