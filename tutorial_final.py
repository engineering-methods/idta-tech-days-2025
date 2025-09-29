import requests
import aas_http_client as aasClient
from aas_standard_parser import AIMCParser
import json
import time

AAS_SERVER_URL = "https://techdays-alm.em.ag/"
ASSET_CONNECTOR_URL = "https://techdays-resource-alm.em.ag/"

TUTORIAL_AAS_ID = "https://fluid40.de/ids/shell/8547_5433_6140_7422"
AIMC_SEMANTIC_ID = "/idta/AssetInterfacesMappingConfiguration"

def tutorial_final():

    # create AAS client and connect to server
    print("Create AAS server client and connect to server.")
    wrapper = aasClient.create_wrapper_by_url(AAS_SERVER_URL)
    client = wrapper.get_client()
    
    # get all AAS from server
    print("Get all Asset Administration Shells from AAS server.")
    shells = wrapper.get_all_asset_administration_shells()
    
    for shell in shells:
        print(f"Found AAS with idShort '{shell.id_short}' and id '{shell.id}'")
    
    # get the AAS used in the tutorial
    tutorial_shell = wrapper.get_asset_administration_shell_by_id(TUTORIAL_AAS_ID)
    print(f"Working with AAS '{tutorial_shell.id_short}' with {len(tutorial_shell.submodel)} submodels.")
    
    # search for the AssetInterfacesMappingConfiguration Submodel by the semantic ID
    aimc_submodel = None
    for submodel_ref in tutorial_shell.submodel:
        submodel_id = submodel_ref.key[0].value
        submodel = wrapper.get_submodel_by_id(submodel_id)
                
        if (submodel.semantic_id is None or len(submodel.semantic_id.key) < 1):
            continue
        
        submodel_semantic_id = submodel.semantic_id.key[0].value
        
        if AIMC_SEMANTIC_ID in submodel_semantic_id:
            aimc_submodel = submodel
            break
        
    print(f"Found AIMC Submodel with idShort '{aimc_submodel.id_short}' and id '{aimc_submodel.id}'")

    # parse the AIMC Submodel to get the mapping configurations
    print("Parse the AIMC Submodel to get the mapping configurations.")
    aimc_parser = AIMCParser(aimc_submodel)    
    aimc_configuration = aimc_parser.parse_mapping_configurations()


    # get all AID Submodels defined in the AIMC configuration
    print("Get all AID Submodels defined in the AIMC configuration.")
    aid_submodels: list = []
    for submodel_id in aimc_configuration.aid_submodel_ids:
        print(f"Get AID Submodel with id '{submodel_id}' from AAS server.")
        aid_submodel_dict = client.get_submodel_by_id(submodel_id)
        aid_submodels.append(aid_submodel_dict)

    print(f"Found {len(aid_submodels)} AID Submodels defined in the AIMC configuration.")
    
    # create session to Asset Connector
    print("Create session to Asset Connector.")
    asset_connector_session = requests.Session()
    asset_connector_session.headers.update({"Content-Type": "application/json"})
    
    # add the aid submodels (in json format) to the Asset Connector configurations
    print("Add the AID Submodels to the Asset Connector configurations.")
    for aid_submodel in aid_submodels:
        # create payload and post to Asset Connector
        request_payload = { "Aid" : aid_submodel }
        response = asset_connector_session.post(ASSET_CONNECTOR_URL + "add-config", json=request_payload)
        print(f"Add AID Submodel with id '{aid_submodel['id']}' to Asset Connector. Response: {response.status_code}")
    
    counter = 1
    while (counter <= 1000):
        # iterate over all mapping configurations and get the values for the source references from the Asset Connector
        for mapping in aimc_configuration.configurations:
            for relation in mapping.source_sink_relations:
                # create payload and post to Asset Connector
                request_payload = { "Reference" : relation.source_as_dict() }           
                response = asset_connector_session.post(ASSET_CONNECTOR_URL + "get-value", json=request_payload)
                
                # read and print the response
                response_content: dict = json.loads(response.content)
                response_payload = response_content.get("Payload", None)
                print("---")
                print(f"{relation.property_name}: {json.dumps(response_payload, indent=4)}")
                print("---")
        
        time.sleep(2)
        counter += 1
    
    
    print("Print all mapping configurations:")

if __name__ == "__main__":
    print("Start tutorial.")
    tutorial_final()
    print("Tutorial completed.")