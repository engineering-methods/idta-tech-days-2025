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
    shells = wrapper.get_all_asset_administration_shells()

    # get all AAS from server
    print(3)
    # get the AAS used in the tutorial
    tutorial_shell = wrapper.get_asset_administration_shell_by_id(TUTORIAL_AAS_ID)
    
    aimc_submodel = None
    # search for the AssetInterfacesMappingConfiguration Submodel by the semantic ID
    for submodel_ref in tutorial_shell.submodel:
        id = submodel_ref.key[0].value
        sm =wrapper.get_submodel_by_id(id)
        
        if sm.semantic_id is None:
            continue
        
        submodel_semantic_id = sm.semantic_id.key[0].value
        if AIMC_SEMANTIC_ID in submodel_semantic_id:
            aimc_submodel = sm
            break
        

    # parse the AIMC Submodel to get the mapping configurations
    parser = AIMCParser(aimc_submodel)
    configurations = parser.parse_mapping_configurations()

    aid_submodel_data = []
    # get all AID Submodels defined in the AIMC configuration
    for submodel_id in configurations.aid_submodel_ids:
        client = wrapper.get_client()
        aid_submodel = client.get_submodel_by_id(submodel_id)
        aid_submodel_data.append(aid_submodel)


    # create session to Asset Connector
    session = requests.session ()
    session.headers.update({"Content-Type": "application/json"})
    
    for sm in aid_submodel_data:
        payload = { "Aid": sm }
        response = session.post(ASSET_CONNECTOR_URL + "add-config", json=payload)
    

    # add the aid submodels (in json format) to the Asset Connector configurations

    print(2)

    counter = 1
    while (counter <= 1000):
        for config in configurations.configurations:
            for relation in config.source_sink_relations:
                source = relation.source_as_dict()
                payload = { "Reference" : source }
                response = session.post(ASSET_CONNECTOR_URL + "get-value", json=payload)

                response_content: dict = json.loads(response.content)
                response_payload = response_content.get("Payload", None)
                print("---")
                print(f"{relation.property_name}: {json.dumps(response_payload, indent=4)}")
                print("---")

        time.sleep(2)
        counter += 1
    
    
if __name__ == "__main__":
    print("Start tutorial.")
    tutorial_final()
    print("Tutorial completed.")