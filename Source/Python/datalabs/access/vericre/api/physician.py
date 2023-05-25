""" Release endpoint classes."""
from dataclasses import dataclass
from zeep import Client
from datetime import datetime

import logging
import os

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError, InvalidRequest
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
    unknowns: dict=None
    payload: dict=None

class PhysiciansSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = PhysiciansSearchEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in PhysiciansSearchEndpointTask: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        
        search_request = self._construct_search_request()
        if not search_request:
            raise InvalidRequest("Invalid input parameters. Please provide either a combination of First Name, Last Name, and Date of Birth, or any of NPI number, ME number, or ECFMG number.")
        
        search_request["applicationId"] = "vericre"
        print("Request is ",search_request)       

        wsdl_url = '../Source/Python/datalabs/access/vericre/api/enterprisesearch.wsdl'
        client = Client(wsdl=wsdl_url)

        service = client.bind('EnterpriseSearchService')
        service._binding_options['address'] = f'https://{self._parameters.domain}.ama-assn.org/enterprisesearch/EnterpriseSearchService'

        if search_request.get("stateCd"):
            response = service.SearchIndividualByState(searchIndividualByStateRequest=search_request)
        else:
            response = service.SearchEnterpriseEntity(searchEnterpriseEntityRequest=search_request)
        
        if response is not None:
            physicians = [self._get_physician(physician, database) for physician in response]
            physicians = list(filter(lambda physician: physician is not None, physicians))

            self._generate_response(physicians)

    def _construct_search_request(self):
        search_request = dict()
        
        search_request = self._construct_request_for_single_param(search_request)

        if not search_request:
         search_request = self._construct_request_for_composite_param(search_request)

        return search_request

    def _construct_request_for_single_param(self, search_request):
        payload = self._parameters.payload
        continue_flag = True

        single_param_to_key = {
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
        
        # if self._assert_not_none(first_name) and self._assert_not_none(last_name) and self._assert_not_none(date_of_birth):
        if self._assert_not_none(first_name) and self._assert_not_none(last_name):
            search_request["fullName"] = f"{first_name}  {last_name}"
            search_request["birthDate"] = date_of_birth

            if self._assert_not_none(state_of_practice):
                search_request["stateCd"] = state_of_practice
       
        return search_request

    @classmethod
    def _assert_not_none(cls,param_value):
        return param_value not in [None,""]

    @classmethod
    def _get_date(cls, date_string):
        try:
            date_object = datetime.strptime(date_string, "%Y%m%d")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except Exception as e:
            LOGGER.error("Exception in formatting the date",e)
            return None

    @classmethod
    def _get_entity_id(cls,entity_id, database):
        response = None
        try:
            response = database.query(User.ama_entity_id).filter(User.ama_entity_id == entity_id).one_or_none()
            #Also add filter by active user- make that a common function
        except Exception as e:
            LOGGER.error("Exception in getting entity id",e)
            response = None
        return response
   
    @classmethod
    def _get_physician(cls,physician, database):
        entity_id = cls._get_entity_id(physician.entityId,database)
        if entity_id is not None:
            return dict(entity_id=physician.entityId,
                first_name=physician.legalFirstName,
                last_name=physician.legalLastName,
                date_of_birth=cls._get_date(physician.birthDate))
        else:
            return None

    def _generate_response(self, physicians):
        self._response_body = self._generate_response_body(physicians)
        self._headers = self._generate_headers()

    @classmethod
    def _generate_response_body(cls, physicians):
        return physicians

    @classmethod
    def _generate_headers(cls):
        return {
            'Content-Type': 'application/json'
            }
