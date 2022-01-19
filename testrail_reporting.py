import argparse
import logging
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import client
import testrail_config as config
import config_helper as conf_help
import string
import random


def run_name_generator(size=8, chars=string.ascii_uppercase + string.digits):
    """
    Create simple random test run name for add_test_run() use
    """
    return ''.join(random.choice(chars) for _ in range(size))


def get_test_plan(plan_id):
    plan_content = config.client.send_get('get_plan/{}'.format(plan_id))
    return plan_content


def add_test_plan(name, config_ids, testcase_ids=[]):

    run_name = 'DCO Endpoints'
    entry_run = [{"name": run_name, "include_all": False, "case_ids": testcase_ids, "config_ids": [config_id]} for config_id in config_ids]

    entry_data = {
        "suite_id": conf_help.suite_id,
        "include_all": True,
        "case_ids": testcase_ids,
        'config_ids': config_ids,
        "runs": entry_run

    }
    req_body = {
        "name": name,
        "description": "",
        "entries": [entry_data]
    }

    test_plan_add = config.client.send_post('add_plan/{}'.format(conf_help.project_id), req_body)
    return test_plan_add


def add_test_run(run_name, testcase_ids):
    """
    Create new test run in Testrail using simple default values for POC purposes
    """
    #  Test Dev project id = 11
    test_run_request = {
        "suite_id": conf_help.suite_id,
        "name": run_name,
        "include_all": False,
        "case_ids": testcase_ids,
        "description": "Test Dev Demo Test Run"
    }

    add_run = config.client.send_post('add_run/{}'.format(conf_help.project_id), test_run_request)
    return add_run


def add_results(run_id, results):
    """
    Send parsed xml test results via add_results_for_cases - uses testcase_ids vs test ids
    param run_id: test run id created in main()
    param results: array of dicts containing testcase_ids, status_ids, and test_messages from xml
    """

    req_body = {
        "results": results
    }

    send_results = config.client.send_post('add_results_for_cases/{}'.format(run_id), req_body)

    return send_results


def add_results_for_cases(run_id, test_results):
    """
    """
    req_body = {
        "results": test_results
    }

    send_test_results = config.client.send_post('add_results_for_cases/{}'.format(run_id), req_body)
    return send_test_results


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


def parse_xml_results(filename):
    """
    Parse given junit xml file and return dictionary of test results
    param filename: junit xml file to be parsed
    return: dict obj
    """
    # skipped and error are custom statuses in testrail instance
    results = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    for elem in root.iter('testcase'):
        test_name = elem.get('name')

        failure = elem.find('failure')
        if failure is not None:
            status_id = 5
            test_message = failure.attrib['message']
            results[test_name] = [test_message, status_id]

        skipped = elem.find('skipped')
        if skipped is not None:
            status_id = 6
            test_message = skipped.attrib['message']
            results[test_name] = [test_message, status_id]

        # status id set to "retest" for error in test dev poc
        error = elem.find('error')
        if error is not None:
            status_id = 4
            test_message = error.attrib['message']
            results[test_name] = [test_message, status_id]

    return results


def main():
    """
    Parse junit xml file for testcases and test results - Create new test run in Testrail, and send up test results.

    """
    # CLI to specify junit xml_file to parse
    parser = argparse.ArgumentParser(description="Parse junit xml file and return results")
    parser.add_argument('-i', '--input', required=True, dest="input", help="junit xml file to be parsed")

    # 1 parse options
    args = parser.parse_args()

    # # 2 check xml file input is valid
    xml_input = Path(args.input)
    if not xml_input.is_file():
        sys.stderr.write("junit xml is not valid, or is unable to be found: {}".format(xml_input))
        sys.exit(1)

    # # 3 parse xml file for testcases
    run_cli = parse_junit_xml(filename=xml_input)
    new_tests = run_cli

    # # 3.5 get
    testcase_names_ids = {}
    xml_testcase_ids = []
    for test in new_tests:
        testcases = client.get_testcase(test)
        testcase = testcases['name']
        testcase_id = testcases['id']
        testcase_names_ids[testcase_id] = testcase
        xml_testcase_ids.append(testcase_id)

    # # 4 parse xml for test results
    get_xml_results = parse_xml_results(filename=xml_input)
    test_results = {}
    # test_results = {testcase_id: [testcase_name, [test_message, status_id]]}

    for test_id, test_name in testcase_names_ids.items():
        for k, v in get_xml_results.items():
            if test_name == k:
                test_results[test_id] = [k, v]

    for test_id, test_name in testcase_names_ids.items():
        if test_id not in test_results:
            status_id = 1
            test_message = "Test Passed"
            test_results[test_id] = [test_name, [test_message, status_id]]

    test_ids_for_run = list(test_results.keys())
    test_ids_for_run.sort()
    # results array for posting results
    results_array = []
    for k, v in test_results.items():
        d = {"case_id": k, "status_id": v[1][1], "comment": v[1][0]}
        results_array.append(d)

    # get configs and platform info
    all_configs = conf_help.get_configs()
    conf_ids = []
    for id in all_configs.values():
        conf_ids.append(id)
    platform_name, platform_arch = conf_help.find_platform_info()
    config_name, config_id = conf_help.find_platform_config(platform_name, platform_arch, all_configs)

    # # create test plan
    plan_name = run_name_generator()
    add_new_test_plan = add_test_plan(name=plan_name, config_ids=conf_ids, testcase_ids=test_ids_for_run)
    # # grab run and entry IDs using config_id for new test plan
    ent_id, run_id = conf_help.find_existing_config_in_test_plan(test_plan=add_new_test_plan, config_id=config_id)
    # # add xml test results to test_run specific to platform config id
    post_results = add_results_for_cases(run_id=run_id, test_results=results_array)
    return post_results


if __name__ == "__main__":
    main()

