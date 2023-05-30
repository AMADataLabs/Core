""" Release endpoint classes."""
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.exc import OperationalError, MultipleResultsFound
from zeep import Client

import logging

from datalabs.access.api.task import APIEndpointTask, InternalServerError, InvalidRequest
from datalabs.access.orm import Database
from datalabs.model.vericre.api import User
from datalabs.parameter import add_schema

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

    def _search_physicians(self, payload):
        url = f'https://{self._parameters.domain}.ama-assn.org/enterprisesearch/EnterpriseSearchService'
        search_request = self._generate_search_request(payload)

        return self._submit_search_request(search_request, url)

    @classmethod
    def _get_matching_physicians(cls, database, request_response):
        physicians = [cls._get_physician(physician, database) for physician in request_response]

        return [physician for physician in physicians if physician is not None]

    def _generate_response(self, physicians):
        self._response_body = self._generate_response_body(physicians)

        self._headers = self._generate_headers()

    def _generate_search_request(self, payload):
        search_request = self._generate_number_search_request(payload)

    def _run(self, database):
        search_request = self._construct_search_request()

        service = self._construct_enterprise_service()

        response = self._call_enterprise_service(search_request, service)

        physicians = self._get_physicians(database, response)

        self._generate_response(physicians)

    def _construct_search_request(self):
        search_request = {}
        search_request = self._construct_request_for_single_param(search_request)

        if not search_request:
            search_request = self._construct_request_for_composite_param(search_request)

        if not search_request:
            raise InvalidRequest(
                "Invalid input parameters. Please provide either a combination of First Name, "
                "Last Name, and Date of Birth, or any of NPI number, ME number, or ECFMG number."
            )

        search_request["applicationId"] = "vericre"
        LOGGER.info("Search request : %s",search_request)

        return search_request

    @classmethod
    def _generate_number_search_request(cls, payload):
        search_request = {
            "meNumber": payload.get("me_number"),
            "npiNumber": payload.get("npi_number"),
            "ecfmgNumber": payload.get("ecfmg_number")
        }

        while continue_flag:
            for key, value in single_param_to_key.items():
                if self._assert_not_none(value):
                    search_request[key] = value
                    continue_flag = False
                    break
            else:
                continue_flag = False

        return search_request

    def _construct_request_for_composite_param(self, search_request):
        payload = self._parameters.payload
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        date_of_birth = payload.get("date_of_birth")
        state_of_practice = payload.get("state_of_practice")

        if (
            self._assert_not_none(first_name)
            and self._assert_not_none(last_name)
            and self._assert_not_none(date_of_birth)
        ):
            search_request["fullName"] = f"{first_name} {last_name}"
            search_request["birthDate"] = date_of_birth

            if state_of_practice:
                search_request["stateCd"] = state_of_practice


        return search_request

    @classmethod
    def _get_entity_id(cls,entity_id, database):
        return database.query(User.ama_entity_id).filter(User.ama_entity_id == entity_id).one_or_none()

    def _construct_enterprise_service(self):
        wsdl_url = '../Source/Python/datalabs/access/vericre/api/enterprisesearch.wsdl'
        client = Client(wsdl=wsdl_url)

        service = client.bind('EnterpriseSearchService')
        # pylint: disable=protected-access
        service._binding_options['address'] = (
            f"https://{self._parameters.domain}.ama-assn.org/"
            "enterprisesearch/EnterpriseSearchService"
        )

        return service

    @classmethod
    def _call_enterprise_service(cls, search_request, service):
        if "stateCd" in search_request:
            response = service.SearchIndividualByState(searchIndividualByStateRequest=search_request)
        else:
            response = service.SearchEnterpriseEntity(searchEnterpriseEntityRequest=search_request)

        return response

    @classmethod
    def _get_physicians(cls, database, response):
        physicians = []

        if response is not None:
            physicians = [cls._get_physician(physician, database) for physician in response]
            physicians = list(filter(lambda physician: physician is not None, physicians))

        return physicians

    @classmethod
    def _get_physician(cls,physician, database):
        response = None
        entity_id = cls._get_entity_id_from_vericre(physician.entityId,database)

        if cls._assert_not_none(entity_id):
            response = dict(entity_id=physician.entityId,
                first_name=physician.legalFirstName,
                last_name=physician.legalLastName,
                date_of_birth=cls._get_date(physician.birthDate))

        return response

    @classmethod
    def _get_entity_id_from_vericre(cls,entity_id, database):
        response = None
        try:
            query = database.query(User.ama_entity_id).filter(User.ama_entity_id == entity_id)
            query = cls._filter_by_active_user(query)
            response = query.one_or_none()
        except OperationalError:
            raise InternalServerError("Vericre connection error. Please try again later.") 
        except MultipleResultsFound:
            LOGGER.error("Multiple results found for entity id : %s",entity_id)
            response = None

        return response

    @classmethod
    def _filter_by_active_user(cls, query):
        return query.filter(User.is_deleted == 'False').filter(User.status == 'ACTIVE')

    @classmethod
    def _get_date(cls, date_string):
        date_formatted = None
        try:
            date_object = datetime.strptime(date_string, "%Y%m%d")
            date_formatted = date_object.strftime("%Y-%m-%d")
        except (TypeError, ValueError) as error:
            LOGGER.error("Exception in formatting the date : %s",error)

        return date_formatted

    def _generate_response(self, physicians):
        self._response_body = self._generate_response_body(physicians)
        self._headers = self._generate_headers()
        self._status_code = self._generate_status_code(physicians)

    @classmethod
    def _generate_response_body(cls, physicians):
        return "No Content. Search request did not find any matches" if not physicians else physicians

    @classmethod
    def _generate_headers(cls):
        return {
            'Content-Type': 'application/json'
            }

    @classmethod
    def _generate_status_code(self, physicians):
        return 204 if not physicians else 200
