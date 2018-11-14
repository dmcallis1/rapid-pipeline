import logging
import sys
import json
from lib import apiGwHelper
import requests
from time import sleep
from akamai.edgegrid import EdgeGridAuth, EdgeRc

logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger()

# Full path to '.edgerc' file
edgeRcLoc = '/Users/dmcallis/.edgerc-a2snew'
edgeRcSection = 'default'

# List for activation email
emailList = ['dmcallis@akamai.com']

# Check arguments
argLen = len(sys.argv)
log.debug('Found ' + str(argLen) + ' command line arguments.')

if argLen != 4:
    log.error('Incorrect number of arguments! Found: ' + str(argLen - 1) + '. Expected: 3')
    log.error('Usage: activateApiVersion.py [Api ID] [Network] [Version]')
    sys.exit(1)

# Command line arguments
apiId = sys.argv[1]
network = sys.argv[2]
version = sys.argv[3]


for arg in sys.argv:
    log.debug('Argument: ' +  arg)

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