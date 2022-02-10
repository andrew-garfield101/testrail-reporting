# config helper file for mappings
import collections
import datetime
import logging
import re
import os
import random
import string
import platform
import distro
import testrail_config as config

# default config for default test_plan
right_now = datetime.datetime.today().strftime("%Y_%m_%d")
test_plan_name = "test_plan_{}".format(right_now)
# Test Dev project id and single test suite below
project_id = 11
suite_id = 1081
client = config.client

# os mapping
os_configs = ["Windows 11 x64", "Windows 11 x86",
              "Windows 10 x64", "Windows 10 x86",
              "Windows 8 x64", "Windows 8 x86",
              "CentOS 7 x64", "CentOS 8 x64",
              "RHEL 7 x64", "RHEL 8 x64",
              "Ubuntu 18.04 x64", "Ubuntu 20.04 x64",
              "MacOS Big Sur x64", "MacOS Catalina x64",
              "MacOS El Capitan x64", "MacOS High Sierra x64",
              "MacOS Mojave x64", "MacOS Sierra x64"]

# config_keywords / might not need ?
config_keywords = ['windows', 'linux', 'debian', 'ubuntu', 'redhat', 'darwin', 'centos', 'rhel']

# release & distro name maps from bts
macOS_release_name_map = {
    '11.2': 'Big Sur',
    '11.1': 'Big Sur',
    '11.0': 'Big Sur',
    '10.16': 'Big Sur',
    '10.15': 'Catalina',
    '10.14': 'Mojave',
    '10.13': 'High Sierra',
    '10.12': 'Sierra',
    '10.11': 'El Capitan'
}

linux_distro_name_map = {
    'Red Hat Enterprise Linux Server': 'RHEL',
    'CentOS Linux': 'CentOS',
    'Ubuntu': 'Ubuntu'
}


def run_name_generator(size=8, chars=string.ascii_uppercase + string.digits):
    """
    Create simple random test run name for add_test_run() use
    """
    return ''.join(random.choice(chars) for _ in range(size))


def config_os_type(config_name):
    for os_key in ['windows']:
        if os_key in config_name.lower():
            return 'windows'
    for os_key in ['centos', 'rhel', 'ubuntu']:
        if os_key in config_name.lower():
            return 'linux'
    for os_key in ['MacOS']:
        if os_key in config_name.lower():
            return 'darwin'


def get_configs():
    """
    """

    all_configs = client.send_get('get_configs/{}'.format(project_id))

    os_configs = {}

    for config_group in all_configs:
        if config_group['name'] == 'Operating Systems':
            for config in config_group['configs']:
                os_configs[config['name']] = config['id']
        if os_configs:
            break
    os_configs = collections.OrderedDict(sorted(os_configs.items(), key=lambda t: t[1]))

    return os_configs


def get_config_ids():
    """
    """
    get_ids = client.send_get('get_configs/{}'.format(project_id))
    ids = {}

    for config_group in get_ids:
        if config_group['name'] == 'Operating Systems':
            for config in config_group['configs']:
                ids[config['name']] = config['id']
        if ids:
            break
    return ids.values()


def get_test_plan(plan_id):
    """
    """

    get_existing_test_plan = client.send_get('get_plan/{}'.format(plan_id))
    return get_existing_test_plan


def add_test_plan(name, config_ids, testcase_ids=[]):

    run_name = 'DCO Endpoints'
    entry_run = [{"name": run_name, "include_all": False, "case_ids": testcase_ids, "config_ids": [config_id]} for config_id in config_ids]

    entry_data = {
        "suite_id": suite_id,
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

    test_plan_add = config.client.send_post('add_plan/{}'.format(project_id), req_body)
    return test_plan_add


def add_test_run(run_name, testcase_ids):
    """
    Create new test run in Testrail using simple default values for POC purposes
    """
    #  Test Dev project id = 11
    test_run_request = {
        "suite_id": suite_id,
        "name": run_name,
        "include_all": False,
        "case_ids": testcase_ids,
        "description": "Test Dev Demo Test Run"
    }

    add_run = config.client.send_post('add_run/{}'.format(project_id), test_run_request)
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


def find_platform_info():
    """
    Probe for platform information on the current machine, and return two strings representing the platform information
     and architecture formatted to match the naming scheme of testrail OS configurations.

    :return: Str representing platform config name (ex. RHEL 7), Str representing platform architecture (ex. x64)
    """
    platform_name = platform.system()
    word_size = platform.architecture()[0][:2]
    if word_size == "32":
        word_size = "86"
    platform_arch = "x{}".format(word_size)

    if platform_name == "Darwin":
        platform_name = "MacOS"
        platform_mac_release = platform.mac_ver()[0]
        for release in macOS_release_name_map:
            if release in platform_mac_release:
                platform_name = "{} {}".format(platform_name, macOS_release_name_map[release])
                break
        if platform_name == "MacOS":
            logging.warning("This appears to be a version of MacOS with no defined testrail configurations, no "
                            "reporting will be done on testrail: MacOS {}".format(platform_mac_release))
    elif platform_name == "Linux":
        dist_info = distro.linux_distribution()
        dist_name = dist_info[0]
        dist_release = 0
        for map_name in linux_distro_name_map:
            if dist_name in map_name:
                platform_name = linux_distro_name_map[map_name]

        if platform_name == "CentOS":
            version_string_split = dist_info[1].split(".")
            dist_major_release, dist_minor_release = version_string_split[0].strip(), version_string_split[1].strip()
            if int(dist_major_release) == 6 and int(dist_minor_release[:1]) >= 5:
                dist_release = "{}.{}".format(dist_major_release, 5)
            else:
                dist_release = dist_major_release
        elif platform_name == "RHEL":
            dist_release = dist_info[1].split(".")[0].strip()
        elif platform_name == "Ubuntu":
            dist_release = dist_info[1]
        else:
            logging.warning("This appears to be a Linux distribution with no defined testrail configurations, no "
                            "reporting will be done on testrail. Distribution info: {}".format(dist_info))

        platform_name = "{} {}".format(platform_name, dist_release)
    elif platform_name == "Windows":
        try:
            import winreg
        except:
            import _winreg as winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
            windows_product_name = winreg.QueryValueEx(key, "ProductName")[0]

        if "Server" in windows_product_name:
            match_obj = re.match(r"Windows Server 20[0-9]{2} ?(?:R2|SP2)?", windows_product_name)
            windows_product_name = match_obj.group(0).strip()
        elif "Windows 7" in windows_product_name:
            pass
        else:
            match_obj = re.match(r"Windows [8\.10]{0,3}", windows_product_name)
            windows_product_name = match_obj.group(0).strip()

        platform_name = windows_product_name

    return platform_name, platform_arch


def find_platform_config(platform_name, platform_arch, all_testrail_configs):
    """
    Map given platform_name and platform_arch to appropriate Testrail configuration.  Returns config_name = None and
     config_id = None when no matching configuration is found.

    :param platform_name: Str representing the platform configuration formatted to testrail convention (ex. RHEL 7)
    :param platform_arch: Str respresenting the platform architecture formatted to testrail convention (ex. x64)
    :param all_testrail_configs: OrderedDict of testrail OS configurations and corresponding config ids
    :return: Str representing matched testrail configuration name, Int representing matched testrail configuration id
    """
    config_name = None
    config_id = None
    # First try exact match
    for config in all_testrail_configs:
        match_name = "{} {}".format(platform_name, platform_arch)
        if match_name.lower() == config.lower():
            config_name, config_id = config, all_testrail_configs[config]

    # If exact match failed, try looser matching.
    # Disabling loose matching during migration to prevent overlapping results reporting
    # if not config_name:
    #     for config in all_testrail_configs:
    #         if platform_name.lower() in config.lower() and platform_arch in config.lower():
    #             config_name, config_id = config, all_testrail_configs[config]

    if not config_name:
        logging.warning("No defined testrail configuration matched this platform name and architecture ({} {}), "
                        "results will not be posted to testrail.".format(platform_name, platform_arch))

    return config_name, config_id


def find_existing_config_in_test_plan(test_plan, config_id):
    """
    Parses given test_plan json object to find any existing entry_id and run_id for the given config_id.  Returns
     (None, None) if no existing run/entry is found.

    :param test_plan: Dict (json) representing a testrail test plan
    :param config_id: Int representing a testrail configuration id
    :return: (Str, Int) representing the existing entry_id and run_id for the given config_id, or (None, None)
    """
    run_id = None
    entry_id = None
    if test_plan["entries"]:
        for entry in test_plan["entries"]:
            for run in entry["runs"]:
                if config_id in run["config_ids"]:
                    if not run_id:
                        run_id = int(run["id"])
                        entry_id = run["entry_id"]
                    else:
                        logging.warning("Multiple runs for this config id exist, please check test plan has one run "
                                        "per OS config id.  Continuing with first run id found.")
    return entry_id, run_id


def get_existing_case_id_list(testrail_client, test_run_id):
    """
    Get list of case ids already associated with a given test_run_id.  Will return an empty list of none are found,
     though I don't think testrail lets you create empty test runs...

    :param testrail_client: Testrail APIClient object
    :param test_run_id: Int or Str representing testrail test run id
    :return: List of Ints representing existing test cases in test run
    """
    test_list = testrail_client.send_get("get_tests/{}".format(test_run_id))
    test_elms = test_list['tests']
    case_id_elms = [sub['case_id'] for sub in test_elms]

    return case_id_elms


def update_test_plan_config(testrail_client, plan_id, plan_entry_id, config_id, testrail_case_list):
    """
    Update an existing test plan entry's run for given config_id with the given testrail_case_list.

    :param testrail_client: Testrail APIClient object
    :param plan_id: Int or Str representing testrail test plan id
    :param plan_entry_id: Str representing testrail test plan entry id
    :param config_id: Int or Str representing testrail OS configuration id
    :param testrail_case_list: List of Ints representing testrail testcase ids to add for this OS config run
    :return:
    """
    entry_data = {
        u"runs": [
            {
                u"include_all:": False,
                u"config_ids": [config_id],
                u"case_ids": testrail_case_list
            }
        ]
    }

    testrail_client.send_post("update_plan_entry/{}/{}".format(plan_id, plan_entry_id), entry_data)
    # Have to send an update post twice, or else it sometimes doesn't fully update the testrail entry run...
    logging.info("Updating testrail case list on existing test plan entry for this OS config.")
    logging.info(testrail_client.send_post("update_plan_entry/{}/{}".format(plan_id, plan_entry_id), entry_data))

    return


def add_test_plan_config(testrail_client, test_plan_id, suite_id, config_id, testrail_case_list):
    """
    Add a new entry + run for given config_id in given test plan with the given testrail_case_list.

    :param testrail_client: Testrail APIClient object
    :param test_plan_id: Int or Str representing testrail test plan id
    :param suite_id: Int or Str representing testrail test suite id
    :param config_id: Int or Str representing testrail OS configuration id
    :param testrail_case_list: List of Ints representing testrail testcase ids to add for this OS config run
    :return:
    """
    entry_data = {
        u"suite_id": suite_id,
        u"include_all": True,
        u"config_ids": [config_id],
        u"case_ids": testrail_case_list,
        u"runs": [
            {
                u"name": u"DCO Endpoints",
                u"include_all": False,
                u"config_ids": [config_id],
                u"case_ids": testrail_case_list
            }
        ]
    }

    logging.info("Adding a new test plan entry + run for this OS config.")
    post_response = testrail_client.send_post("add_plan_entry/{}".format(test_plan_id), entry_data)
    logging.info(post_response)
    run_id = post_response[u"runs"][0][u"id"]

    return run_id


def setup_plan_for_run(testcase_list, test_plan_id, config_id, overwrite_case_list=False):
    """
    """

    test_plan = get_test_plan(plan_id=test_plan_id)
    existing_entry_id, existing_run_id = find_existing_config_in_test_plan(test_plan, config_id)

    if existing_run_id:
        if not overwrite_case_list:
            testcase_list = list(set(get_existing_case_id_list(client, int(existing_run_id)) + testcase_list))
        update_test_plan_config(client, test_plan_id, existing_entry_id, config_id, testcase_list)
        plan_run_id = existing_run_id
    else:
        plan_run_id = add_test_plan_config(client, test_plan_id, suite_id, config_id, testcase_list)

    return int(plan_run_id)

