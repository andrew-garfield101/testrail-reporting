import argparse
import datetime
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from testrail import *

client = APIClient('')
client.user = ''
client.password = ''


def parse_junit_xml(filename):
    """
    Parse a given junit xml file and return dict of testcases.
    param filename: junit xml file to be parsed
    return: dict obj
    """

    testcase_names = {}
    testcases = []

    tree = ET.parse(filename)
    root = tree.getroot()
    for elem in root.iter():
        if elem.tag == 'testcase':
            testcase_name = elem.attrib['name']
            testcases.append(testcase_name)

    # dict of testcases
    # testcase_names = {"testcases": ['testcase_one', 'testcase_two', 'testcase_three']}
    # testcase_names['testcases'] = testcases
    # return testcase_names


    # list of testcases
    return testcases

    # call to add each test in testcase list to testrail api
    # for test in testcases:
    #     add_testcase(testcase_name=test)


# Client #

def add_testcase(testcase_name):
    """
    Send POST request to testrail client to add an individual testcase
    param testcase_name: str obj
    return: POST response - dict obj
    """

    # POC uses 1 section id
    section_id = 1
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
    project_id = 1

    resp = client.send_get('get_cases/{}'.format(project_id))
    return resp


if __name__ == "__main__":

    # default test run name
    now = datetime.datetime.today().strftime("%Y_%m_%d")
    test_run_name = "test_run_{}".format(now)

    parser = argparse.ArgumentParser(description="Parse junit xml file and return results")
    parser.add_argument('-i', '--input', required=True, dest="input", help="junit xml file to be parsed")

    # parse options
    args = parser.parse_args()

    # check input
    xml_input = Path(args.input)
    if not xml_input.is_file():
        sys.stderr.write("junit xml is not valid, or is unable to be found: {}".format(xml_input))
        sys.exit(1)

    # parse for testcases
    run_cli = parse_junit_xml(filename=xml_input)
    print("list of testcases from xml parsed {}".format(run_cli))

    # testcase_dict = {}

    # loop add_testcase func
    for test in run_cli:
        add_test = add_testcase(testcase_name=test)

    # grab testcases from api
    new_testcases = get_testcases()
    print("newly added testcase info {}".format(new_testcases))


