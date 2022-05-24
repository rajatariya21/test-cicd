import json, time
from app import app
from io import BytesIO
tester = app.test_client()


##test for get operations
get_all_response = tester.post("/api/v1/connectors/get_all")
get_config_response = tester.post("/api/v1/connectors/get_display_list",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({"source_definition_id":"778daa7c-feaf-4db6-96f3-70fd645acc77"}))
get_response = tester.post("/api/v1/connectors/get",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({"user_id" : "Sheshan01"}))
# Check for status 200
def test_get_status():
    assert get_all_response.status_code==200
    assert get_config_response.status_code==200
    assert get_response.status_code==200

# Check for returned type json
def test_get_apis_for_json_response():
    assert get_all_response.content_type == "application/json"
    assert get_config_response.content_type == "application/json"
    assert get_response.content_type == "application/json"

# Check for data returned
def test_get_apis_response_content():
    assert b'connector_def_id' in get_all_response.data
    assert b'sourceDefinitionId' in get_config_response.data
    assert b'No connectors' or b'connector_id' in get_response.data


# #test for workspace operations
workspaceresponse = tester.post("/api/v1/workspace/create",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({"name": "workspace_demo"}))


# Check for status 200
def test_workspace_status():
    assert workspaceresponse.status_code == 200


# Check for returned type json
def test_workspace_for_json_response():
    assert workspaceresponse.content_type == "application/json"


# Check for data returned
def test_workspace_response_content():
    assert b'workspace_id' in workspaceresponse.data


# #test for Connector and Connection operations

# Connector Creation
def test_connector_configure():
    Connector_configure = tester.post("/api/v1/connector/configure",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({
                        "user_id": "Sheshan01",
                        "workspace_id": "dummy",
                        "connector_name": "Pokeapi",
                        "user_defined_name": "Pokeapi_data",
                        "auth_method": "dummy",
                        "auth_token": "dummy",
                        "token_expiry_time": "dummy",
                        "project_id": "Pokeapi_data",
                        "password": "dummy",
                        "api_key": "dummy",
                        "connection_configurations": {
                        	"pokemon_name": "bulbasaur"
                            }
                        }))
    assert Connector_configure.status_code == 200
    assert Connector_configure.content_type == "application/json"
    assert b'connector_id' in Connector_configure.data
    global connector_id
    connector_id = Connector_configure.json["data"]["connector_id"]


# Connector Update
def test_connector_update():
    Connector_update = tester.post("/api/v1/connector/update",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                    "connector_id": connector_id,
                    "connection_configurations": {
                        "pokemon_name": "bulbasaur"
                        },
                    "user_defined_name": "POkiingApi",
                    "user_id": "Sheshan01",
                    "auth_method": "dummy",
                    "auth_token": "dummy_data",
                    "token_expiry_time": "dummy",
                    "project_id": "Pokeapi_data",
                    "password": "dummy",
                    "api_key": "dummy"
                        }))
    assert Connector_update.status_code == 200
    assert Connector_update.content_type == "application/json"
    assert b'connector_id' in Connector_update.data



#Connector View
def test_connector_view():
    Connector_view = tester.post("/api/v1/connector/get",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({
                    "connector_id": connector_id
                        }))
    
    assert Connector_view.status_code == 200
    assert Connector_view.content_type == "application/json"
    assert b'POkiingApi' in Connector_view.data

#Local uploader
def test_local_upload():
    file=(BytesIO(b'my file contents'), "Fake.csv")
    Local_upload = tester.post("/api/v1/connector/local_upload",
                    content_type='multipart/form-data',
                    data = {'file': file}
                )
    
    assert Local_upload.status_code == 200
    assert Local_upload.content_type == "application/json"
    assert b'successfully for Fake' in Local_upload.data
    

#Connection Create
def test_connection_create():
    Connection_create = tester.post("/api/v1/connection/create",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({
                    "connector_id": connector_id,
                    "artifact_id": "",
                	"schedule": {
                		"months": 1,
                		"weeks": 0, 
                		"days": 0,
                		"hours": 0,
                		"minutes": 0
                	}
                }))
    assert Connection_create.status_code == 200
    assert Connection_create.content_type == "application/json"
    assert b'Ingestion started' in Connection_create.data
    global connection_id
    connection_id = Connection_create.json["data"]["connection_id"]


##For now returning immediately for UI response so not getting connection_id in create response.
## so cant test Status,Trigger and Delete for now.
# #Connection Status
# Connection_response2 = tester.post("/api/v1/connection/status",
#                 headers = {"Content-Type": "application/json"}, 
#                 data = json.dumps())
# #Connection Trigger
# Connection_response3 = tester.post("/api/v1/connection/trigger",
#                 headers = {"Content-Type": "application/json"}, 
#                 data = json.dumps({
#                     "connector_id": str(Connection_response1.json["data"]["connector_id"])
#                         }))
# #Connection Delete
# Connection_response4 = tester.post("/api/v1/connection/stop",
#                 headers = {"Content-Type": "application/json"}, 
#                 data = json.dumps({
#                     "connector_id": str(Connection_response1.json["data"]["connector_id"])
#                         }))
# #Connector Delete
# zConnector_delete= tester.post("/api/v1/connector/delete",
#                 headers = {"Content-Type": "application/json"}, 
#                 data = json.dumps({
#                     "connector_id": str(Connector_configure.json["data"]["connector_id"])
#                         }))

#     # assert(Connection_response2.status_code,200)
#     # assert(Connection_response3.status_code,200)
#     # assert(Connection_response4.status_code,200)
# #Check for returned type json
# def test_connection_apis_for_json_response():
#     # assert(Connection_response2.content_type, "application/json")
#     # assert(Connection_response3.content_type, "application/json")
#     # assert(Connection_response4.content_type, "application/json")
# #Check for data returned
# def test_connection_apis_response_content():
    
#     # assert(b'' in Connection_response2.data)
#     # assert(b'' in Connection_response3.data)
#     # assert(b'' in Connection_response4.data)



####Need to test delete connector last or after create connection completes.

# def test_connector_delete():#Connection Create
#     #Connector Delete
#     Connector_delete= tester.post("/api/v1/connector/delete",
#                 headers = {"Content-Type": "application/json"}, 
#                 data = json.dumps({
#                     "connector_id": connector_id
#                     }))

#     assert Connector_delete.status_code,200
#     assert Connector_delete.content_type, "application/json"
#     assert b'deleted successfully' in Connector_delete.data


##Source tests
def test_source_create():
    source_create_response = tester.post("/api/v1/sources/create",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                        "type": "file",
                        "connection_configurations": {
	                    	"provider":{
	                    		"storage": "HTTPS"
	                    	},
                        	"url": "https://github.com/sheshan-doye-konvergeai/Myrepo/blob/main/amazon_co-ecommerce_sample.csv?raw=true",
                        	"format": "csv",
                        	"dataset_name": "amz_data"
                            },
                        "name": "AmzFile"
                    }))
    
    assert source_create_response.status_code == 200
    assert source_create_response.content_type == "application/json"
    assert b'connector_id' in source_create_response.data
    global source_id
    source_id = source_create_response.json["data"]["id"]
    
def test_source_update():
    source_update_response = tester.post("/api/v1/sources/update",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
	            "id": source_id,
	            "connection_configurations": {
	            	"provider":{
	            		"storage": "HTTPS"
	            	},
                	"url": "https://github.com/sheshan-doye-konvergeai/Myrepo/blob/main/amazon_co-ecommerce_sample.csv?raw=true",
                	"format": "csv",
                	"dataset_name": "amz_data"
	            },
	            "name": "Amazon_data"
                    }))
    assert source_update_response.status_code == 200
    assert source_update_response.content_type == "application/json"
    assert b'Amazon_data' in source_update_response.data
    
def test_source_read():
    source_read_response = tester.post("/api/v1/sources/read",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                        "id": source_id
                    }))
    assert source_read_response.status_code == 200
    assert source_read_response.content_type == "application/json"
    assert b'Amazon_data' in source_read_response.data
def test_source_delete():
    source_delete_response = tester.post("/api/v1/sources/delete",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                        "id": source_id
                    }))
    assert source_delete_response.status_code == 200
    assert source_delete_response.content_type == "application/json"
    assert b'Source deleted successfully' in source_delete_response.data


##Destination tests
def test_destination_create():
    destination_create_response = tester.post("/api/v1/destinations/create",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                "type": "local csv",
                "connection_configurations": {
                   "destination_path": "/local"
                    },
                "name": "AmzDestination"
}
))
    
    assert destination_create_response.status_code == 200
    assert destination_create_response.content_type == "application/json"
    assert b'connector_id' in destination_create_response.data
    global destination_id
    destination_id = destination_create_response.json["data"]["id"]
    
def test_destination_update():
    destination_update_response = tester.post("/api/v1/destinations/update",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
	            "id": destination_id,
                "connection_configurations": {
                   "destination_path": "/local"
                    },
	            "name": "Amazon_Destination"
                }))
    assert destination_update_response.status_code == 200
    assert destination_update_response.content_type == "application/json"
    assert b'Amazon_Destination' in destination_update_response.data
    
def test_destination_read():
    destination_read_response = tester.post("/api/v1/destinations/read",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                        "id": destination_id
                }))
    assert destination_read_response.status_code == 200
    assert destination_read_response.content_type == "application/json"
    assert b'Amazon_Destination' in destination_read_response.data

def test_destination_delete():
    destination_delete_response = tester.post("/api/v1/destinations/delete",
                headers = {"Content-Type": "application/json"},
                data = json.dumps({
                        "id": destination_id
                }))
    assert destination_delete_response.status_code == 200
    assert destination_delete_response.content_type == "application/json"
    assert b'Destination deleted successfully' in destination_delete_response.data

# Preview stream 
def test_get_stream_preview():
    get_response = tester.post("/api/v1/connectors/get_stream_preview",
                    headers = {"Content-Type": "application/json"}, 
                    data = json.dumps({
                        "connection_id" : connection_id,
                        "stream_name":"pokemon"}))
    assert get_response.status_code == 200
    assert get_response.content_type == "application/json"


#####test delete connector last or after create connection completes.

def test_connector_delete():
    #Connector Delete
    time.sleep(15)
    Connector_delete= tester.delete("/api/v1/connector/delete",
                headers = {"Content-Type": "application/json"}, 
                data = json.dumps({
                    "connector_id": connector_id
                    }))

    assert Connector_delete.status_code,200
    assert Connector_delete.content_type, "application/json"
    assert b'deleted successfully' in Connector_delete.data
