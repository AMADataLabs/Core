# Build Example:
#    docker build -t scheduler -f ./Build/Scheduler/Dockerfile --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -e DOTENV_PATH=scheduler.env -ti scheduler python -c "import awslambda; print(awslambda.handler(None, None))"

FROM python:3.7
WORKDIR /Scheduler
ENV PYTHONPATH=/Scheduler:/Scheduler/site-packages
ENV CLASSPATH=/Scheduler
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/Scheduler/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/Scheduler ./Build/Scheduler
COPY ./Source ./Source

ARG template_vars
RUN echo $template_vars
COPY ./Build/Scheduler/*.env ./
RUN find ./ -name "*.env" -exec \
    ./Script/render-template \
    --template {} \
    --file {} \
    --vars pythonpath=/Scheduler,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ Scheduler

RUN rm -rf ./Build/Master
RUN rm -rf ./Source
