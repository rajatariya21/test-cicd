# ----------------------
# Misc
# ----------------------
AUTH_BASIC = "basic"
AUTH_DIGEST = "digest"
AUTH_OAUTH1 = "oauth1"
REQUEST_POST = "post"
REQUEST_GET = "get"

# ----------------------
# Messages
# ----------------------
SUCCESS = "success"

# Mongodb

MONGODBHOST = "MONGODBHOST"
MONGOUSER = "MONGOUSER"
MONGOPASSWORD = "MONGOPASSWORD"
MONGOLOCALHOST = "localhost:27017"
MONGOSERTOUT = 3000

# error
FAIL = "fail"


# ----------------------
# Airbyte
# ----------------------

LIBRARY_NAME = "airbyte"

# method_family

DESTINATION_DEFINITIONS = "destination_definitions"
SOURCE_DEFINITIONS = "source_definitions"


# method_name

LIST = "list"
GET = "get"

# airbyte keywords
AIRBYTE_DESTINATION_DEFINITIONS = "destinationDefinitions"
AIRBYTE_SOURCE_DEFINITIONS = "sourceDefinitions"
AIRBYTE_SOURCE_DEFINITION_ID = "sourceDefinitionId"
AB_DEST_DEF_ID = "destinationDefinitionId"
AIRBYTE_WORKSPACE_ID = "workspaceId"
AIRBYTE_SOURCE_ID = "sourceId"
AB_DEST_ID = "destinationId"
AB_SRC_DEF_SPEC = "source_definition_specifications"
AB_DEST_DEF_SPEC = "destination_definition_specifications"
AIRBYTE_NAME = "name"
AIRBYTE_API_TOKEN = "api_token"
AIRBYTE_EMAIL = "email"
AIRBYTE_DOMAIN = "domain"
AIRBYTE_ACCESS_TOKEN = "access_token"
AIRBYTE_PASSWORD = "password"
AIRBYTE_USERNAME = "username"
AIRBYTE_SSL = "ssl"
AIRBYTE_SCHEMA = "schema"
AIRBYTE_DATABASE = "database"
AIRBYTE_PORT = "port"
AIRBYTE_HOST = "host"
AIRBYTE_FORMAT = "format"
AIRBYTE_EMAIL = "email"
AB_ANONY_DATA_COLL = "anonymousDataCollection"
AIRBYTE_NEWS = "news"
AIRBYTE_SECURITY_UPDATES = "securityUpdates"
AIRBYTE_NOTIFICATIONS = "notifications"
AIRBYTE_DESTINATION_NAME = "destinationName"
AIRBYTE_CONNECTION_ID = "connectionId"
AIRBYTE_WITH_REFRESHED_CATALOG = "withRefreshedCatalog"
AB_CONN_SPEC = "connectionSpecification"
AIRBYTE_SOURCE_NAME = "sourceName"
AB_CONN_CONFIG = "connectionConfiguration"
AIRBYTE_HOST = "AIRBYTE_HOST"
AB_LOCALHOST = "http://localhost:8001"
AIRBYTE_API_VERSION = "AIRBYTE_API_VERSION"
AB_LOCAL_API_VERSION = "v1"
AIRBYTE_IS_SYNCING = "isSyncing"
AIRBYTE_LATEST_SYNC_JOB_STATUS = "latestSyncJobStatus"
AIRBYTE_CREATE = "create"
AB_DOC_URL = "documentationUrl"
AIRBYTE_DOCKER_TAG = "dockerImageTag"
AB_DOC_REPO = "dockerRepository"
AIRBYTE_DEV = "dev"
AIRBYTE_DOC_URL = "https://docs.airbyte.io/"
AB_CUST_DEST = "Custom Destination"
AB_CONTENT_TYPE = "Content-Type"
AB_APP_JSON = "application/json"
AB_DEST_DEF_CREATE_URL = "{}/api/v1/destination_definitions/create"
AB_WEBHOOK_URL = "{}/api/v1/workspaces/update"
AIRBYTE_WEB_HOST = "AIRBYTE_WEB_HOST"
AIRBYTE_CUSTOM_OUTPUT_DIRECTORY = "output_directory"
AB_CHECK_SRC = "{}/api/v1/sources/check_connection"
AB_CHECK_DEST = "{}/api/v1/destinations/check_connection"


SHARED_VOLUME_PATH = "SHARED_VOLUME_PATH"

WEAV_DATA_SERVICE = "WEAV_DATA_SERVICE"

WEAV_DATA_SERVICE_ADD_BY_PATH = "{}/api/v1/dataset/add_by_path"
WEAV_DEST_CUSTOM_PYTHON = "peeyushweav/weav_destination-custom-python"

# dataflow service
WEAV_DATAFLOW_DAG_TRIGGER = "{}/api/v1/dag/dag-trigger"
WEAV_DATAFLOW_SERVICE = "WEAV_DATAFLOW_SERVICE"
DICT_OF_DAGS_ID = {
    "ann":"ann_weav","bio":"bio_weav",
    "conll":"conll_weav","jira":"jira_weav",
    "json":"json_weav","jsonl":"jsonl_weav",
    "slack":"slack_weav","tsv":"tsv_weav",
    "csv":"structured_weav"
    }
EXECUTABLE_DAG = "executable_dag"
DAG_ID = "dag_id"
EXECUTION_CONTEXT = "execution_context"
DAG_RUN_ID = "dag_run_id"
CONFIGURATION = "configuration"


CONNECTOR_DEF_ID = "connector_def_id"
CONNECTION_ID = "connection_id"
PROPERTIES = "properties"
TYPE = "type"
DEFAULT = "default"
SOURCE = "source"
TOKEN = "token"
EMAIL = "email"
DOMAIN = "domain"
PASSWORD = "password"
USERNAME = "username"
ENCRYPT = "encrypt"
SCHEMA = "schema"
DATABASE = "database"
PORT = "port"
HOST = "host"
LOCATION = "location"
FILE_FORMAT = "file_format"
ANONYMOUS_DATA_COLLECTION = "anonymous_data_collection"
NEWS = "news"
SECURITY_UPDATES = "security_updates"
NOTIFICATIONS = "notifications"
SLUG = "slug"
WORKSPACES = "workspaces"
MINUTES = "minutes"
HOURS = "hours"
DAYS = "days"
WEEKS = "weeks"
MONTHS = "months"
CATALOG = "catalog"
SCHEDULE = "schedule"
STATUS = "status"
ACTIVE = "active"
ATTEMPTS = "attempts"
FAILED_ATTEMPTS = "failed_attempts"
CREATE = "create"
GET_BY_SLUG = "get_by_slug"
BASIC_NORMALIZATION = "basic_normalization"
REPOSITORY = "repository"
URL = "url"
PROVIDER = "provider"
DESTINATION_PATH = "destination_path"
STORAGE = "storage"
HTTPS = "HTTPS"
LOCAL = "local"
UNITS = "units"
TIME_UNIT = "timeUnit"
SOURCES = "sources"
DELETE = "delete"
UPDATE = "update"
DESTINATION = "destination"
DESTINATIONS = "destinations"
DISCOVER_SCHEMA = "discover_schema"
SYNC_CATALOG = "syncCatalog"
RULE = "rule"
CONNECTIONS = "connections"
MESSAGE = "message"
IS_SYNCING = "is_syncing"
REQUIRED = "required"
SOURCE_DEFINITION_ID = "source_definition_id"

SYNC = "sync"
JOB = "job"
JOBS = "jobs"

CONFIG_ID = "configId"
CONFIG_TYPES = "configTypes"
RECORDS_SYNCED = "recordsSynced"
REC_SYNC = "records_synced"
CONFIG = "config"
CREATED_AT = "createdAt"
UPDATED_AT = "updatedAt"
CONFIG_TYPE = "configType"
SUCCEEDED = "succeeded"
INCOMPLETE = "incomplete"
FAILED = "failed"
ATTEMPT = "attempt"
ID = "id"
LOGS = "logs"
LOG_LINES = "logLines"
STATE = "state"
STRING = "string"
FLOAT = "float"
INTEGER = "integer"
OBJECT = "object"
ARRAY = "array"
BOOL = "boolean"
EXAMPLES = "examples"
ONEOF = "oneOf"
WEB_BACKEND_CONNECTIONS = "web_backend/connections"
PROJECT_ID = "project_id"
DATASET_ID = "dataset_id"
ARTIFACT_ID = "artifact_id"
URL_PATH = "url_path"
LOCAL_INGESTED_FOLDER = "Local_Ingested"
FORMAT_3IP = "{}/{}/{}"
LOCAL_PREFIX = "/local{}"
WEAV_DATA_UPLOAD_RAW = "/weav-data/uploaded-raw-files/{}"
WEAV_DATA_AB_PATH = "/weav-data/airbyte/{}/default.csv"
WEAV_DATA_ING_PATH = "/weav-data/ingestion-raw-files/{}.{}"
WEAV_DATA_RAW_PATH1 = "/weav-data/ingestion-raw-files/{}"
WEAV_DATA_RAW_PATH2 = "/weav-data/ingestion-raw-files/{}/{}.csv"
INSPECT_URL = "{}/api/v1/introspection/inspect"
FILE_PREVIEW_URL = "{}/api/v1/introspection/file_preview"
INTROSPECTION_HOST = "INTROSPECTION_HOST"
INTROSPECTION_LOCALHOST = "http://localhost:7003"
EXCEL_LIST = ["xlsx","xlsm","xltx","xltm","xlsb","xla","xlam","xll","xlw","xls"]
JSON = "json"
JSONL = "jsonl"
# CSV_READABLES = ["csv","bio","conll","ans","iob2","txt","html","xml","tsv","tab","a1","a2","ann"]
PREVIEW_FORMATS = ["csv","jsonl","json","excel"]
AB_SUP_FORMAT = ["jsonl","json","feather","parquet"]
TXT = "txt"
CSV = "csv"
EXCEL = "excel"
FEATHER = "feather"
PARQUET = "parquet"
NOT_APPL = "Not Applicable"
DISCRIPTOR_COL_NAMES = "cols_names"
CSV_READS = "csv_readables"
EMPTY_STR = ""
DATASET_NAME = "dataset_name"
BIO_COL = ["Tag", "String"]
CONLL_COL = ["String", "Tag"]
TXT_COL = ["LineData"]
READER_OPTIONS = "reader_options"
DEF_READER_OPT = "{\"sep\" : \"\\n\", \"names\": [\"LineData\"], \"skip_blank_lines\": false, \"nrows\": 30}"
# DEF_READER_OPT = "{\"sep\" : \"\\n\", \"names\": [\"LineData\"], \"skip_blank_lines\": false}"
DEF_READER_OPT_EXCEL = "{\"nrows\":30}"
DEF_READER_OPT_LOCAL_UPLOAD = "{\"sep\" : \"\\n\", \"names\": [\"LineData\"], \"skip_blank_lines\": false}"
EXTENSION = "extension"
TAGS = "tags"
FILE = "file"
WRITE_MODE = 'w'
SEP = "sep"
NROWS = "nrows"
NAMES = "names"
QUOTING = "quoting"
SKIP_BLANK_LINES = "skip_blank_lines"
CONLL = "conll"
BIO = "bio"
DELIMETER = "delimeter"
FILE_TYPE = "file_type"
CONNECTOR_ID = "connector_id"
DESTINATION_ID = "destination_id"
SOURCE_NAME = "source_name"
CONNECTOR_NAME = "connector_name"
USER_DEFINED_NAME = "user_defined_name"
USER_ID = "user_id"
COL_ID = "_id"
ADDRESSES = "addresses"
PATH = "path"
RAW = "raw"
CODE = "code"
DATA = "data"
TEMP_VALUE = "temp"
LIBRARY_ARGS = "library_args"
DEMO_WORKSPACE = "workspace1"
CSV_DESTINATION = "CSV Destination Connector"
LOCAL_CSV = "local csv"
CONNECTOR_DELETED_SUCCESSFULLY = "Connector deleted successfully -- "
DESTINATION_DELETION_MESSAGE = "Destination deleted successfully"
CONNECTION_CONFIGURATIONS = "connection_configurations"
NO_CONN_MSG = "No connectors created by user yet"
NO_RECORD = "No record present for specified connector_id"
NO_STREAM = "No such stream available, Please select from available streams :{}"
WORKSPACE_ID = "workspace_id"
NAME = "name"
STREAMS = "streams"
WEBHOOK_TEST_CALL = "Hello World! This is a test from Airbyte"
DISCOVER_SCHEMA_MSG = "we have discovered following streams for {}, Please select the data stream you want to sync:"
DESTINATION_PATH = "destination_path"
CREATE_SOURCE_EXC_MESSAGE = "Could not create source due to Error: {}"
DELETE_SOURCE_EXC_MESSAGE = "Could not delete source due to Error: {}"
GET_SOURCE_EXC_MESSAGE = "Could not get source {}"
CREATE_DESTINATION_EXC_MESSAGE = "Could not create destination {}"
DELETE_DESTINATION_EXC_MESSAGE = "Could not delete source {}"
GET_DESTINATION_EXC_MESSAGE = "Could not get destination {}"
CREATE_CONNECTION_EXC_MESSAGE = "Could not create connection {}"
DELETE_CONNECTION_EXC_MESSAGE = "Could not delete connection {}"
STATUS_CONNECTION_EXC_MESSAGE = "Could not get status of connection {}"
LIST_CONNECTION_EXC_MESSAGE = "Could not give list of connection in given workspace {}"
DATASET_NAME_NOT_DETECTED = "We were unable to detect dataset name for the provided data source, please provide name for dataset and confirm the other details"
FORMAT_NOT_DETECTED = "We were unable to detect format of the provided data source, please provide format and confirm the other details"
MONGODB_ERROR_MSG = "We encountered an error while trying to connect to Mongodb: {}"
INTROSPECTION_ERROR_MSG = "We encountered an error while trying to connect IntrospectionService"
CHECK_CONNECTION_FAILED_MSG = "We encountered an error while trying to read source data with provided configurations: {}"
FILE_CSV_CONNECTOR_SUCCESS_MSG = "We detected below parameters for your dataset, you can update the parameters and test the connection again or click on Done to download the dataset with these parameters"
OTHER_CONNECTOR_SUCCESS_MSG = "Connector configured successfully"
SAMPLE_DOWNLOAD_EXCEPTION_MSG = "Failed to check source data with default configuration, please select correct configuration parameters and test the connection again."