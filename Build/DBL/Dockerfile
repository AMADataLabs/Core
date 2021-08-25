# Build Example:
#    docker build -t dbl -f ./Build/DBL/Dockerfile --build-arg template_vars='username=bob,password=foo' ./
# Run Example:
#    docker run -e DOTENV_PATH=ppd.env -ti dbl python task.py

FROM python:3.7
WORKDIR /DBL
ENV PYTHONPATH=/DBL:/DBL/site-packages
ENV CLASSPATH=/DBL
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/DBL/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/DBL ./Build/DBL
COPY ./Source ./Source

ARG template_vars
RUN echo $template_vars
COPY ./Build/DBL/*.env.jinja ./
RUN find ./ -name "*.env.jinja" | sed 's/.jinja//' | xargs -t -I {}\
    ./Script/render-template \
    --template {} \
    --file {} \
    --vars pythonpath=/DBL,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ DBL

RUN rm -rf ./Build/Master
RUN rm -rf ./Source
