""" Release endpoint classes."""
import cgi
from dataclasses import dataclass
import logging
from typing import List

import urllib3

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from datalabs.access.orm import Database
from datalabs.access.vericre.api.audit import AuditLogger, AuditLogParameters, RequestType
from datalabs.access.vericre.api.authentication import PassportAuthenticatingEndpointMixin
from datalabs.access.vericre.api.header import PROFILE_HEADERS
from datalabs.parameter import add_schema
from datalabs.util.profile import run_time_logger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class AMAProfilePDFEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    identity: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    document_bucket: str
    client_id: str
    client_secret: str
    token_url: str
    profile_url: str
    pdf_url: str
    unknowns: dict = None


class AMAProfilePDFEndpointTask(PassportAuthenticatingEndpointMixin, APIEndpointTask):
    PARAMETER_CLASS = AMAProfilePDFEndpointParameters

    def __init__(self, parameters: dict, data: List[bytes] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()
        self._headers = PROFILE_HEADERS.copy()

    def run(self):
        LOGGER.debug("Parameters in AMAProfilePDFEndpointTask: %s", self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path["entity_id"]
        source_ip = self._parameters.identity["sourceIp"]

        self._authenticate_to_passport(self._parameters, self._headers)

        self._assert_profile_exists(entity_id)

        pdf, filename = self._get_profile_pdf(entity_id)

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=RequestType.AMA_PDF,
            authorization=self._parameters.authorization,
            document_bucket=self._parameters.document_bucket,
            document_key=f"downloaded_documents/AMA_Profile_PDF/{filename}",
            request_ip=source_ip,
        )

        AuditLogger.save_audit_log(database, pdf, audit_parameters)

        self._generate_response(pdf, filename)

    @run_time_logger
    def _assert_profile_exists(self, entity_id):
        response = self._request_ama_profile(entity_id)

        if response.status == 404:
            raise ResourceNotFound("An AMA eProfiles profile was not found for the provided entity ID.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

    @run_time_logger
    def _get_profile_pdf(self, entity_id):
        response = self._request_ama_profile_pdf(entity_id)

        if response.status == 404:
            raise ResourceNotFound("An AMA eProfiles profile was not found for the provided entity ID.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        filename = cgi.parse_header(response.headers["Content-Disposition"])[1]["filename"]

        return response.data, filename

    def _generate_response(self, pdf, filename):
        self._response_body = pdf

        self._headers = {"Content-Type": "application/pdf", "Content-Disposition": f"attachment; filename={filename}"}

    @run_time_logger
    def _request_ama_profile(self, entity_id):
        return self._http.request("GET", f"{self._parameters.profile_url}/{entity_id}", headers=self._headers)

    @run_time_logger
    def _request_ama_profile_pdf(self, entity_id):
        return self._http.request("GET", f"{self._parameters.pdf_url}/{entity_id}", headers=self._headers)
