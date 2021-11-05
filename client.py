# Testrail Client Methods
from testrail import *
import testrail_config as config

client = config.client
client.user = config.testrail_user
client.password = config.testrail_password

# Client Methods #


def add_testcase(testcase_name):

    """
    Send POST request to testrail client to add an individual testcase
    param testcase_name: str obj
    return: POST response - dict obj
    """
    # POC uses 1 section id
    section_id = config.section_id
    request_body = {
        "title": testcase_name,
        "type_id": 1
    }
    resp = client.send_post('add_case/{}'.format(section_id), request_body)
    return resp


def get_testcases():
    """
    """
    # POC only 1 project suite
    project_id = config.project_id
    resp = client.send_get('get_cases/{}'.format(project_id))
    return resp
