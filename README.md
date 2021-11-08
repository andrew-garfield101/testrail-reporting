# testrail-reporting
### Testrail Reporting CLI to publish new testcases to a Testrail instance.

This tool is primarily setup as a POC, functionality is aimed at those specific aspects.

### Config
Edit config file to reflect updated instance values:

    testrail_config.py
    from testrail import *
    
    client = APIClient(url for Testrail instance)
    testrail_user = email address for testrail user
    testrail_password = password for testrail user

### Use
To run the CLI:

    python ./testrail_reporting.py -i <test_result_example.xml>

