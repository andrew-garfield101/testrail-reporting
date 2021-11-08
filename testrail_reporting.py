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
    # parse xml for testcases - returns list of testcases
    run_cli = parse_junit_xml(filename=xml_input)
    # print("testcases found in xml file: {}".format(run_cli))

    # 2
    # check for existing testcases in testrail project - returns dict of {testcase_id: 'testcase_name'}
    run_test_check = check_for_existing_testcases()
    # print("Existing testcases in Testrail POC: {}".format(run_test_check))

    # 3 compare new parsed tests with existing tests - return dict of shared testcase_names {id: 'testcase_name'}
    new_tests = run_cli
    existing_tests = run_test_check
    # print("new_tests {}".format(new_tests))
    # print("existing_tests {}".format(existing_tests))
    pre_existing_tests = {}
    tests_to_add = []
    for elem in new_tests:
        for k, v in existing_tests.items():
            if elem == v:
                pre_existing_tests[k] = [v]
        else:
            if elem != v:
                tests_to_add.append(elem)


    # return pre_existing_tests
    print("these are the tests already exist in testrail {}".format(pre_existing_tests))
    print("tests to add {}".format(tests_to_add))

    # 4
    # add parsed testcases not in pre_existing_tests dict to testrail
    # tests_to_add = {}
    # for test in new_tests:
    #     if test not in pre_existing_tests:
    #         tests_to_add[test] = []

    # print("tests to add to testrail {}".format(tests_to_add))
    # add_testcases_to_testrail(testcases=tests_to_add)



if __name__ == "__main__":
    main()
