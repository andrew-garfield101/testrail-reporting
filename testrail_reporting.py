import argparse
import datetime
import sys
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import client
import requests


def parse_junit_xml(filename):
    """
    Parse a given junit xml file and return list of testcases.
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
        test_name = add_test['name']
        testcases_added[test_id] = [test_name]

    return testcases_added


def check_for_existing_testcases():
    """
    Checks testrail project for existing testcases, returns dict of testcase_ids and associated tests
    return: dict obj {testcase_id: 'testcase_name'}
    """
    check = client.get_testcases()
    return check


def main():
    """
    Add testcases to Testrail, parse a given xml file for testcases and add to Testrail project POC

    """
    # CLI to specify junit xml_file to parse
    parser = argparse.ArgumentParser(description="Parse junit xml file and return results")
    parser.add_argument('-i', '--input', required=True, dest="input", help="junit xml file to be parsed")

    # parse options
    args = parser.parse_args()

    # check xml file input is valid
    xml_input = Path(args.input)
    if not xml_input.is_file():
        sys.stderr.write("junit xml is not valid, or is unable to be found: {}".format(xml_input))
        sys.exit(1)

    # 1
    # parse xml for testcases - returns list of testcases
    run_cli = parse_junit_xml(filename=xml_input)

    # 2
    # check for existing testcases in testrail project - returns dict of {testcase_id: 'testcase_name'}
    run_test_check = check_for_existing_testcases()
    print("THESE ARE TESTS IN TESTRAIL {}".format(run_test_check))

    # 3
    # compare new parsed tests with existing tests - if tests exist in testrail add testcase name and id to dict
    # remove testcase name from list of new_tests to be added

    new_tests = run_cli
    existing_tests = run_test_check
    pre_existing_tests = {}

    for elem in new_tests:
        for k, v in existing_tests.items():
            if elem == v:
                pre_existing_tests[k] = [v]
                new_tests.remove(elem)
    print("NEW TESTS TO ADD {}".format(new_tests))

    # # 4
    # # add parsed tests not in existing cases to testrail
    if new_tests:
        try:
            add_testcases_to_testrail(testcases=new_tests)
        except Exception as err:
            logging.info("Unable to add test cases to Testrail: {}".format(err))

    if not new_tests:
        logging.info("No new tests to add")


if __name__ == "__main__":
    main()
