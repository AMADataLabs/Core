import argparse
from   collections import defaultdict
import json
import os
import subprocess
import sys

from   datalabs.access.api.awslambda import APIEndpointTaskWrapper
from   datalabs.plugin import import_plugin

import repo


def main(args):
    repo.configure()  # Setup the repo's PYTHONPATH

    os.environ["DYNAMODB_CONFIG_TABLE"] = "DataLake-configuration-dev"
    os.environ["API_ID"] = args["api"]

    query_parameters = aggregate_query_parameters(args["query_parameter"] or [])
    payload = json.loads(args["payload"])
    event = generate_api_gateway_event(args["method"], args["endpoint"], query_parameters, args["no_auth"])

    event["payload"] = payload

    task_wrapper = APIEndpointTaskWrapper(event)

    print(task_wrapper.run())


def aggregate_query_parameters(query_parameter_kvargs):
    query_parameters = defaultdict(list)

    for kvarg in query_parameter_kvargs:
        key, value = tuple(kvarg.split("="))

        query_parameters[key].append(value)

    return query_parameters

def generate_api_gateway_event(method, endpoint, query_parameters, no_auth):
    single_query_parameters = {key:value[0] for key, value in query_parameters.items()}
    authorizer_context = ""

    if not method:
        method = "GET"

    if not no_auth:
        authorizer_context = f'''
            "authorizer": {{
                "CPTAPI": "2048-10-06-05:00",
                "principalId": "username",
                "integrationLatency": 0,
                "customerNumber": "000002164389",
                "customerName": "TEST Health Solutions"
            }}, "resourcePath": "{endpoint}",
        '''

    event = f'''{{
        "resource": "{endpoint}",
        "path": "{endpoint}",
        "httpMethod": "{method}",
        "headers": {{
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate, br",
            "Authorization": "Bearer WJfefqn5pWUZ9jv2RorEucE0MLVUemayqGAByOsS",
            "Host": "localhost",
            "Postman-Token": "50934e08-9798-4eb4-bf8d-ec8e96060a2a",
            "User-Agent": "PostmanRuntime/7.29.0",
            "x-amzn-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256",
            "x-amzn-tls-version": "TLSv1.2",
            "x-amzn-vpc-id": "vpc-0f54b51b973b709d2",
            "x-amzn-vpce-config": "1",
            "x-amzn-vpce-id": "vpce-0bc731de06c089ce1",
            "X-Forwarded-For": "172.31.10.211"
        }},
        "multiValueHeaders": {{
            "Accept": ["*/*"],
            "Accept-Encoding": ["gzip, deflate, br"],
            "Authorization": ["Bearer WJfefqn5pWUZ9jv2RorEucE0MLVUemayqGAByOsS"],
            "Host": ["localhost"],
            "Postman-Token": ["50934e08-9798-4eb4-bf8d-ec8e96060a2a"],
            "User-Agent": ["PostmanRuntime/7.29.0"],
            "x-amzn-cipher-suite": ["ECDHE-RSA-AES128-GCM-SHA256"],
            "x-amzn-tls-version": ["TLSv1.2"],
            "x-amzn-vpc-id": ["vpc-0f54b51b973b709d2"],
            "x-amzn-vpce-config": ["1"],
            "x-amzn-vpce-id": ["vpce-0bc731de06c089ce1"],
            "X-Forwarded-For": ["172.31.10.211"]
        }},
        "queryStringParameters": {json.dumps(single_query_parameters)},
        "multiValueQueryStringParameters": {json.dumps(query_parameters)},
        "pathParameters": null,
        "stageVariables": null,
        "requestContext": {{
            "resourceId": "zs07zi",
            {authorizer_context}
            "resourcePath": "{endpoint}",
            "operationName": "getFiles",
            "httpMethod": "{endpoint}",
            "extendedRequestId": "QmOw7G1BIAMFYJQ=",
            "requestTime": "15/Apr/2022:01:05:22 +0000",
            "path": "{endpoint}",
            "accountId": "644454719059",
            "protocol": "HTTP/1.1",
            "stage": "sbx",
            "domainPrefix": "cpt-api-sbx",
            "requestTimeEpoch": 1649984722561,
            "requestId": "c2fc2e4d-8082-4375-a923-e7c4fddbf51a",
            "identity": {{
                "cognitoIdentityPoolId": null,
                "cognitoIdentityId": null,
                "vpceId": "vpce-0bc731de06c089ce1",
                "principalOrgId": null,
                "cognitoAuthenticationType": null,
                "userArn": null,
                "userAgent": "PostmanRuntime/7.29.0",
                "accountId": null,
                "caller": null,
                "sourceIp": "172.31.10.211",
                "accessKey": null,
                "vpcId": "vpc-0f54b51b973b709d2",
                "cognitoAuthenticationProvider": null,
                "user": null
            }},
            "domainName": "localhost",
            "apiId": "b1secmwhmj"
        }},
        "body": null,
        "isBase64Encoded": false
    }}'''

    return json.loads(event)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--api', help='API ID.')
    ap.add_argument('-e', '--endpoint', help='Endpoint path.')
    ap.add_argument('-p', '--query-parameter', action='append', help='Query parameter as name=value.')
    ap.add_argument('-m', '--method', help='Use specified HTTP method.')
    ap.add_argument('-P', '--payload', default='{}', help='JSON paylod.')
    ap.add_argument('-A', '--no-auth', action='store_true', help='Do not add Authorizer context.')
    args = vars(ap.parse_args())

    main(args)