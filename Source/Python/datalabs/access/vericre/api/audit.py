""" audit logging """
import base64
from dataclasses import dataclass
from enum import Enum
import hashlib
import logging
import time

from botocore.exceptions import ClientError

from datalabs.access.api.task import InternalServerError
from datalabs.access.aws import AWSClient
from datalabs.model.vericre.api import APILedger
from datalabs.util.profile import run_time_logger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class RequestType(Enum):
    DOCUMENTS = "Documents"
    AMA_PDF = "ama_profile_pdf"
    CAQH_PDF = "caqh_profile_pdf"


class UserType(Enum):
    PHYSICIAN = "physician"


@dataclass
class AuditLogParameters:
    entity_id: str
    request_type: str
    authorization: dict
    document_bucket: str
    document_key: str
    request_ip: str
    document_version_id: str = ""


class AuditLogger:
    @classmethod
    @run_time_logger
    def save_audit_log(cls, database, document_data, audit_log_parameters):
        document_bucket = audit_log_parameters.document_bucket
        document_key = audit_log_parameters.document_key

        audit_log_parameters.document_version_id = cls._upload_document_to_s3(
            document_bucket, document_key, document_data
        )

        cls._add_audit_log_record_in_db(database, audit_log_parameters, UserType.PHYSICIAN.value)

    @classmethod
    @run_time_logger
    def _upload_document_to_s3(cls, document_bucket, document_key, data):
        version_id = ""

        try:
            md5_hash = base64.b64encode(hashlib.md5(data).digest())

            with AWSClient("s3") as aws_s3:
                put_object_result = aws_s3.put_object(
                    Bucket=document_bucket, Key=document_key, Body=data, ContentMD5=md5_hash.decode()
                )

                version_id = cls._process_put_object_result(put_object_result)
        except ClientError as error:
            LOGGER.exception(error.response)
            raise InternalServerError("An error occurred when saving a file to S3") from error

        return version_id

    @classmethod
    @run_time_logger
    def _add_audit_log_record_in_db(cls, database, audit_log_parameters, user_type):
        new_record = APILedger(
            created_at=int(time.time()),
            customer_id=audit_log_parameters.authorization["user_id"],
            customer_name=audit_log_parameters.authorization["user_name"],
            document_version_id=audit_log_parameters.document_version_id,
            entity_id=audit_log_parameters.entity_id,
            file_path=audit_log_parameters.document_key,
            request_date=str(int(time.time())),
            request_ip=audit_log_parameters.request_ip,
            request_type=audit_log_parameters.request_type.value,
            user_type=user_type,
        )

        database.add(new_record)
        database.commit()

    @classmethod
    def _process_put_object_result(cls, put_object_result):
        if put_object_result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise InternalServerError("An error occurred when saving a file to S3")

        return put_object_result["VersionId"]
