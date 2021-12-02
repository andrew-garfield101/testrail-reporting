# testrail-reporting
### Testrail Reporting CLI to publish new testcases to a Testrail instance.

POC for Testrail Reporting in EAF. CLI takes a valid junit xml file and sends test results to Testrail Instance specified
in config. Functionality is aimed at specific aspects of POC. 

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

    Note: xml file needs to be in Project directory for POC
