""" Release endpoint classes."""
from   dataclasses import dataclass
from   datetime import datetime
import logging

from   zeep import Client

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest
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
    domain: str
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

        return self._generate_response(physicians)

    def _search_physicians(self):
        url = f'https://{self._parameters.domain}.ama-assn.org/enterprisesearch/EnterpriseSearchService'
        search_request = self._generate_search_request()

        return self._submit_search_request(search_request, url)

    @classmethod
    def _get_matching_physicians(cls, database, request_response):
        physicians = [cls._get_physician(physician, database) for physician in request_response]

        return [physician for physician in physicians if physician is not None]

    def _generate_response(self, physicians):
        self._response_body = self._generate_response_body(physicians)

        self._headers = self._generate_headers()

    def _generate_search_request(self):
        search_request = self._generate_request_for_single_param()

        if not search_request:
            search_request = self._generate_request_for_composite_param(search_request)

        if not search_request:
            raise InvalidRequest(
                "Invalid input parameters. Please provide either a combination of First Name, Last Name, " \
                "and Date of Birth, or any of NPI number, ME number, or ECFMG number."
            )

        search_request["applicationId"] = "vericre"
        LOGGER.debug('Request: %s', search_request)

        return search_request

    @classmethod
    def _submit_search_request(cls, search_request, url):
        client = Client(wsdl=ENTERPRISE_SEARCH_WSDL)

        service = client.bind('EnterpriseSearchService')

        service._binding_options['address'] = url  # pylint: disable=protected-access

        if search_request.get("stateCd"):
            response = service.SearchIndividualByState(searchIndividualByStateRequest=search_request)
        else:
            response = service.SearchEnterpriseEntity(searchEnterpriseEntityRequest=search_request)

        return response

    @classmethod
    def _generate_response_body(cls, physicians):
        return physicians

    @classmethod
    def _generate_headers(cls):
        return {
            'Content-Type': 'application/json'
        }

    @classmethod
    def _get_physician(cls, physician, database):
        entity_id = cls._get_entity_id(physician.entityId, database)
        physician = None

        if entity_id is not None:
            physician = dict(
                entity_id=physician.entityId,
                first_name=physician.legalFirstName,
                last_name=physician.legalLastName,
                date_of_birth=cls._get_date(physician.birthDate)
            )

        return physician

    @classmethod
    def _generate_request_for_single_param(cls, payload):
        search_request = {}
        continue_flag = True

        single_param_to_key = {
            "meNumber": payload.get("me_number"),
            "npiNumber": payload.get("npi_number"),
            "ecfmgNumber": payload.get("ecfmg_number")
        }

        while continue_flag:
            for key, value in single_param_to_key.items():
                continue_flag = False

                if value:
                    search_request[key] = value
                    continue_flag = False
                    break

        return search_request

    @classmethod
    def _generate_request_for_composite_param(cls, payload, search_request):
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        date_of_birth = payload.get("date_of_birth")
        state_of_practice = payload.get("state_of_practice")

        if first_name and last_name:
            search_request["fullName"] = f"{first_name}  {last_name}"
            search_request["birthDate"] = date_of_birth

        if state_of_practice:
            search_request["stateCd"] = state_of_practice

        return search_request

    @classmethod
    def _get_entity_id(cls,entity_id, database):
        return database.query(User.ama_entity_id).filter(User.ama_entity_id == entity_id).one_or_none()

    @classmethod
    def _get_date(cls, date_string):
        date_object = datetime.strptime(date_string, "%Y%m%d")
        formatted_date = date_object.strftime("%Y-%m-%d")

        return formatted_date
