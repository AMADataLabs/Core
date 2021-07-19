<<<<<<< HEAD
# Build Example:
#    docker build -t pdr -f ./Build/ProfileDiscrepency/dev/Dockerfile --build-arg apigw_aws_access_key=ABCD123 --build-arg apigw_aws_secret_key=ABCD123' ./
# Run Example:
#    docker run -ti pdr"
FROM anapsix/alpine-java:8u121b13_jdk

ARG jira_username
ARG jira_password
ARG apigw_aws_access_key
ARG apigw_aws_secret_key
ARG talend_aws_access_key
ARG talend_aws_secret_key

ENV JIRA_USERNAME=${jira_username}
ENV JIRA_PASSWORD=${jira_password}
ENV APIGW_AWS_ACCESS_KEY=${apigw_aws_access_key}
ENV APIGW_AWS_SECRET_KEY=${apigw_aws_secret_key}
ENV TALEND_AWS_ACCESS_KEY=${talend_aws_access_key}
ENV TALEND_AWS_SECRET_KEY=${talend_aws_secret_key}

# Adding curl
WORKDIR /opt
RUN apk --no-cache add curl

# Installing aws-cli for downloading talend job from s3
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

WORKDIR /opt/talend

# importing SSL certificate for jira on prem
RUN mkdir -p /home/ssl-certs
COPY ./Build/ProfileDiscrepency/dev/jira_on_prem_ssl_cert.cer /home/ssl-certs
RUN $JAVA_HOME/jre/bin/keytool -import \
    -keystore $JAVA_HOME/jre/lib/security/cacerts \
    -file "/home/ssl-certs/jira_on_prem_ssl_cert.cer" \
    -storepass changeit \
    -trustcacerts \
    -noprompt \
    -alias cert_for_talend \
    -v

COPY ./Source ./Source
COPY ./Build/ProfileDiscrepency/dev/start.sh .
COPY ./Script ./Script

# creating apigw AWS profile
ENV AWS_PROFILE=apigw
RUN aws configure set aws_access_key_id "$APIGW_AWS_ACCESS_KEY"
RUN aws configure set aws_secret_access_key "$APIGW_AWS_SECRET_KEY"
RUN aws configure set region "us-east-1"
RUN aws configure list

RUN AWS_ENV_SCRIPT=$(Script/apigw_assume_role.sh | grep source | awk '{print $2}') && \
    source $AWS_ENV_SCRIPT && \
    aws s3 cp s3://ama-dev-datalake-lambda-us-east-1/PDR/ProfileDiscrepency_0.2.zip ProfileDiscrepency_0.2.zip
RUN unzip -q ProfileDiscrepency_0.2.zip
RUN rm -rf ProfileDiscrepency_0.2.zip
RUN chmod +x ProfileDiscrepency/ProfileDiscrepency_run.sh


CMD ["sh", "start.sh"]
=======
FROM anapsix/alpine-java:8u121b13_jdk

ARG talend_job
ARG talend_version
ARG jira_username
ARG jira_password
ARG apigw_aws_access_key
ARG apigw_aws_secret_key
ARG hadi_aws_access_key
ARG hadi_aws_secret_key

ENV TALEND_JOB=${talend_job}
ENV TALEND_VERSION=${talend_version}
ENV JIRA_USERNAME=${jira_username}
ENV JIRA_PASSWORD=${jira_password}
ENV APIGW_AWS_ACCESS_KEY=${apigw_aws_access_key}
ENV APIGW_AWS_SECRET_KEY=${apigw_aws_secret_key}
ENV TALEND_AWS_ACCESS_KEY=${talend_aws_access_key}
ENV TALEND_AWS_SECRET_KEY=${talend_aws_secret_key}

# Adding curl
WORKDIR /opt
RUN apk --no-cache add curl

# Installing aws-cli for downloading talend job from s3
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

WORKDIR /opt/talend

COPY ./Script ./Script
COPY ./Source ./Source

# creating apigw AWS profile
RUN aws configure set aws_access_key_id $apigw_aws_access_key --profile apigw
RUN aws configure set aws_secret_access_key $apigw_aws_secret_key --profile apigw
RUN aws configure set region "us-east-1" --profile apigw
RUN export AWS_PROFILE=apigw

# importing SSL certificate for jira on prem
RUN mkdir -p /home/ssl-certs
COPY ./Build/ProfileDiscrepency/dev/jira_on_prem_ssl_cert.cer /home/ssl-certs
RUN $JAVA_HOME/jre/bin/keytool -import \
    -keystore $JAVA_HOME/jre/lib/security/cacerts \
    -file "/home/ssl-certs/jira_on_prem_ssl_cert.cer" \
    -storepass changeit \
    -trustcacerts \
    -noprompt \
    -alias cert_for_talend \
    -v

# running startup script
COPY ./Build/ProfileDiscrepency/dev/start.sh .
CMD ["sh", "start.sh"]
>>>>>>> 04f6f83dda4ae7cebd5bb2bc37b4241c4e2a1a53
