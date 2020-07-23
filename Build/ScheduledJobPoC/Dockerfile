# Build Example:
#    docker build -t scheduled-job-poc -f ./Build/ScheduledJobPoC/Dockerfile ./

FROM python:3.7
RUN apt update
RUN apt install -y vim

WORKDIR /ScheduledJobPoC

COPY ./Build/ScheduledJobPoC/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Build/ScheduledJobPoC/put_foo.py .
RUN touch foo
RUN chmod go+r foo
