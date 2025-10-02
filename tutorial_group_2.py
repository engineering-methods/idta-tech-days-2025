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
    wrapper = aasClient.create_wrapper_by_url(AAS_SERVER_URL)
    client = wrapper.get_client()

    shells = wrapper.get_all_asset_administration_shells()
    shells2 = client.get_all_asset_administration_shells()


    # get all AAS from server

    # get the AAS used in the tutorial
    shell = wrapper.get_asset_administration_shell_by_id(TUTORIAL_AAS_ID)
    
    aimc_submodel = None
    # search for the AssetInterfacesMappingConfiguration Submodel by the semantic ID
    for sm_ref in shell.submodel:
        sm_id = sm_ref.key[0].value
        sm = wrapper.get_submodel_by_id(sm_id)
        
        if sm.semantic_id is None:
            continue
        
        if AIMC_SEMANTIC_ID in sm.semantic_id.key[0].value :
            aimc_submodel = sm
            break

    # parse the AIMC Submodel to get the mapping configurations
    aimc_parser = AIMCParser(aimc_submodel)
    configurations = aimc_parser.parse_mapping_configurations()
    
    aid_submodels: list = []
    # get all AID Submodels defined in the AIMC configuration
    for submodel_id in configurations.aid_submodel_ids:
        aid_sm_dict = client.get_submodel_by_id(submodel_id)
        aid_submodels.append(aid_sm_dict)

    # create session to Asset Connector
    asset_connector_session = requests.Session()
    asset_connector_session.headers.update({"Content-Type": "application/json"})
    
    for aid_submodel in aid_submodels:
        request_payload = { "Aid": aid_submodel }
        response = asset_connector_session.post(ASSET_CONNECTOR_URL + "add-config", json=request_payload)


    # add the aid submodels (in json format) to the Asset Connector configurations

    print(2)

    counter = 1
    while (counter <= 1000):
        for configuration in configurations.configurations:
            # iterate over all mapping configurations and get the values for the source references from the Asset Connector
            for source_ref in configuration.source_sink_relations:
                source_ref_dict = source_ref.source_as_dict()
                payload = { "Reference" : source_ref_dict }
                response = asset_connector_session.post(ASSET_CONNECTOR_URL + "get-value", json=payload)


                response_content: dict = json.loads(response.content)
                response_payload = response_content.get("Payload", None)
                print("---")
                print(f"{source_ref.property_name}: {json.dumps(response_payload, indent=4)}")
                print("---")

        time.sleep(2)
        counter += 1
    
    
if __name__ == "__main__":
    print("Start tutorial.")
    tutorial_final()
    print("Tutorial completed.")