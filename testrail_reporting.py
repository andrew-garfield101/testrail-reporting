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
    # parse xml file
    run_cli = parse_junit_xml(filename=xml_input)
    new_tests = run_cli
    # get existing tests in TR compare to new_tests list & remove existing testcases
    existing_tests = client.get_testcases()
    for test in new_tests:
        for k, v in existing_tests.items():
            if test == v:
                new_tests.remove(test)
    # add tests not in TR
    for test in new_tests:
        tests_added = client.add_testcase(test)

    return tests_added

    # add results parse


if __name__ == "__main__":
    main()
