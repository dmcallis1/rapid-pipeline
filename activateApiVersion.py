import logging
import sys
from lib import apiGwHelper
import requests
from time import sleep
import argparse
import os
from akamai.edgegrid import EdgeGridAuth, EdgeRc

logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger()

# Source in command line arguments
parser = argparse.ArgumentParser(description='API GW CI demo toolkit -> ' + os.path.basename(__file__))
requiredNamed = parser.add_argument_group('required arguments')
parser.add_argument('--config', action="store", default=os.environ['HOME'] + "/.edgerc", help="Full or relative path to .edgerc file")
parser.add_argument('--section', action="store", default="default", help="The section of the edgerc file with the proper {OPEN} API credentials.")
requiredNamed.add_argument('--version', action="store", default="latest", help="The version of the API Gateway definition, which will be compared with the new external API definition.")
requiredNamed.add_argument('--id', action="store", type=int, help="The Gateway property id for the target API Gateway.")
requiredNamed.add_argument('--network', action="store", default="staging", help="The target network to activate the version of the Akamai API Gateway on (PRODUCTION or STAGING)")
requiredNamed.add_argument('--email', action="store", help="A comma-seperated list of e-mails for which activation statuses will be sent.")
args = parser.parse_args()

if len(sys.argv) <=3:
    parser.print_help()
    sys.exit(1)

# List for activation email
emailList = args.email.split(",")

# Other Command line arguments
apiId = str(args.id)
network = args.network
version = args.version
edgeRcLoc = args.config
edgeRcSection = args.section

log.debug('Initializing Akamai {OPEN} client authentication. Edgerc: ' + edgeRcLoc + ' Section: ' + edgeRcSection)

try:
    edgerc = EdgeRc(edgeRcLoc)
    baseurl = 'https://%s' % edgerc.get(edgeRcSection, 'host')
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(edgerc, edgeRcSection)
    log.debug('API Base URL: ' + baseurl)

except Exception as e:
    log.error('Error authenticating Akamai {OPEN} API client.')
    log.error(e)

if version == 'latest':
    log.info('Requested latest version.')
    version, apiName = apiGwHelper.getLatestVersion(session, baseurl, apiId)

log.info('Activating API Definition version: ' + version + ' on network: ' + network + ' for API Definition: '+ apiName + '.')

try:
    respCode, respContent = apiGwHelper.activateVersion(session, baseurl, apiId, version, network, emailList)

    if respCode != 200:
        log.error('Error occurred during activation!')
        log.error('Response Code: ' + str(respCode))
        log.error('Response Reason: ' + str(respContent))
        sys.exit(1)

except Exception as e:
    log.error('Error occurred during activation!')
    log.error(e)


status, activeVersion = apiGwHelper.getActivationStatus(session, baseurl, apiId, version, network)

while status != 'ACTIVE':
    sleep(10)
    log.info('Activation status on ' + network + ': ' + status)
    status, activeVersion = apiGwHelper.getActivationStatus(session, baseurl, apiId, version, network)
    if status == 'ACTIVE':
        break

log.info('API Definition version ' + version + ' is now active for API Definition: ' + apiName + '.')