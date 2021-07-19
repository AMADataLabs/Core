echo "getting apigw aws account keys" && \
Script/apigw_assume_role.sh && \

echo "setting apigw aws account keys" && \
source $(ls -a .s3token*) && \

echo "pulling talend binary job" && \
aws s3 cp s3://ama-dev-datalake-lambda-us-east-1/PDR/ProfileDiscrepency_0.2.zip ProfileDiscrepency_0.2.zip && \

echo "unzipping zip file" && \
unzip -q ${TALEND_JOB}_${TALEND_VERSION}.zip && \
rm -rf ${TALEND_JOB}_${TALEND_VERSION}.zip && \
chmod +x ${TALEND_JOB}/${TALEND_JOB}_run.sh && \

echo "running talend job" && \
sh ${TALEND_JOB}/${TALEND_JOB}_run.sh 