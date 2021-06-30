FROM anapsix/alpine-java:8u121b13_jdk

ARG talend_job
ARG talend_version
ARG jira_username
ARG jira_password
ARG aws_access_key
ARG aws_secret_key

ENV TALEND_JOB ${talend_job}
ENV TALEND_VERSION ${talend_version}
ENV JIRA_USERNAME ${jira_username}
ENV JIRA_PASSWORD ${jira_password}
ENV AWS_ACCESS_KEY ${aws_access_key}
ENV AWS_SECRET_KEY ${aws_secret_key}

WORKDIR /opt/talend

RUN mkdir output

COPY ${TALEND_JOB}_${talend_version}.zip .

RUN mkdir -p /home/ssl-certs

COPY ssl_cert_for_talend.cer /home/ssl-certs

RUN $JAVA_HOME/jre/bin/keytool -import \
    -keystore $JAVA_HOME/jre/lib/security/cacerts \
    -file "/home/ssl-certs/ssl_cert_for_talend.cer" \
    -storepass changeit \
    -trustcacerts \
    -noprompt \
    -alias cert_for_talend \
    -v

RUN unzip ${TALEND_JOB}_${TALEND_VERSION}.zip && \
    rm -rf ${TALEND_JOB}_${TALEND_VERSION}.zip && \
    chmod +x ${TALEND_JOB}/${TALEND_JOB}_run.sh

CMD ["/bin/sh", "-c", "${TALEND_JOB}/${TALEND_JOB}_run.sh"]