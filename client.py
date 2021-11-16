# Testrail Client Methods
from testrail import *
import testrail_config as config
import requests
from requests.auth import HTTPBasicAuth

client = config.client
client.user = config.testrail_user
client.password = config.testrail_password


# Client Methods #

### Testrail API ####

# def add_testcase(testcase_name):
#
#     """
#     Send POST request to testrail client to add an individual testcase
#     param testcase_name: str obj
#     return: POST response - dict obj
#     """
#     # POC uses 1 section id
#     section_id = config.section_id
#     request_body = {
#         "title": testcase_name,
#         "type_id": 1
#     }
#     resp = client.send_post('add_case/{}'.format(section_id), request_body)
#     return resp
#
#
# def get_testcases():
#     """
#     """
#     # 1 project id and suite id in POC
#     project_id = config.project_id
#     resp = client.send_get('get_cases/{}'.format(project_id))
#     cases = resp['cases']
#     existing_testcases = {elem['id']:elem['title'] for elem in cases}
#     return existing_testcases
#


############## Microservice ####################
#
def get_testcase(testcase):
    """
    """
    resp = requests.get('{}/testcase/byName?testcaseName={}'.format(config.micro_client, testcase),
                        auth=HTTPBasicAuth(client.user, client.password))
    resp_data = resp.json()
    testcase = resp_data[:]
    testcase_name = {elem['id']: elem['name'] for elem in testcase}
    return testcase_name


def get_testcases():
    """
    """
    # project name should be arg for func

    resp = requests.get('{}/testcase/byProjectName?projectName={}'.format(config.micro_client, config.micro_proj_name),
                        auth=HTTPBasicAuth(client.user, client.password))

    resp_data = resp.json()
    cases = resp_data[:]
    existing_testcases = {elem['id']: elem['name'] for elem in cases}
    return existing_testcases


def add_testcase(testcase_name):
    """
    """
    req_body = {
        "projectName": config.micro_proj_name,
        "testCaseName": testcase_name
    }
    resp = requests.post('{}/testcase/add?projectName=EAF_POC&testCaseName={}'.format(config.micro_client,
                                                                                      req_body),
                         auth=HTTPBasicAuth(client.user, client.password))
    resp_data = resp.json()

    return resp_data

