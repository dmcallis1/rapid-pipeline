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
    log.error('Usage: updateEndpointSwagger.py [Api ID] [Path to Swagger File]')
    sys.exit(1)

# Command line arguments
apiId = sys.argv[1]
swaggerFile = sys.argv[2]

# Verify file exists
if apiGwHelper.validateSwaggerFile(swaggerFile) != True:
    log.error('The Swagger file argument provided is not a valid file, or it cannot be found.')
    log.error('Ensure the file is properly pathed and exists, with read permissions.')
    sys.exit(1)


log.info('Using swagger file: ' + swaggerFile)

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


log.info('Retrieving version from API: ' + apiId)

try:
    version, apiName = apiGwHelper.getLatestVersion(session, baseurl, apiId)
except Exception as e:
    log.error('Error getting latest version!')
    log.error(e)

log.info('Using latest version Id: ' + version + ' for API definition: ' + apiName)

# Compare API Definition and Swagger resource count
log.info('Comparing API definition resources with Swagger definition...')
try:
    apiDefNum, fileDefNum = apiGwHelper.compareDefinitionCounts(session, baseurl, apiId, version, swaggerFile)
    log.info('Swagger file resources: ' + str(fileDefNum) + '. API Definition Resources: ' + str(apiDefNum) + '.')

except Exception as e:
    log.error('Error encountered obtaining API resource counts for version: ' + version)
    log.error('Proceeding...')

log.info('Importing new API definitions from file: ' + swaggerFile)
try:

    respCode, respContent = apiGwHelper.uploadSwaggerDef(session, baseurl, apiId, version, swaggerFile)

    if respCode != 200:
        log.error('RAPID API returned an error!')
        log.error('Error: ' + str(respContent))

    log.info('Import Success! Response code: ' + str(respCode))


except Exception as e:
    log.error('Error importing swagger API definition!')
    log.error(e)