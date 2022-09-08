# Build Example:
#    docker build -t hello_world_java -f Build/HelloWorldJava/Task/Dockerfile ./
# Run Example:
#    docker run -e -ti hello_world_java java datalabs.tool.TaskRunner \
#        --arg HELLO_WORLD_JAVA__LOG_MESSAGE__2022-03-23T00:00:00

FROM openjdk:11
WORKDIR /HelloWorldJava
ENV CLASSPATH=/HelloWorldJava:/HelloWorldJava/lib
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Bundle.zip .
unzip Bundle.zip
