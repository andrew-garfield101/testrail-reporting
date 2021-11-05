import argparse
import datetime
import sys
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import client


def parse_junit_xml(filename):
    """
    Parse a given junit xml file and return dict of testcases.
    param filename: junit xml file to be parsed
    return: list obj
    """

    testcases = []

    tree = ET.parse(filename)
    root = tree.getroot()
    for elem in root.iter():
        if elem.tag == 'testcase':
            testcase_name = elem.attrib['name']
            testcases.append(testcase_name)
    return testcases


def add_testcases_to_testrail(testcases):
    """
    Given list of testcase names, sends POST request to testrail client, returns dict of newly added testcases
    and their associated test_ids
    param testcases: list of testcases
    return: dict obj - testcases_added = {testcase_id: [testcase_name]}
    """
    testcases_added = {}

    for elem in testcases:
        add_test = client.add_testcase(testcase_name=elem)
        test_id = add_test['id']
        test_name = add_test['title']
        testcases_added[test_id] = [test_name]

    return testcases_added


def check_for_existing_testcases():
    """
    """
    check = client.get_testcases()
    return check


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

    # check for existing testcases
    run_testcase_check = check_for_existing_testcases()

    # add parsed testcases to testrail
    add_tests = add_testcases_to_testrail(run_cli)




