# Testrail Client Methods
import json

from testrail import *
import testrail_config as config
import requests
from requests.auth import HTTPBasicAuth

client = config.client
client.user = config.testrail_user
client.password = config.testrail_password


def get_testcase(*args):
    """
    """
    url = '{}/testcase?projectName={}&testcaseName={}'.format(config.micro_client, config.micro_proj_name, args[0])
    auth = HTTPBasicAuth(client.user, client.password)

    resp = requests.get(url=url, auth=auth)

    return resp.json()


