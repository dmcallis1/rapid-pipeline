import yaml
import os.path
import json

def validateSwaggerFile(swaggerFile):

    # Todo - pass in swagger file as argument
    isFile = os.path.isfile(swaggerFile)
    return isFile


def getLatestVersion(session, baseurl, apiId):

    '''

    Returns a string with the latest version number of the API Gateway definition.

    :param session:
    :param baseurl:
    :param apiId:
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions'
    result = session.get(endpoint).json()

    # Latest version should always be at position 0
    version = str(result['apiVersions'][0]['versionNumber'])
    name = str(result['apiEndPointName'])


    return version, name

def getResourceFromVersion(session, baseurl, apiId, version):

    '''

    Returns a JSON object containing the API definition (as returned from the API Gateway) for a specific API version.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/resources-detail'
    result = session.get(endpoint).json()

    return result

def uploadSwaggerDef(session, baseurl, apiId, version, swaggerFile):

    '''

    Updates a specific version of an API Definition using an external swagger file.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :param swaggerFile:
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/file'

    params = {'importFileFormat': 'swagger'}
    files = {'importFile': (os.path.basename(swaggerFile), open(swaggerFile, 'r'), 'application/x-yaml')}
    resp = session.post(endpoint, data=params, files=files)

    return resp.status_code, resp.content

def compareDefinitionCounts(session, baseurl, apiId, version, swaggerFile):

    '''

    Compares the number of API resources in a swagger file (provided) with a specific API version.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :param swaggerFile:
    :return:
    '''

    result = getResourceFromVersion(session, baseurl, apiId, version)
    apiDefNum = len(result['apiResources'])

    fileDef = yaml.load(open(swaggerFile, 'r'))
    fileDefNum = str(len(fileDef['paths'].keys()))

    return apiDefNum, fileDefNum

def activateVersion(session, baseurl, apiId, version, network, emailList):

    activationObject = {
        "networks": [
            network
        ],
        "notificationRecipients": emailList,
        "notes": "Activating endpoint on + " + network + " network."
    }

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/activate'
    resp = session.post(endpoint, json=activationObject)

    return resp.status_code, resp.content

def getActivationStatus(session, baseurl, apiId, version, network):

    result = getResourceFromVersion(session, baseurl, apiId, version)
    network = network + 'Version'
    activationStatus = result[network]['status']
    activationVersion = result[network]['versionNumber']
    return activationStatus, activationVersion

def createApiVersion(session, baseurl, apiId, version):

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/cloneVersion'
    resp = session.post(endpoint)
    return resp.status_code