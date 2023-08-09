""" Release endpoint classes."""
from   dataclasses import dataclass
from   datetime import datetime
from   io import BytesIO
import logging

import requests
from   sqlalchemy.exc import OperationalError, MultipleResultsFound
from   zeep import Client

from   datalabs.access.api.task import APIEndpointTask, InternalServerError, InvalidRequest
from   datalabs.access.orm import Database
from   datalabs.access.vericre.api.wsdl import ENTERPRISE_SEARCH_WSDL
from   datalabs.model.vericre.api import User
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class PhysiciansSearchEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    ama_domain: str
    vericre_alb_domain: str
    payload: dict
    unknowns: dict=None

class PhysiciansSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = PhysiciansSearchEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in PhysiciansSearchEndpointTask: %s', self._parameters)
        physicians = []

        search_results = self._search_physicians(self._parameters.payload)

        with Database.from_parameters(self._parameters) as database:
            physicians = self._get_matching_physicians(database, search_results)

        self._proceed_caqh_sync(physicians)

        return self._generate_response(physicians)

    def _search_physicians(self, payload):
        url = f'https://{self._parameters.ama_domain}.ama-assn.org/enterprisesearch/EnterpriseSearchService'
        search_request = self._generate_search_request(payload)

        return self._submit_search_request(search_request, url)

    @classmethod
    def _get_matching_physicians(cls, database, request_response):
        physicians = []

        if request_response is not None:
            physicians = [cls._get_physician(physician, database) for physician in request_response]

        return [physician for physician in physicians if physician is not None]

    def _generate_response(self, physicians):
        physicians = [
            {
                "entity_id": physician["entity_id"],
                "first_name": physician["first_name"],
                "last_name": physician["last_name"],
                "date_of_birth": physician["date_of_birth"]
            }
            for physician in physicians
        ]

        self._response_body = self._generate_response_body(physicians)

        self._headers = self._generate_headers()

        self._status_code = self._generate_status_code(physicians)

    def _generate_search_request(self, payload):
        search_request = self._generate_number_search_request(payload)

        if not search_request:
            search_request = self._generate_name_search_request(payload)

        search_request["applicationId"] = "vericre"
        LOGGER.debug('Search Request: %s', search_request)

        return search_request

    @classmethod
    def _submit_search_request(cls, search_request, url):
        client = Client(wsdl=BytesIO(ENTERPRISE_SEARCH_WSDL.encode()))

        service = client.bind('EnterpriseSearchService')

        service._binding_options['address'] = url  # pylint: disable=protected-access

        if "stateCd" in search_request:
            response = service.SearchIndividualByState(searchIndividualByStateRequest=search_request)
        else:
            response = service.SearchEnterpriseEntity(searchEnterpriseEntityRequest=search_request)

        return response

    @classmethod
    def _generate_response_body(cls, physicians):
        return "No Content. Search request did not find any matches" if not physicians else physicians

    @classmethod
    def _generate_headers(cls):
        return {
            'Content-Type': 'application/json'
        }

    @classmethod
    def _generate_status_code(cls, physicians):
        return 204 if not physicians else 200

    @classmethod
    def _get_physician(cls, physician, database):
        entity_id = cls._get_entity_id(physician.entityId, database)
        physician_data = None

        if entity_id is not None:
            physician_data = dict(
                entity_id=physician.entityId,
                first_name=physician.legalFirstName,
                last_name=physician.legalLastName,
                date_of_birth=cls._get_date(physician.birthDate),
                npi_number=physician.npiNumber.NPI[0].npiNumber
            )

        return physician_data

    @classmethod
    def _generate_number_search_request(cls, payload):
        search_request = {
            "meNumber": payload.get("me_number"),
            "npiNumber": payload.get("npi_number"),
            "ecfmgNumber": payload.get("ecfmg_number")
        }

        return {key:value for key, value in search_request.items() if value}

    def _generate_name_search_request(self, payload):
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        date_of_birth = payload.get("date_of_birth")
        state_of_practice = payload.get("state_of_practice")
        search_request = {}

        self._validate_payload(payload)

        search_request["fullName"] = f"{first_name} {last_name}"
        search_request["birthDate"] = date_of_birth

        if state_of_practice:
            search_request["stateCd"] = state_of_practice

        return search_request

    @classmethod
    def _validate_payload(cls, payload):
        if "first_name" not in payload or "last_name" not in payload or "date_of_birth" not in payload:
            raise InvalidRequest(
                "Invalid input parameters. Please provide either a combination of First Name, Last Name, " \
                "and Date of Birth, or any of NPI number, ME number, or ECFMG number."
            )

        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        date_of_birth = payload.get("date_of_birth")

        if not first_name:
            raise InvalidRequest("Invalid input parameters. first_name cannot be empty.")

        if not last_name:
            raise InvalidRequest("Invalid input parameters. last_name cannot be empty.")

        if not date_of_birth:
            raise InvalidRequest("Invalid input parameters. date_of_birth cannot be empty.")

    @classmethod
    def _get_entity_id(cls,entity_id, database):
        response = None

        try:
            query = database.query(User.ama_entity_id).filter(User.ama_entity_id == entity_id)
            query = cls._filter_by_active_user(query)
            response = query.one_or_none()
        except OperationalError as error:
            raise InternalServerError("VeriCre connection error. Please try again later.") from error
        except MultipleResultsFound:
            LOGGER.error("Multiple results found for entity id : %s", entity_id)
            response = None

        return response

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')

    @classmethod
    def _get_date(cls, date_string):
        formatted_date = None

        try:
            date_object = datetime.strptime(date_string, "%Y%m%d")
            formatted_date = date_object.strftime("%Y-%m-%d")
        except (TypeError, ValueError) as error:
            LOGGER.error("Exception in formatting the date : %s",error)

        return formatted_date

    def _proceed_caqh_sync(self, physicians):

        physicians_payload = [
            {"entityId": physician["entity_id"], "npiNumber": physician["npi_number"]}
            for physician in physicians
        ]

        try:
            requests.post(
                f'https://{self._parameters.vericre_alb_domain}/users/physicians/search/onCAQHSync',
                verify=False,
                timeout=(None, 0.1),
                json=physicians_payload
            )

            LOGGER.info('CAQH sync request finished for %s physician(s)', len(physicians))
        except requests.exceptions.ReadTimeout:
            LOGGER.info('CAQH sync request sent for %s physician(s)', len(physicians))
        except requests.exceptions.RequestException as exception:
            LOGGER.error('CAQH sync request failed: %s', exception)
