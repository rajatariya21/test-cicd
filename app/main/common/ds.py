import uuid
from dataclasses import dataclass
from typing import Mapping

from dacite import from_dict
from dataclasses_jsonschema import JsonSchemaMixin


def get_request_json_as_dataclass(data_class, data):
    return from_dict(data_class=data_class, data=data)


def get_unique_id():
    return str(uuid.uuid4()).replace("-", "")


@dataclass
class TagAndMetaData(JsonSchemaMixin):
    tags: list = None
    metadata: dict = None


@dataclass
class UniqueItem(JsonSchemaMixin):
    id: str = get_unique_id()
    connector_id: str = None
    destination_id: str = None
    connection_id: str = None
    connection_configurations: dict = None
    message: str = None
    sample_preview: str = None
    sample_path: str = None


@dataclass
class DataSource(UniqueItem, TagAndMetaData):
    type: str = None
    connection_configurations: dict = None
    workspace_id: str = None
    name: str = None


@dataclass
class IngestionStream:
    json_schema: dict


@dataclass
class DataIngestionSchema:
    streams: Mapping[str, IngestionStream] = None


@dataclass
class Schedule:
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0


@dataclass
class IngestionRule(UniqueItem):
    source: DataSource = None
    destination: DataSource = None
    schema: DataIngestionSchema = None
    schedule: Schedule = None
    status: str = None


@dataclass
class StatusData(UniqueItem):
    connector_name: str = None
    status: str = None
    is_syncing: bool = None
    records_synced: int = None
    dataset_id: str = None


@dataclass
class IngestionExecution(StatusData, TagAndMetaData):
    rule: IngestionRule = None
    last_run_timestamp: str = None
    next_run_timestamp: str = None
    errors: list = None
    logs: list = None



@dataclass
class WeavDataSource:
    user_id: str = None
    workspace_id: str = None
    connector_id: str = None
    destination_id: str = None
    artifact_id: str = None
    connector_name: str = None
    user_defined_name: str = None
    auth_method: str = None
    auth_token: str = None
    token_expiry_time: str = None
    project_id: str = None
    password: str = None
    api_key: str = None
    connection_configurations: dict = None
    schedule: Schedule = None
    catalog: dict =None
    transformation_dag: str = None


@dataclass
class WorkspaceData:
    name: str = None
    email: str = None
    anonymous_data_collection: bool = False
    news: bool = False
    security_updates: bool = False
    notifications: list = None
    workspace_id: str = None


@dataclass
class DataService(UniqueItem):
    dataset_id: str = None
    version_id: str = None

@dataclass
class BackendService(UniqueItem):
    service: str = None

@dataclass
class StreamPreview:
    connection_id: str = None
    stream_name: str = None
