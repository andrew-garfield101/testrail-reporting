import argparse
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import client
import config_helper as conf_help


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
    # # 1. CLI - specify junit xml_file & test_plan ID for test result reporting
    parser = argparse.ArgumentParser(description="Parse junit xml file and return results")
    parser.add_argument('-i', '--input', required=True, dest="input", help="junit xml file to be parsed")
    parser.add_argument('-p', '--plan_id', type=int, required=True, dest="plan_id", help="Testrail test plan ID")
    args = parser.parse_args()

    # # 2 check args (xml_file & test plan ID) are valid
    xml_input = Path(args.input)
    if not xml_input.is_file():
        sys.stderr.write("junit xml is not valid, or is unable to be found: {}".format(xml_input))
        sys.exit(1)

    test_plan_arg = conf_help.get_test_plan(args.plan_id)
    if test_plan_arg is None:
        sys.stderr.write("No test plan with ID {} found, please enter a valid test plan ID".format(test_plan_arg))
        sys.exit(1)
    else:
        test_plan_name = test_plan_arg['name']
        print("Test Plan Name & ID: {}, {}".format(test_plan_name, args.plan_id))
    
    # # 3 parse xml file for testcases, add testscases and testcase_ids to list
    run_cli = parse_junit_xml(filename=xml_input)
    new_tests = run_cli
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

    # # 5 get configs and platform info
    all_configs = conf_help.get_configs()
    conf_ids = []
    for id in all_configs.values():
        conf_ids.append(id)
    platform_name, platform_arch = conf_help.find_platform_info()
    config_name, config_id = conf_help.find_platform_config(platform_name, platform_arch, all_configs)

    # # 6 add test run entry to test plan w/ test results for specific config_id
    new_test_plan = conf_help.setup_plan_for_run(testcase_list=test_ids_for_run, test_plan_id=args.plan_id,
                                                 config_id=config_id, overwrite_case_list=False)

    # update results for specific OS run
    update_run = conf_help.add_results(run_id=new_test_plan, results=results_array)

    return update_run


if __name__ == "__main__":
    main()
