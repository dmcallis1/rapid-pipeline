import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import logging
import sys
import json
from lib import apiGwHelper

logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger()

# Full path to '.edgerc' file
edgeRcLoc = '/Users/dmcallis/.edgerc-a2snew'
edgeRcSection = 'default'

# Check arguments
argLen = len(sys.argv)
log.debug('Found ' + str(argLen) + ' command line arguments.')

if argLen != 3:
    log.error('Incorrect number of arguments! Found: ' + str(argLen - 1) + '. Expected: 1')
    log.error('Usage: updateEndpointSwagger.py [Api ID] [API Version]')
    sys.exit(1)

# Command line arguments
apiId = sys.argv[1]
version = sys.argv[2]

log.info('Using version passed from arguments: \'' + version + '\'')

for arg in sys.argv:
    log.debug('Argument: ' +  arg)

'''
    Edgegrid authentication Section
    Session and baseurl objects will be passed to helper methods.
'''

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

log.info('Checking activation status for ' + apiName + ' version: ' + version)

networks = ['staging', 'production']

create = False

for network in networks:
    activeStatus, activeVersion = apiGwHelper.getActivationStatus(session, baseurl, apiId, version, network)

    log.info(network + ' network status: ' + activeStatus + ' version: ' + activeVersion + ' (current version: ' + version + ').')

    if version == activeVersion:
        create = True


if create == True:

    log.info('Creating new API version for ' + apiName + '. Based off version: ' + version)

    try:
        respCode = apiGwHelper.createApiVersion(session, baseurl, apiId, version)
    except Exception as e:
        log.error('Exception encountered creating new API endpoint version!')
        log.error(e)
        sys.exit(1)

    version, apiName = apiGwHelper.getLatestVersion(session, baseurl, apiId)
    log.info('Created new ' + apiName + ' API endpoint version: ' + version)

else:
    log.info('The latest ' + apiName + ' API Definition version ' + version + ' is not active in any network. Skipping create step.')