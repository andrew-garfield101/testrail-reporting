# Testrail Client Methods
import json

from testrail import *
import testrail_config as config
import requests
from requests.auth import HTTPBasicAuth

client = config.client
client.user = config.testrail_user
client.password = config.testrail_password


def get_testcases():
    """
    Returns dict {test_id : 'testcase_name'}
    """
    url = '{}testcase/byProjectName?projectName={}'.format(config.micro_client, config.micro_proj_name)
    auth = HTTPBasicAuth(client.user, client.password)
    resp = requests.get(url=url, auth=auth)
    if resp.status_code != 200:
        return None
    resp_data = json.loads(resp.content)
    test_data = {elem['id']: elem['name'] for elem in resp_data}
    return test_data


def add_testcase(testcase):
    """
    """
    url = '{}testcase/add?projectName={}&testCaseName={}'.format(config.micro_client, config.micro_proj_name, testcase)
    auth = HTTPBasicAuth(client.user, client.password)
    resp = requests.post(url=url, auth=auth)
    if resp.status_code != 200:
        return None
    resp_data = json.loads(resp.content)
    return resp_data
