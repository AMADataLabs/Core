""" Release endpoint classes."""
import cgi
from dataclasses import dataclass
import json
import logging
import urllib.parse
from typing import List, Optional

import urllib3

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from datalabs.access.orm import Database
from datalabs.access.vericre.api.audit import AuditLogger, AuditLogParameters, RequestType
from datalabs.access.vericre.api.datetime import get_current_datetime
from datalabs.parameter import add_schema
from datalabs.util.profile import run_time_logger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class CAQHProfilePDFEndpointParameters:
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
    username: str
    password: str
    org_id: str
    application_type: str
    provider_docs_url: str
    status_check_url: str
    unknowns: Optional[dict] = None


class CAQHProfilePDFEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = CAQHProfilePDFEndpointParameters

    def __init__(self, parameters: dict, data: Optional[List[bytes]] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()

    def run(self):
        self._set_parameter_defaults()
        LOGGER.debug("Parameters: %s", self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        entity_id = self._parameters.path["entity_id"]
        source_ip = self._parameters.identity["sourceIp"]

        sql = self._query_for_provider_id(entity_id)

        query = self._execute_sql(database, sql)

        query_result = self._convert_query_result_to_list(query)

        self._verify_query_result(query_result)

        provider = query_result[0]["caqh_profile_id"]

        pdf, filename = self._fetch_caqh_pdf(provider)

        current_date_time = get_current_datetime()

        audit_parameters = AuditLogParameters(
            entity_id=entity_id,
            request_type=RequestType.CAQH_PDF,
            authorization=self._parameters.authorization,
            document_bucket=self._parameters.document_bucket,
            document_key=(
                f'downloaded_documents/CAQH_Profile_PDF/{filename.replace(".pdf", f"_{current_date_time}.pdf")}'
            ),
            request_ip=source_ip,
        )

        AuditLogger.save_audit_log(database, pdf, audit_parameters)

        self._generate_response(pdf, filename, current_date_time)

    @classmethod
    def _query_for_provider_id(cls, entity_id):
        sql = f"""
            select
                p.caqh_profile_id
            from physician p
            join "user" u on u.id = p."user"
                and u.ama_entity_id = '{entity_id}'
                and u.is_deleted = 'False'
                and u.status = 'ACTIVE'
        """

        return sql

    @classmethod
    @run_time_logger
    def _execute_sql(cls, database, sql):
        query = database.execute(sql)
        return query

    @classmethod
    @run_time_logger
    def _convert_query_result_to_list(cls, query):
        query_result = [dict(row) for row in query.fetchall()]
        return query_result

    @classmethod
    def _verify_query_result(cls, query_result):
        if len(query_result) == 0:
            raise ResourceNotFound("A provider ID was not found in VeriCre for the given entity ID.")

        if len(query_result) > 1:
            raise InternalServerError("Multiple records were found in VeriCre for the given entity ID.")

        if isinstance(query_result[0]["caqh_profile_id"], type(None)) or query_result[0]["caqh_profile_id"] == "":
            raise ResourceNotFound("A provider ID was not found in VeriCre for the given entity ID.")

    def _fetch_caqh_pdf(self, provider):
        provider_id = self._get_caqh_provider_id(provider)

        parameters = urllib.parse.urlencode(
            {
                "applicationType": self._parameters.application_type,
                "docURL": "replica",
                "organizationId": self._parameters.org_id,
                "caqhProviderId": provider_id,
            }
        )

        response = self._request_caqh_pdf(parameters)

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.data}, status: {response.status}")

        filename = cgi.parse_header(response.headers["Content-Disposition"])[1]["filename"]

        return response.data, filename

    def _set_parameter_defaults(self):
        self._parameters.authorization["auth_headers"] = urllib3.make_headers(
            basic_auth=f"{self._parameters.username}:{self._parameters.password}"
        )

    def _generate_response(self, pdf, filename, current_date_time):
        filename = filename.replace(".pdf", f"_{current_date_time}.pdf")

        self._response_body = pdf

        self._headers = {"Content-Type": "application/pdf", "Content-Disposition": f"attachment; filename={filename}"}

    def _request_caqh_pdf(self, parameters):
        return self._http.request(
            "GET",
            f"{self._parameters.provider_docs_url}?{parameters}",
            headers=self._parameters.authorization["auth_headers"],
        )

    def _get_caqh_provider_id(self, provider):
        provider_data = provider.split("-")
        provider_prefix = provider_data[0]
        provider_id = provider_data[1]

        caqh_provider_id = None

        if provider_prefix == "caqh":
            caqh_provider_id = provider_id
        elif provider_prefix == "npi":
            caqh_provider_id = self._get_caqh_provider_id_from_npi(provider_id)

        return caqh_provider_id

    def _get_caqh_provider_id_from_npi(self, npi):
        parameters = urllib.parse.urlencode(
            {
                "Product": "PV",
                "Organization_Id": self._parameters.org_id,
                "NPI_Provider_Id": npi,
            }
        )

        response = self._request_caqh_provider_id_from_npi(parameters)

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.data}, status: {response.status}")

        provider_data = json.loads(response.data)

        if provider_data["provider_found_flag"] != "Y":
            raise ResourceNotFound("A provider ID was not found in CAQH ProView for the given NPI.")

        return provider_data["caqh_provider_id"]

    def _request_caqh_provider_id_from_npi(self, parameters):
        return self._http.request(
            "GET",
            f"{self._parameters.status_check_url}?{parameters}",
            headers=self._parameters.authorization["auth_headers"],
        )
