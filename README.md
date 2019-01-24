# API Gateway CI Toolkit

The *API Gateway CI Toolkit* contains a series of sample scripts which can be used to quickly implement an API Governance CI process for the [Akamai API Gateway](https://www.akamai.com/us/en/products/web-performance/api-gateway.jsp). API developers can use the *API Gateway CI Toolkit* to reconcile changes to API specification (using Swagger or RAML) with their Akamai API Gateway definition.
Such a CI process eliminates much of the administration overhead associated with the management of your Akamai API Gateway configuration state, allowing developers to focus on core services development.

The scripts contained in this project perform the following functions within a simple CI process:

1. Create a new version of an existing Akamai API Gateway configuration. Sanity checking logic is built in to understand the activation state of the target API gateway property version (updating if not activated, creating a new version if activated)
2. Update the Akamai API Gateway configuration using either a RAML or Swagger API definition artifact. This step also performs a high level comparison of the exiting API Gateway resource state and the new API definition.
3. Activate a new Akamai API Gateway configuration on either PRODUCTION or STAGING networks.

The above three steps can be orchestrated by some process workflow framework (Jenkins, Bamboo, Rundeck, etc) and triggered by some external event (such as a VCS event like commit or push) to automate the process of reconciling API definition updates with the Akamai API Gateway configuration state.

### Prerequisites

The *API Gateway CI Toolkit* requires the following to be in place prior to initial use:

1. An Akamai API client with 'API Definition' READ-WRITE authorizations https://developer.akamai.com/api/getting-started.
2. An existing API Gateway property created, with the 'Akamai-generated ID' value (found in Luna Control Center, in the API Gateway configuration section).

## Installation

All package dependencies are maintained in the requirements.txt file. Use pip to install:

pip install -r requirements.txt

### Runtime Environment

Each script was developed and tested using a python 3 (3.6.2) interpeter.

It should also be noted that the scripts assume the runtime environment will be a Linux/Unix OS. Some scripts expect Linux specific directory structures.

## Script Execution

All scripts must be invoked using the python3 interpreter directly.

Example python3 \<script\> \<arguments\>

The arguments supported by each script will be defined below, and can be identified by calling the script with a '--help' or no argument:

```
python3 activateApiVersion.py --help

usage: activateApiVersion.py [-h] [--config CONFIG] [--section SECTION]
                             [--version VERSION] [--id ID] [--network NETWORK]
                             [--email EMAIL]

API GW CI demo toolkit -> activateApiVersion.py

optional arguments:
  -h, --help         show this help message and exit
  --config CONFIG    Full or relative path to .edgerc file
  --section SECTION  The section of the edgerc file with the proper {OPEN} API
                     credentials.

required arguments:
  --version VERSION  The version of the API Gateway definition, which will be
                     compared with the new external API definition.
  --id ID            The Gateway property id for the target API Gateway.
  --network NETWORK  The Gateway property id for the target API Gateway.
  --email EMAIL      A comma-seperated list of e-mails for which activation
                     statuses will be sent.
```

While all scripts expect a series of required arguments (listed below), each script can support the following optional arguments:

- '--config': the absolute or relative path of the .edgerc file containing the Akamai API credentials
- '--section': the specific section within the .edgerc file containing the Akamai API credentials

## Script Detail

### createNewApiVersion.py

Creates a new API definition version. If the target API Gateway Definition version is not active, the script will detect this and perform no action on the property.

**Required Arguments**

- '--id': the value of the 'Akamai-generated ID' for the target property (found in Luna Control center).
- '--version': the target version to update (numeric or 'latest')

### updateEndpointFromDefinition.py

**Required Arguments**

- '--id': the value of the 'Akamai-generated ID' for the target property (found in Luna Control center).
- '--file': the relative or absolute path of the Swagger or RAML API definition which will be used to update the Akamai API Gateway definition.

### activateApiVersion.py

**Required Arguments**

- '--version': the version of the Akamai API Gateway property to activate.
- '--id': the value of the 'Akamai-generated ID' for the target property (found in Luna Control center).
- '--network': the target network to activate the version of the Akamai API Gateway on (PRODUCTION or STAGING).
- '--email': A comma-seperated list of e-mails for which activation statuses will be sent.