import argparse
import datetime
import sys
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import client


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
        test_name = add_test['title']
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
    # parse xml for testcases
    run_cli = parse_junit_xml(filename=xml_input)
    # print("testcases found in xml file: {}".format(run_cli))

    # 2
    # check for existing testcases in testrail project
    run_test_check = check_for_existing_testcases()
    # print("Existing testcases in Testrail POC: {}".format(run_test_check))
    existing_tests = run_test_check

    # 3
    # add parsed testcases to testrail
    add_tests = add_testcases_to_testrail(run_cli)
    # print("newly added testcases to testrail: {}".format(add_tests))
    new_tests = add_tests

    # 4
    # test dict comparison
    shared_tests = {}
    for i in existing_tests:
        if (i in new_tests) and (existing_tests[i] == new_tests[i]):
            shared_tests[i] = existing_tests[i]

    # print("these are the tests that exist already in testrail: {}".format(shared_tests))


if __name__ == "__main__":
    main()
