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
    
    
    # get all AAS from server

    
    # get the AAS used in the tutorial
    
    
    # search for the AssetInterfacesMappingConfiguration Submodel by the semantic ID


    # parse the AIMC Submodel to get the mapping configurations


    # get all AID Submodels defined in the AIMC configuration

    
    # create session to Asset Connector

    
    # add the aid submodels (in json format) to the Asset Connector configurations

    
    counter = 1
    while (counter <= 1000):
        # iterate over all mapping configurations and get the values for the source references from the Asset Connector
        
        
        time.sleep(2)
        counter += 1
    
    
if __name__ == "__main__":
    print("Start tutorial.")
    tutorial_final()
    print("Tutorial completed.")