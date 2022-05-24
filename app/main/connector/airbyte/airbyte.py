import copy
import dataclasses
import datetime
import json
import pandas as pd
import base64
from urllib.parse import urlparse
import uuid
from os import environ, path
import os
import shutil
# from urllib.parse import urlparse

from dacite import from_dict
from dataclasses import asdict
import requests
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
import app.main.common.constants as constants
from app.main.common.ds import (
    DataIngestionSchema,
    DataService,
    DataSource,
    IngestionExecution,
    IngestionRule,
    IngestionStream,
    Schedule,
    UniqueItem,
    WeavDataSource,
    BackendService,
    get_request_json_as_dataclass,
)
from app.main.common.rest import (
    AirbyteError,
    RestManager,
    DataserviceException,
    ThreadWithReturnValue,
    ConfigException,
    ConnectionException,
    IntrospectionException,
    MongoException
)
from flask import current_app

class AirbyteIngestor:
    def __init__(
        self,
        airbyte_host=environ.get(
            constants.AIRBYTE_HOST, constants.AB_LOCALHOST),
        airbyte_api_version=environ.get(
            constants.AIRBYTE_API_VERSION, constants.AB_LOCAL_API_VERSION),
        **kwargs,
    ):
        self.endpoint = airbyte_host.strip("/")
        self.api_version = airbyte_api_version
        self.airbyte_web_host = environ.get(
            constants.AIRBYTE_WEB_HOST, constants.AB_LOCALHOST)
        self.weav_data_service = environ.get(constants.WEAV_DATA_SERVICE)
        self.weav_dataflow_service = environ.get(constants.WEAV_DATAFLOW_SERVICE)
        self.introspection_host = environ.get(
            constants.INTROSPECTION_HOST, constants.INTROSPECTION_LOCALHOST)
        self.excel_ext = constants.EXCEL_LIST
        # TODO: pick it up from .env

    # Creating global mongoclient
    client = MongoClient(
            # host=[constants.MONGOLOCALHOST],
            host=[environ.get(constants.MONGODBHOST)],
            serverSelectionTimeoutMS=constants.MONGOSERTOUT,  # 3second timeout
            username=environ.get(constants.MONGOUSER),
            password=environ.get(constants.MONGOPASSWORD),
        )

    def get_destination_definitions_list(self):
        """This function will list out the destination definitions.
        Returns:
            dataclass: This will return the list of destination definitions
            in post response.
        """
        return self.post_response(
            method_family=constants.DESTINATION_DEFINITIONS,
            method_name=constants.LIST
        ).json[constants.AIRBYTE_DESTINATION_DEFINITIONS]

    def get_source_definitions_list(self):
        """This function will list out the source definitions.
        Returns:
            dataclass: This will return
            the list of source definitions in post response.
        """
        return self.post_response(
            method_family=constants.SOURCE_DEFINITIONS,
            method_name=constants.LIST
        ).json[constants.AIRBYTE_SOURCE_DEFINITIONS]

    def slug_name(self, name: str):
        """This function will be responsible for giving slug name.
        Args:
            name (str): slug name.
        Returns:
            str: This will return slug name.
        """
        return "-".join(name.strip().lower().split())

    def get_workspace_by_slug(self, name):
        """Finding the workspace by using slug.
        Args:
            name (str): slug name.
        Returns:
            dict: It will post the workspace response.
        """
        return self.post_response(
            constants.WORKSPACES,
            constants.GET_BY_SLUG, data={constants.SLUG: name}
        ).json

    def create_workspace(
        self,
        name,
        email=None,
        anonymous_data_collection=False,
        news=False,
        security_updates=False,
        notifications=None,
    ):
        """This function will create a workspace by using some fields.
        Args:
            name (str): name of the workspace
            email (Email, optional): Defaults to None.
            anonymous_data_collection (bool, optional): Defaults to False.
            news (bool, optional): Defaults to False.
            security_updates (bool, optional): Defaults to False.
            notifications (str, optional): Defaults to None.
        Returns:
            dict: This will post the workspace response in dict
        """
        if notifications is None:
            notifications = []
        response = self.post_response(
            constants.WORKSPACES,
            constants.CREATE,
            data={
                constants.AIRBYTE_EMAIL: email,
                constants.AB_ANONY_DATA_COLL: anonymous_data_collection,
                constants.AIRBYTE_NAME: name,
                constants.AIRBYTE_NEWS: news,
                constants.AIRBYTE_SECURITY_UPDATES: security_updates,
                constants.AIRBYTE_NOTIFICATIONS: notifications,
            },
        )
        if response.status_code == 409:
            return self.get_workspace_by_slug(self.slug_name(name))
        return response.json

    def check_dictionary_item(self, response, item):
        """This funcition will gives the response of get request
        only if item is present in response dictionary. Otherwise
        gives None.
        Args:
            response (dict): the JSON response.
            item (str): fields inside the response.
        Returns:
            str: It will return the dict of item in response.
        """
        if item in response.keys():
            ret_item = response[item]
        else:
            ret_item = None
        return ret_item

    def get_url(self, method_family: str, method_name: str = None):
        """This function will convert method family and method name into WEAV URL.
        Args:
            method_family (str): This is the method family of WEAV endpoint.
            method_name (str, optional):
            This is the method name of WEAV endpoint.
            Defaults to None.
        Returns:
            str: This will return URL string.
        """
        if method_name is not None:
            return (
                f"{self.endpoint}/api/{self.api_version}" +
                f"/{method_family}/{method_name}"
            )
        else:
            return f"{self.endpoint}/api/{self.api_version}/{method_family}"

    def post_response(
        self,
        method_family: str,
        method_name: str = None,
        data: dict = None,
        headers: dict = None,
    ):
        """This funcition will gives the response of post request.
        Args:
            method_family (str): This is the method family of WEAV endpoint.
            method_name (str, optional):
            This is the method name of WEAV endpoint.
            Defaults to None.
            data (dict, optional):
            It is a Payload dictionary. Defaults to None.
            headers (dict, optional): It is the header of post request.
            Defaults to None.
        Returns:
            dataclass: This will return dataclass of post response.
        """
        url = self.get_url(method_family, method_name)
        response = RestManager.post(url=url, data=data, headers=headers)
        return response

    def get_connection_by_type(
        self, data_source: DataSource, type=constants.SOURCE, conf_data=None
    ):
        """This function will get the required connection parameters depending on
            the type of the connector we are creating.
        Args:
            data_source (DataSource): This is coming from dataclass
            type (str, optional):
            Name of the connector type. Defaults to source.
        Returns:
            dict: It will return connection configuration
            dictionary which has all the
                  required connection parameters to
                  create source/destination connector.
        """
        connector_id = self.get_connector_definition_id(data_source, type=type)
        if type == constants.SOURCE:
            response = self.post_response(
                method_family=constants.AB_SRC_DEF_SPEC,
                method_name=constants.GET,
                data={constants.AIRBYTE_SOURCE_DEFINITION_ID: connector_id},
            )
        else:
            response = self.post_response(
                method_family=constants.AB_DEST_DEF_SPEC,
                method_name=constants.GET,
                data={constants.AB_DEST_DEF_ID: connector_id},
            )
        # storing the required fields in connection_spec
        connection_spec = response.json[constants.AB_CONN_SPEC]
        connection_configuration_dictionary = {}
        # storing the value for each field
        # in connection configuration dictionary.
        for spec_field in connection_spec[constants.PROPERTIES].keys():
            value = None
            if spec_field not in data_source.connection_configurations.keys():
                field_spec = connection_spec[constants.PROPERTIES][spec_field]
                if field_spec[constants.TYPE] == constants.STRING:
                    value = field_spec.get(constants.DEFAULT, "")
                elif field_spec[constants.TYPE] == constants.FLOAT:
                    value = field_spec.get(constants.DEFAULT, 0.0)
                elif field_spec[constants.TYPE] == constants.INTEGER:
                    value = field_spec.get(constants.DEFAULT, 0)
                elif field_spec[constants.TYPE] == constants.OBJECT:
                    value = field_spec.get(constants.DEFAULT, {})
                elif field_spec[constants.TYPE] == constants.ARRAY:
                    value = field_spec.get(constants.DEFAULT, [])
                elif field_spec[constants.TYPE] == constants.BOOL:
                    value = field_spec.get(constants.DEFAULT, "False")
                connection_configuration_dictionary[spec_field] = value
            else:
                connection_configuration_dictionary[
                    spec_field
                ] = data_source.connection_configurations[spec_field]
        return connection_configuration_dictionary

    def get_schedule_by_type(self, data_source, schedule):
        """This function will create a schedule for sync.
        Args:
            data_source (DataSource): It is coming from dataclass.
            schedule (Schedule): minutes┃hours┃days┃weeks┃months.
        Returns:
            dict: It will retrun schedule depending on the fields.
        """
        schedule_by_type = {}
        if dataclasses.is_dataclass(schedule):
            schedule = dataclasses.asdict(schedule)
        minutes = schedule[constants.MINUTES]
        hours = schedule[constants.HOURS]
        days = schedule[constants.DAYS]
        weeks = schedule[constants.WEEKS]
        months = schedule[constants.MONTHS]

        schedule_by_type = {
            constants.MINUTES: minutes,
            constants.HOURS: hours,
            constants.DAYS: days,
            constants.WEEKS: weeks,
            constants.MONTHS: months,
        }
        return schedule_by_type

    def format_schedule_by_library(self, data_source, schedule):
        """formatting the schedule into units and timeunit.
        Args:
            data_source (DataSource): It is coming from dataclass.
            schedule (Schedule): minutes┃hours┃days┃weeks┃months.
        Returns:
            dict: It will return the schedule with fields units and timeunit.
        """
        if dataclasses.is_dataclass(schedule):
            schedule = dataclasses.asdict(schedule)

        def check_dictionary_item_schedule(input_schedule, key=None):
            if key in input_schedule:
                response_schedule = {
                    constants.UNITS: input_schedule[key],
                    constants.TIME_UNIT: key,
                }
            return response_schedule

        input_sequence = [
            constants.MONTHS,
            constants.WEEKS,
            constants.DAYS,
            constants.HOURS,
            constants.MINUTES,
        ]
        for key in input_sequence:
            returned_value = check_dictionary_item_schedule(
                input_schedule=schedule, key=key
            )
            if returned_value[constants.UNITS]:
                return returned_value

    def reformat_schedule_by_library(self, data_source: DataSource, schedule: dict):
        """Reformatting schedule back to normal schedule.
        Args:
            data_source (DataSource): It is coming from dataclass.
            schedule (dict): units and timeunit.
        """

        def check_dictionary_item_schedule(input_schedule):
            schedule = Schedule()
            schedule = dataclasses.asdict(schedule)
            time_unit = input_schedule[constants.TIME_UNIT]
            unit = input_schedule[constants.UNITS]
            schedule[time_unit] = unit
            return schedule

        if schedule:
            return check_dictionary_item_schedule(input_schedule=schedule)

    def get_connector_definition_id(self,
                                    source: DataSource,
                                    type=constants.SOURCE):
        """This function will gives the source and destination definition id.
        Args:
            source (DataSource): It is coming for dataclass.
            type (str, optional):
            It is the type of the connector. Defaults to source".
        Returns:
            str: It will return source
            definition depending on their definitionId and
                 type.
        """
        connectors_mapping = dict()
        if type == constants.SOURCE:
            source_definitions = self.get_source_definitions_list()
            for source_definition in source_definitions:
                connectors_mapping[
                    source_definition[constants.AIRBYTE_NAME].lower()
                ] = source_definition
            source_definition = connectors_mapping.get(
                source.type.lower(),
                {
                    constants.AIRBYTE_SOURCE_DEFINITION_ID: None,
                },
            )
            return source_definition[constants.AIRBYTE_SOURCE_DEFINITION_ID]
        else:
            destination_definitions = self.get_destination_definitions_list()
            for destination_definition in destination_definitions:
                connectors_mapping[
                    destination_definition[constants.AIRBYTE_NAME].lower()
                ] = destination_definition
            destination_definition = connectors_mapping.get(
                source.type.lower(),
                {
                    constants.AB_DEST_DEF_ID: None,
                },
            )
            return destination_definition[constants.AB_DEST_DEF_ID]

    def get_workspace_id(self, source: DataSource) -> str:
        """This function will be useful for getting workspace Id from library args
           and creating new workspace id
        Args:
            source (DataSource): This is coming from dataclass
        Returns:
            str: It will return the workspace id
        """
        workspace_id = source.workspace_id
        if workspace_id is None:
            workspace = self.create_workspace(name=str(uuid.uuid4()))
            workspace_id = workspace[constants.AIRBYTE_WORKSPACE_ID]
        return workspace_id

    def get_airbyte_workspace_id(self):
        """Finding the workspace created by airbyte.
        Returns:
            dict: It will post the workspace response.
        """
        format(self.airbyte_web_host)
        response = requests.post("{}/api/v1/workspaces/list".format(
            self.airbyte_web_host))
        return response.json()['workspaces'][0]['workspaceId']

    def add_source(self, source: DataSource, *args, **kwargs) -> DataSource:
        """This function will create the source connector.
        Args:
            source (DataSource): DataSource that
            describes the source to be created.
        Raises:
            AirbyteError: If the status is not
            successful then this error will raise.
        Returns:
            DataSource: It wll return source connector response.
        """
        # it will have all the source and destination connectors definition.
        workspace_id = self.get_airbyte_workspace_id()
        # Name of of source connector for ex Jira or File etc.
        source_name = source.name
        # It will tells the required connection
        # parameters according to the connector
        # that we are creating
        connection_configuration = self.get_connection_by_type(
            data_source=source)

        # depending on the type of connector it will give us definition id.
        source_definition_id = self.get_connector_definition_id(
            source, type=constants.SOURCE
        )
        response = self.post_response(
            constants.SOURCES,
            constants.CREATE,
            data={
                constants.AIRBYTE_NAME: source_name,
                constants.AB_CONN_CONFIG: connection_configuration,
                constants.AIRBYTE_WORKSPACE_ID: workspace_id,
                constants.AIRBYTE_SOURCE_DEFINITION_ID: source_definition_id,
            },
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.CREATE_SOURCE_EXC_MESSAGE.format(
                    response.json["message"]
                ),
                object=connection_configuration,
                reason=response.reason,
                status_code=response.status_code
            )
        ret_source = copy.deepcopy(source)
        ret_source.id = self.check_dictionary_item(
            response.json, item=constants.AIRBYTE_SOURCE_ID
        )
        conf_data = response.json[constants.AB_CONN_CONFIG]
        ret_source.connection_configurations = conf_data
        ret_source.workspace_id = response.json[constants.AIRBYTE_WORKSPACE_ID]
        ret_source.name = response.json[constants.AIRBYTE_NAME]
        ret_source.type = response.json[constants.AIRBYTE_SOURCE_NAME].lower()
        ret_source.metadata = {
            constants.AIRBYTE_SOURCE_DEFINITION_ID: self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_SOURCE_DEFINITION_ID
            )
        }
        return ret_source

    def remove_source(self, source: DataSource, *args, **kwargs) -> DataSource:
        """This function will be responsible for deleting source connector.
        Args:
            source (DataSource): It describes the source to be deleted.
        Raises:
            AirbyteError: If we pass wrong sourceId
            and status i.e deleting is not
                          successful then this error will raise.
        Returns:
            DataSource: It will return the
            status depending on the source removal.
        """
        response = self.post_response(
            constants.SOURCES,
            constants.DELETE,
            data={constants.AIRBYTE_SOURCE_ID: source.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.DELETE_SOURCE_EXC_MESSAGE.format(
                    str(response.json())
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        if response.status_code == 204:
            return True

    def get_source(self, source: DataSource, *args, **kwargs) -> DataSource:
        """This function will be responsible for reading the source that we created.
        Args:
            source (DataSource): It describes the source to be viewed..
        Raises:
            AirbyteError: For suppose we are
            passing different sourceId then this
                          error will raise.
        Returns:
            DataSource: This will return the source connector that we created.
        """
        response = self.post_response(
            constants.SOURCES,
            constants.GET,
            data={constants.AIRBYTE_SOURCE_ID: source.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.GET_SOURCE_EXC_MESSAGE.format(
                    str(response.json())),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_source = copy.deepcopy(source)
        ret_source.id = self.check_dictionary_item(
            response.json, item=constants.AIRBYTE_SOURCE_ID
        )
        conf_data = response.json[constants.AB_CONN_CONFIG]
        ret_source.connection_configurations = conf_data
        ret_source.workspace_id = response.json[constants.AIRBYTE_WORKSPACE_ID]
        ret_source.name = response.json[constants.AIRBYTE_NAME]
        ret_source.type = response.json[constants.AIRBYTE_SOURCE_NAME].lower()
        ret_source.metadata = {
            constants.AIRBYTE_SOURCE_DEFINITION_ID: self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_SOURCE_DEFINITION_ID
            )
        }
        return ret_source

    def update_source(self, source: DataSource, *args, **kwargs) -> DataSource:
        """This  function will update the source connector that we created.
        Args:
            source (DataSource): It describes the source to be updated.
        Raises:
            AirbyteError: If the source
            connector is not available then this error
                          will raise.
        Returns:
            DataSource: It will return the updated source.
        """
        response_for_type = self.post_response(
            constants.SOURCES,
            constants.GET,
            data={constants.AIRBYTE_SOURCE_ID: source.id},
        )
        source.type = response_for_type.json[
            constants.AIRBYTE_SOURCE_NAME].lower()
        connection_configuration = self.get_connection_by_type(
            data_source=source)
        response = self.post_response(
            constants.SOURCES,
            constants.UPDATE,
            data={
                constants.AIRBYTE_SOURCE_ID: source.id,
                constants.AB_CONN_CONFIG: connection_configuration,
                constants.AIRBYTE_NAME: source.name,
            },
        )

        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.GET_SOURCE_EXC_MESSAGE.format(
                    str(response.json())),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_source = copy.deepcopy(source)
        ret_source.id = self.check_dictionary_item(
            response.json, item=constants.AIRBYTE_SOURCE_ID
        )
        conf_data = response.json[constants.AB_CONN_CONFIG]
        ret_source.connection_configurations = conf_data
        ret_source.workspace_id = response.json[constants.AIRBYTE_WORKSPACE_ID]
        ret_source.name = response.json[constants.AIRBYTE_NAME]
        ret_source.type = response.json[constants.AIRBYTE_SOURCE_NAME].lower()
        ret_source.metadata = {
            constants.AIRBYTE_SOURCE_DEFINITION_ID: self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_SOURCE_DEFINITION_ID
            )
        }
        return ret_source

    def add_destination(self, destination: DataSource, *args, **kwargs) -> DataSource:
        """This function will create the destination connector.
        Args:
            destination (DataSource):
            It describes the destination to be created.
        Raises:
            AirbyteError: This error will
            arise if we pass wrong fields while creating
                          destination connector.
        Returns:
            DataSource: This will return the destination connector.
        """
        workspace_id = self.get_airbyte_workspace_id()
        # name of the destination connector for ex postgres or local csv etc.
        destination_name = destination.name
        # get the required connection parametesr
        # depending on the the connector.
        connection_configuration = self.get_connection_by_type(
            data_source=destination, type=constants.DESTINATION
        )
        destination_definition_id = self.get_connector_definition_id(
            destination, type=constants.DESTINATION
        )
        response = self.post_response(
            constants.DESTINATIONS,
            constants.CREATE,
            data={
                constants.AIRBYTE_NAME: destination_name,
                constants.AB_CONN_CONFIG: connection_configuration,
                constants.AIRBYTE_WORKSPACE_ID: workspace_id,
                constants.AB_DEST_DEF_ID: destination_definition_id,
            },
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.CREATE_DESTINATION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_destination = copy.deepcopy(destination)
        ret_destination.id = self.check_dictionary_item(
            response.json, item=constants.AB_DEST_ID
        )
        conf_data = response.json[constants.AB_CONN_CONFIG]
        ret_destination.connection_configurations = conf_data
        ret_destination.workspace_id = response.json[
            constants.AIRBYTE_WORKSPACE_ID]
        ret_destination.name = response.json[constants.AIRBYTE_NAME]
        ret_destination.type = response.json[
            constants.AIRBYTE_DESTINATION_NAME].lower()
        ret_destination.metadata = {
            constants.AIRBYTE_SOURCE_DEFINITION_ID: self.check_dictionary_item(
                response.json, item=constants.AB_DEST_DEF_ID
            )
        }
        return ret_destination

    def remove_destination(
        self, destination: DataSource, *args, **kwargs
    ) -> DataSource:
        """This function will remove the destination connector.
        Args:
            destination (DataSource):
            It describes the destination to be deleted.
        Raises:
            AirbyteError: If we pass wrong
            destinationId then this error will arise.
        Returns:
            DataSource: This will return status
            is sussessfull if connector was deleted.
        """
        response = self.post_response(
            constants.DESTINATIONS,
            constants.DELETE,
            data={constants.AB_DEST_ID: destination.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.DELETE_DESTINATION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        if response.status_code == 204:
            return True

    def get_destination(self, destination: DataSource, *args, **kwargs) -> DataSource:
        """This function will be responsible for reading
        the created destination connector.
        Args:
            destination (DataSource): It describes the
            destination to be viewed.
        Raises:
            AirbyteError: It will raise the error, if
            we pass wrong destinationId.
        Returns:
            DataSource: This will return destination connector that we created.
        """
        response = self.post_response(
            constants.DESTINATIONS,
            constants.GET,
            data={constants.AB_DEST_ID: destination.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.GET_DESTINATION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_destination = copy.deepcopy(destination)
        ret_destination.id = self.check_dictionary_item(
            response.json, item=constants.AB_DEST_ID
        )
        conf_data = response.json[constants.AB_CONN_CONFIG]
        ret_destination.connection_configurations = conf_data
        ret_destination.workspace_id = response.json[
            constants.AIRBYTE_WORKSPACE_ID]
        ret_destination.name = response.json[constants.AIRBYTE_NAME]
        ret_destination.type = response.json[
            constants.AIRBYTE_DESTINATION_NAME].lower()
        ret_destination.metadata = {
            constants.AIRBYTE_SOURCE_DEFINITION_ID: self.check_dictionary_item(
                response.json, item=constants.AB_DEST_DEF_ID
            )
        }
        return ret_destination

    def update_destination(
        self, destination: DataSource, *args, **kwargs
    ) -> DataSource:
        """This function will be responsible for
        updating the destination connector we created.
        Args:
            destination (DataSource): It describes
            the destination to be updated.
        Raises:
            AirbyteError: It will raise the error,
            if we pass wrong destinationId.
        Returns:
            DataSource: This will return updated destination connector.
        """
        response_for_type = self.post_response(
            constants.DESTINATIONS,
            constants.GET,
            data={constants.AB_DEST_ID: destination.id},
        )
        destination.type = response_for_type.json[
            constants.AIRBYTE_DESTINATION_NAME
        ].lower()
        connection_configuration = self.get_connection_by_type(
            data_source=destination, type=constants.DESTINATION
        )
        response = self.post_response(
            constants.DESTINATIONS,
            constants.UPDATE,
            data={
                constants.AB_DEST_ID: destination.id,
                constants.AB_CONN_CONFIG: connection_configuration,
                constants.AIRBYTE_NAME: destination.name,
            },
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.GET_DESTINATION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_destination = copy.deepcopy(destination)
        ret_destination.id = self.check_dictionary_item(
            response.json, item=constants.AB_DEST_ID
        )
        conf_data = response.json[constants.AB_CONN_CONFIG]
        ret_destination.connection_configurations = conf_data
        ret_destination.workspace_id = response.json[
            constants.AIRBYTE_WORKSPACE_ID]
        ret_destination.name = response.json[constants.AIRBYTE_NAME]
        ret_destination.type = response.json[
            constants.AIRBYTE_DESTINATION_NAME].lower()
        ret_destination.metadata = {
            constants.AB_DEST_DEF_ID: self.check_dictionary_item(
                response.json, item=constants.AB_DEST_DEF_ID
            )
        }
        return ret_destination

    def add_ingestion_rule(
        self,
        source: DataSource,
        destination: DataSource,
        schema: DataIngestionSchema,
        schedule: Schedule,
        status: str,
        *args,
        **kwargs,
    ) -> IngestionRule:
        """Create a connection between source and destination.
        Args:
            source (DataSource): source connector.
            destination (DataSource): destination connector.
            schema (DataIngestionSchema): describes the available schema.
            schedule (Schedule): syncing data.
            status (str): active,inactive, deprecated.
        Returns:
            IngestionRule: It will return the connection rule.
        """
        # Depending on the sourceid airbyte will gives the source schema.
        if schema:
            ingestion_stream = IngestionStream(
                json_schema=schema
                )
            data_ingestion_schema = DataIngestionSchema(
                streams={constants.SYNC_CATALOG: ingestion_stream}
                )
        else:
            schema_response = self.post_response(
                constants.SOURCES,
                constants.DISCOVER_SCHEMA,
                data={constants.AIRBYTE_SOURCE_ID: source.id},
                )
            # Creating dataclass of ingestion schemas
            ingestion_stream = IngestionStream(
                json_schema=schema_response.json[constants.CATALOG]
            )
            # it will gives the available schema.
            data_ingestion_schema = DataIngestionSchema(
                streams={constants.SYNC_CATALOG: ingestion_stream}
            )
        # Calling request library for GET service of Airbyte Source
        # created earlier.
        source_response = self.post_response(
            constants.SOURCES,
            constants.GET,
            data={constants.AIRBYTE_SOURCE_ID: source.id},
        )
        source_json_response = source_response.json

        # passing the required fields to create source dataclass.
        source = DataSource(
            id=self.check_dictionary_item(
                source_json_response, item=constants.AIRBYTE_SOURCE_ID
            ),
            name=self.check_dictionary_item(
                source_json_response, item=constants.AIRBYTE_NAME
            ),
            type=self.check_dictionary_item(
                source_json_response, item=constants.AIRBYTE_SOURCE_NAME
            ),
            connection_configurations=self.check_dictionary_item(
                source_json_response, item=constants.AB_CONN_CONFIG
            ),
            workspace_id=self.check_dictionary_item(
                source_json_response, item=constants.AIRBYTE_WORKSPACE_ID
            ),
            metadata={
                constants.AIRBYTE_SOURCE_DEFINITION_ID:
                self.check_dictionary_item(
                    source_json_response,
                    item=constants.AIRBYTE_SOURCE_DEFINITION_ID
                )
            },
        )

        # Calling request library for GET service of Airbyte Destination
        # created earlier
        destination_response = self.post_response(
            constants.DESTINATIONS,
            constants.GET,
            data={constants.AB_DEST_ID: destination.id},
        )
        destination_json_response = destination_response.json
        destination = DataSource(
            id=self.check_dictionary_item(
                destination_json_response, item=constants.AB_DEST_ID
            ),
            name=self.check_dictionary_item(
                destination_json_response, item=constants.AIRBYTE_NAME
            ),
            type=self.check_dictionary_item(
                destination_json_response,
                item=constants.AIRBYTE_DESTINATION_NAME
            ),
            connection_configurations=self.check_dictionary_item(
                destination_json_response,
                item=constants.AB_CONN_CONFIG,
            ),
            workspace_id=self.check_dictionary_item(
                source_json_response, item=constants.AIRBYTE_WORKSPACE_ID
            ),
            metadata={
                constants.AB_DEST_DEF_ID: self.check_dictionary_item(
                    source_json_response,
                    item=constants.AB_DEST_DEF_ID,
                )
            },
        )
        # for syncing of the source and destination data.
        # it will schedule in the form of minutes, hours, days, months.
        schedule = self.get_schedule_by_type(source, schedule)
        # it will set the ingestion rule i.e source id, destination id etc.
        ingestion_rule = IngestionRule(
            source=source,
            destination=destination,
            schema=data_ingestion_schema,
            schedule=schedule,
            status=status,
        )
        return ingestion_rule

    def ingestion_rule(
        self, rule: IngestionRule, *args, **kwargs
    ) -> IngestionExecution:
        """This function will creates the ingestion execution.
        Args:
            rule (IngestionRule): source,
            destination, schema, schedule, status.
        Returns:
            IngestionExecution: It will return the rule,
            timestamp, status, error, logs.
        """
        ingestion_execution = {}
        ingestion_execution[constants.RULE] = rule
        for k, v in kwargs.items():
            ingestion_execution[k] = v
        ingestion_execution = from_dict(
            data_class=IngestionExecution, data=ingestion_execution
        )
        return ingestion_execution

    def start_ingestion(
        self, ingestion_execution: IngestionExecution
    ) -> IngestionExecution:
        """It will start the ingestion service.
        Args:
            ingestion_execution (IngestionExecution):
            It will describe the sourceId
            and destinationId.
        Raises:
            AirbyteError: It wll raise error if we pass wrong ids.
        Returns:
            IngestionExecution: It will return the ingestion service.s
        """
        # It will format the schedule into times, unit time.
        schedule = self.format_schedule_by_library(
            ingestion_execution.rule.source, ingestion_execution.rule.schedule
        )
        # creating the schema.
        catalog = {
            constants.SYNC_CATALOG: ingestion_execution.rule.schema.streams[
                constants.SYNC_CATALOG
            ].json_schema
        }
        # we have to post these fields to get the connection.
        response = self.post_response(
            constants.CONNECTIONS,
            constants.CREATE,
            data={
                constants.AIRBYTE_SOURCE_ID:
                ingestion_execution.rule.source.id,
                constants.AB_DEST_ID: ingestion_execution.rule.destination.id,
                constants.SYNC_CATALOG: catalog[constants.SYNC_CATALOG],
                constants.SCHEDULE: schedule,
                constants.STATUS: ingestion_execution.status,
            },
        )
        errors = []
        if self.check_dictionary_item(response.json, item=constants.MESSAGE):
            errors.append(response.json[constants.MESSAGE])
        logs = [response.reason]
        ingestion_execution.logs = logs
        ingestion_execution.errors = errors
        rule_schedule = ingestion_execution.rule.schedule
        months = {}
        if constants.MONTHS in rule_schedule.keys():
            months = {constants.MONTHS: rule_schedule[constants.MONTHS]}
            del rule_schedule[constants.MONTHS]
        last_run_timestamp = datetime.datetime.now()
        next_run_timestamp = last_run_timestamp + (
            datetime.timedelta(**rule_schedule) + relativedelta(**months)
        )
        sync_response_status = self.post_response(
            constants.WEB_BACKEND_CONNECTIONS,
            constants.GET,
            data={
                constants.AIRBYTE_WITH_REFRESHED_CATALOG: True,
                constants.AIRBYTE_CONNECTION_ID: self.check_dictionary_item(
                    response.json, item=constants.AIRBYTE_CONNECTION_ID
                ),
            },
        )
        # in this format we will get the connection.
        ingestion_execution = IngestionExecution(
            id=self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_CONNECTION_ID
            ),
            rule=ingestion_execution.rule,
            last_run_timestamp=last_run_timestamp.timestamp(),
            next_run_timestamp=next_run_timestamp.timestamp(),
            status=self.check_dictionary_item(
                sync_response_status.json,
                item=constants.AIRBYTE_LATEST_SYNC_JOB_STATUS),
            logs=logs,
            errors=errors,
            is_syncing=self.check_dictionary_item(
                sync_response_status.json, item=constants.AIRBYTE_IS_SYNCING
            ),
        )

        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.CREATE_CONNECTION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                object=ingestion_execution,
                reason=response.reason,
                status_code=response.status_code
            )
        return ingestion_execution

    def delete_ingestion(
        self, ingestion_execution: IngestionExecution
    ) -> IngestionExecution:
        """This function is responsible for deleting the connection.
        Args:
            ingestion_execution (IngestionExecution):
            connectionId of connection
                                                      we created.
        Raises:
            AirbyteError: This will
            raise the error if we pass wrong connectionId.
        Returns:
            IngestionExecution: If
            connection was deleted sussessfully then give
                                us the success response.
        """
        response = self.post_response(
            constants.CONNECTIONS,
            constants.DELETE,
            data={constants.AIRBYTE_CONNECTION_ID: ingestion_execution.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.DELETE_CONNECTION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        if response.status_code == 204:
            return True

    def get_status_of_ingestion(
        self, ingestion_execution: IngestionExecution
    ) -> IngestionExecution:
        """Getting the status of the ingestion.
        Args:
            ingestion_execution (IngestionExecution):
            It will describe the connectionId.
        Raises:
            AirbyteError: It will raise the error
            if we pass wrong connectionId.
        Returns:
            IngestionExecution: It will give the connection that we created.
        """
        response = self.post_response(
            constants.WEB_BACKEND_CONNECTIONS,
            constants.GET,
            data={constants.AIRBYTE_CONNECTION_ID: ingestion_execution.id},
        )
        errors = []
        if self.check_dictionary_item(response.json, item=constants.MESSAGE):
            errors.append(response.json[constants.MESSAGE])
        logs = [response.reason]
        ingestion_execution.logs = logs
        ingestion_execution.errors = errors
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.STATUS_CONNECTION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                object=ingestion_execution,
                reason=response.reason,
                status_code=response.status_code
            )
        source = DataSource(
            tags=None,
            metadata={
                constants.AIRBYTE_SOURCE_DEFINITION_ID:
                self.check_dictionary_item(
                    response.json[constants.SOURCE],
                    item=constants.AIRBYTE_SOURCE_DEFINITION_ID,
                )
            },
            id=self.check_dictionary_item(
                response.json, item=constants.SOURCE)[
                constants.AIRBYTE_SOURCE_ID
            ],
            name=self.check_dictionary_item(
                response.json, item=constants.SOURCE)[
                constants.AIRBYTE_NAME
            ],
            type=self.check_dictionary_item(
                response.json, item=constants.SOURCE)[
                constants.AIRBYTE_SOURCE_NAME
            ],
            connection_configurations=self.check_dictionary_item(
                response.json, item=constants.SOURCE
            )[constants.AB_CONN_CONFIG],
            workspace_id=self.check_dictionary_item(
                response.json, item=constants.SOURCE
            )[constants.AIRBYTE_WORKSPACE_ID],
        )
        destination = DataSource(
            tags=None,
            metadata={
                constants.AB_DEST_DEF_ID: self.check_dictionary_item(
                    response.json[constants.DESTINATION],
                    item=constants.AB_DEST_DEF_ID,
                )
            },
            id=self.check_dictionary_item(
                response.json, item=constants.DESTINATION)[
                constants.AB_DEST_ID
            ],
            name=self.check_dictionary_item(
                response.json, item=constants.DESTINATION)[
                constants.AIRBYTE_NAME
            ],
            type=self.check_dictionary_item(
                response.json, item=constants.DESTINATION)[
                constants.AIRBYTE_DESTINATION_NAME
            ],
            connection_configurations=self.check_dictionary_item(
                response.json, item=constants.DESTINATION
            )[constants.AB_CONN_CONFIG],
            workspace_id=self.check_dictionary_item(
                response.json, item=constants.SOURCE
            )[constants.AIRBYTE_WORKSPACE_ID],
        )
        # Modify schema
        # schema_response = self.post_response(
        #     constants.SOURCES,
        #     constants.DISCOVER_SCHEMA,
        #     data={constants.AIRBYTE_SOURCE_ID: source.id},
        # )
        # ingestion_stream = IngestionStream(
        #     json_schema=schema_response.json[constants.CATALOG]
        # )
        # data_ingestion_schema = DataIngestionSchema(
        #     streams={constants.SYNC_CATALOG: ingestion_stream}
        # )
        # schedule = self.reformat_schedule_by_library(
        #     data_source=source,
        #     schedule=self.check_dictionary_item(
        #         response.json, item=constants.SCHEDULE),
        # )
        rule = IngestionRule(
            id=self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_CONNECTION_ID
            ),
            source=source,
            destination=destination,
            # schema=data_ingestion_schema,
            # schedule=schedule,
            status=self.check_dictionary_item(
                response.json, item=constants.STATUS),
        )
        ingestion_execution = IngestionExecution(
            id=self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_CONNECTION_ID
            ),
            rule=rule,
            last_run_timestamp=ingestion_execution.last_run_timestamp,
            next_run_timestamp=ingestion_execution.next_run_timestamp,
            status=self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_LATEST_SYNC_JOB_STATUS
            ),
            logs=logs,
            errors=errors,
            is_syncing=self.check_dictionary_item(
                response.json, item=constants.AIRBYTE_IS_SYNCING
            ),
        )
        if ingestion_execution.status == constants.SUCCEEDED:
            jobs_response = self.post_response(
            constants.JOBS,
            constants.LIST,
            data={constants.CONFIG_ID: ingestion_execution.id, constants.CONFIG_TYPES: [constants.SYNC]},
            )
            records_synced = jobs_response.json[constants.JOBS][0][constants.ATTEMPTS][0][constants.RECORDS_SYNCED]
            ingestion_execution.records_synced = records_synced

            # get dataset_id
            db = self.client.ingestiondb
            collection = db.connectors
            connection_details = collection.find_one(
                {constants.CONNECTOR_ID: ingestion_execution.rule.source.id})
            if connection_details is not None:
                if "dataset_id" in connection_details.keys():
                    ingestion_execution.dataset_id = connection_details["dataset_id"]
        return ingestion_execution

    def trigger_ingestion(
        self, ingestion_execution: IngestionExecution
    ) -> IngestionExecution:
        """Sync a connection of ingestion service.
        Args:
            ingestion_execution (IngestionExecution):
            It will describe the connectionId.
        Raises:
            AirbyteError: It will raise the error
            if we pass the wrong connectionId.
        Returns:
            IngestionExecution: It will manually
            sync the connection of ingestion
                                service.
        """
        response = self.post_response(
            constants.CONNECTIONS,
            constants.SYNC,
            data={constants.AIRBYTE_CONNECTION_ID: ingestion_execution.id},
        )
        errors = []
        if self.check_dictionary_item(response.json, item=constants.MESSAGE):
            errors.append(response.json[constants.MESSAGE])
        ingestion_execution.errors = errors
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.CREATE_CONNECTION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                object=ingestion_execution,
                reason=response.reason,
                status_code=response.status_code
            )
        ingestion_execution.id = self.check_dictionary_item(
            response.json[constants.JOB], item=constants.CONFIG_ID
        )
        ingestion_execution.last_run_timestamp = self.check_dictionary_item(
            response.json[constants.JOB], item=constants.CREATED_AT
        )
        ingestion_execution.next_run_timestamp = self.check_dictionary_item(
            response.json[constants.JOB], item=constants.UPDATED_AT
        )
        ingestion_execution.tag = [
            self.check_dictionary_item(
                response.json[constants.JOB], item=constants.CONFIG_TYPE
            )
        ]
        ingestion_execution.status = self.check_dictionary_item(
            response.json[constants.JOB], item=constants.STATUS
        )
        ingestion_execution.is_syncing = (
            ingestion_execution.status != constants.SUCCEEDED
        )
        # attempt = ids presented in response of connection.
        attempts = []
        logs = [response.reason]
        for attempt in self.check_dictionary_item(
            response.json, item=constants.ATTEMPTS
        ):
            attempts.append(attempt[constants.ATTEMPT][constants.ID])
            logs.extend(attempt[constants.LOGS][constants.LOG_LINES])

        ingestion_execution.logs = logs
        ingestion_execution.metadata = {
            constants.ATTEMPTS: self.check_dictionary_item(
                response.json[constants.JOB], item=constants.ID
            ),
            constants.FAILED_ATTEMPTS: len(attempts) and len(attempts) - 1,
        }
        return ingestion_execution

    def ingestion_status(
        self, ingestion_execution: IngestionExecution
    ) -> IngestionExecution:
        """It will give the connection we created.
        Args:
            ingestion_execution (IngestionExecution):
            It will describe the connectionId.
        Raises:
            AirbyteError: It will raise the error
            if we pass the wrong connectionId.
        Returns:
            IngestionExecution: It will return
            the status of connection.
        """
        response = self.post_response(
            constants.STATE,
            constants.GET,
            data={constants.AIRBYTE_CONNECTION_ID: ingestion_execution.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.STATUS_CONNECTION_EXC_MESSAGE.format(
                    response.json()),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_source = copy.deepcopy(ingestion_execution)
        ret_source.id = self.check_dictionary_item(
            response.json, item=constants.AIRBYTE_CONNECTION_ID
        )
        ret_source.status = response.json[constants.STATE]
        return ret_source

    def list_ingestion(
        self, ingestion_execution: IngestionExecution
    ) -> IngestionExecution:
        """This will give us the all connections.
        Args:
            ingestion_execution (IngestionExecution):
            It will describe the workspaceId.
        Raises:
            AirbyteError: It will raise error if we pass wrong workspaceId.
        Returns:
            IngestionExecution: This will return all
            the connections presented in
            particular workspace.
        """
        response = self.post_response(
            constants.CONNECTIONS,
            constants.LIST,
            data={constants.AIRBYTE_WORKSPACE_ID: ingestion_execution.id},
        )
        if response.status_code >= 300:
            raise AirbyteError(
                message=constants.LIST_CONNECTION_EXC_MESSAGE.format(
                    str(response.json)
                ),
                reason=response.reason,
                status_code=response.status_code
            )
        ret_source = copy.deepcopy(ingestion_execution)
        ret_source.id = ingestion_execution.id
        return ret_source

    def get_file_name_and_ext(self, url: str):
        """Detect file_name and extention from url
        Args:
            url (str): url of source

        Returns:
            tuple: file_name and extention
        """
        url_parsed_data = urlparse(url)
        file_name = path.basename(url_parsed_data.path)
        file_ext = file_name.split('.')[-1]
        file_name = file_name.split('.')[0]
        if file_name == file_ext:
            file_ext = None
        return file_name, file_ext

    def filetype(self, url: str) -> str:
        """Get format for Airbyte

        Args:
            url (str): url of source

        Returns:
            str: extention as format
        """
        file_ext = self.get_file_name_and_ext(url)[1]
        if file_ext is not None:
            if file_ext == constants.CSV:
                return constants.CSV
            elif file_ext == constants.JSON:
                return constants.JSON
            elif file_ext == constants.JSONL:
                return constants.JSONL
            elif file_ext in self.excel_ext:
                return constants.EXCEL
            elif file_ext == constants.FEATHER:
                return constants.FEATHER
            elif file_ext == constants.PARQUET:
                return constants.PARQUET
            else:
                return constants.CSV_READS
        else:
            return None

    def check_connection(self, rule):
        """check source and destination

        Args:
            rule : source and destination configuration
        """
        def check_source(rule):
            url = constants.AB_CHECK_SRC.format(self.airbyte_web_host)
            payload = json.dumps({constants.AIRBYTE_SOURCE_ID: rule.source.id})
            headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
            response = requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
            )
            assert response.json()[constants.STATUS] == constants.SUCCEEDED,response.json()[constants.MESSAGE]

        def check_destination(rule):
            url = constants.AB_CHECK_DEST.format(self.airbyte_web_host)
            payload = json.dumps({constants.AB_DEST_ID: rule.destination.id})
            headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
            response = requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
            )
            assert response.json()[constants.STATUS] == constants.SUCCEEDED,response.json()[constants.MESSAGE]
        try:
            check_source(rule)
            check_destination(rule)

        except Exception as e:
            if rule.source.type == constants.FILE:
                del rule.source.connection_configurations[constants.READER_OPTIONS]
                del rule.source.connection_configurations[constants.AIRBYTE_FORMAT]
                error_msg = constants.CHECK_CONNECTION_FAILED_MSG.format(str(e)[0:str(e).find(": ")])
            elif rule.source.type in ["mongodb","mysql","postgres","slack"]:
                error_msg=str(e)
            elif rule.source.type in ["jira","salesforce"]:
                error_msg=constants.CHECK_CONNECTION_FAILED_MSG.format(str(e))
            else:
                error_msg = str(e)

            # Removing failed connectors from airbyte.  
            self.remove_connector(WeavDataSource(connector_id = rule.source.id))
            self.remove_destination(rule.destination)
            raise AirbyteError(
                message=error_msg,
                status_code=422, #Connector validation Error
                object=rule.source.connection_configurations
            )

    def add_connector(
        self, weav_source: WeavDataSource, *args, **kwargs
    ) -> WeavDataSource:
        """Create connector for source or destination using Airbyte Api

        Args:
            weav_source (WeavDataSource): WeavDataSource object
            describes the connector to be added

        Returns:
            WeavDataSource: WeavDataSource object with Unique connector_id
        """
        type = weav_source.connector_name.lower()
        connection_configurations = weav_source.connection_configurations

        # Sending Hardcoded configuration(reader_option and provider)
        # for "File" connector
        if type == constants.FILE:
            url = str(connection_configurations[constants.URL])
            ret_config_dict = {constants.URL:url,
                        constants.DATASET_NAME:None,
                        constants.AIRBYTE_FORMAT:None,
                        constants.READER_OPTIONS:None}
            filename_ext_tup = self.get_file_name_and_ext(url)
            file_type = self.filetype(url)
            if file_type in [constants.EXCEL,constants.FEATHER,constants.PARQUET]:
                connection_configurations[constants.AIRBYTE_FORMAT] = file_type
            if connection_configurations.get(constants.DATASET_NAME) is None:
                # dataset name detection check
                dataset_name = filename_ext_tup[0] #Ask user to confirm the name else provide
                ret_config_dict[constants.DATASET_NAME]=dataset_name

                if dataset_name is None:
                    raise ConfigException(
                        data = ret_config_dict,
                        message=constants.DATASET_NAME_NOT_DETECTED
                    )
                connection_configurations[constants.DATASET_NAME] = dataset_name
                user_in_dataset_name = False
            else:
                dataset_name = connection_configurations[constants.DATASET_NAME]
                user_in_dataset_name = True
                ret_config_dict[constants.DATASET_NAME] = dataset_name


            if connection_configurations.get(constants.AIRBYTE_FORMAT) is None:
                # Format detection checks
                file_format = constants.CSV
                ret_config_dict[constants.AIRBYTE_FORMAT]=file_format

                if file_format is None:
                    raise ConfigException(
                        data = ret_config_dict,
                        message=constants.FORMAT_NOT_DETECTED
                    )
                connection_configurations[constants.AIRBYTE_FORMAT] = file_format
                user_in_format = False
            else:
                file_format = connection_configurations[constants.AIRBYTE_FORMAT]
                user_in_format = True
                ret_config_dict[constants.AIRBYTE_FORMAT] = file_format

            if connection_configurations[constants.AIRBYTE_FORMAT] in [constants.CSV, constants.EXCEL]:
                if connection_configurations[constants.AIRBYTE_FORMAT] == constants.CSV:
                    reader_opt = constants.DEF_READER_OPT
                if connection_configurations[constants.AIRBYTE_FORMAT] == constants.EXCEL:
                    reader_opt = constants.DEF_READER_OPT_EXCEL
                if connection_configurations.get(constants.READER_OPTIONS) is None:
                    read_flag = False
                    # setting reader_options to pull sample data
                    connection_configurations[constants.READER_OPTIONS] = reader_opt
                    ret_config_dict[constants.READER_OPTIONS] = reader_opt         
                else:
                    read_flag = True
            connection_configurations[constants.PROVIDER] = {constants.STORAGE: constants.HTTPS}
            transformation_dag = filename_ext_tup[1]
        else:
            transformation_dag = type

        name = weav_source.user_defined_name
        workspace_id = weav_source.workspace_id
        source = DataSource(
            type=type,
            connection_configurations=connection_configurations,
            name=name,
            workspace_id=workspace_id,
        )

        # Add connector errors -- AirbyteError
        connector = self.add_source(source)
        ret_source = copy.deepcopy(weav_source)
        ret_source.connector_id = connector.id
        ret_source.workspace_id = connector.workspace_id
        ret_source.transformation_dag = transformation_dag
        # Creating destination
        name = constants.AB_CUST_DEST + "_" + weav_source.project_id
        data = {
            constants.TYPE: constants.AB_CUST_DEST,
            constants.NAME: name,
            constants.CONNECTION_CONFIGURATIONS: {
                constants.AIRBYTE_CUSTOM_OUTPUT_DIRECTORY: "{}/{}".format(
                    constants.LIBRARY_NAME, weav_source.project_id
                )
            },
            constants.WORKSPACE_ID: weav_source.workspace_id,
        }
        destination = get_request_json_as_dataclass(DataSource, data)

        # Add destination errors -- AirbyteError
        destination = self.add_destination(destination)
        custom_destination_id = destination.id
        ret_source.destination_id = custom_destination_id
        if weav_source.schedule is None:
            weav_source.schedule = Schedule()
        data = {
                constants.SOURCE: {constants.ID: ret_source.connector_id,
                constants.TYPE: type,
                constants.CONNECTION_CONFIGURATIONS: connection_configurations},
                constants.DESTINATION: {constants.ID: custom_destination_id},
                constants.SCHEDULE: weav_source.schedule,
                constants.STATUS: constants.ACTIVE,
            }
        rule = get_request_json_as_dataclass(IngestionRule, data)
        # testing source and destination for given config
        self.check_connection(rule)
        type = weav_source.connector_name.lower()
        sample_file_path = None
        if type == constants.FILE and\
            connection_configurations[constants.AIRBYTE_FORMAT] in [constants.CSV, constants.EXCEL] and\
                read_flag == False:
            rule = self.add_ingestion_rule(
                    source=rule.source,
                    destination=rule.destination,
                    schema=rule.schema,
                    schedule=rule.schedule,
                    status=rule.status,
                    )
            ingestion_execution = self.ingestion_rule(rule, status=rule.status)
            ingestion_execution = self.start_ingestion(ingestion_execution)
            self.trigger_ingestion(ingestion_execution)

            if self.check_synching(ingestion_execution):
                # #Docker
                path = constants.WEAV_DATA_AB_PATH.format(
                    weav_source.project_id)
                raw_data = pd.read_csv(path)
                if filename_ext_tup[1] is None:
                    new_file = constants.WEAV_DATA_ING_PATH.format(
                        connection_configurations[constants.DATASET_NAME],file_format)
                else:
                    new_file = constants.WEAV_DATA_ING_PATH.format(
                        connection_configurations[constants.DATASET_NAME],filename_ext_tup[1])
                
                # LOCAL-Reforming Original file
                # path = "/tmp/airbyte_local/airbyte/{}/default.csv".format(
                #     weav_source.project_id)
                # raw_data = pd.read_csv(path)
                # if filename_ext_tup[1] is None:
                #     new_file = "/home/sheshan/Downloads/Original/{}.{}".format(
                #         connection_configurations["dataset_name"],file_format)
                # else:
                #     new_file = "/home/sheshan/Downloads/Original/{}.{}".format(
                #         connection_configurations["dataset_name"],filename_ext_tup[1])

                if connection_configurations[constants.AIRBYTE_FORMAT] == constants.EXCEL:
                    data = [json.loads(text) for text in list(raw_data["data"])]
                    data = pd.json_normalize(data)
                    new_file = data.to_csv(new_file)
                    fileformat = constants.EXCEL
                    # Delete old reader_option configuration
                    connection_configurations = ret_source.connection_configurations
                    del connection_configurations[constants.READER_OPTIONS]
                elif connection_configurations[constants.AIRBYTE_FORMAT] == constants.CSV:
                    with open(new_file, 'w') as f:
                        for line in raw_data["data"]:
                            lt = json.loads(line)["LineData"]
                            if lt is None:
                                f.write('\n')
                            else:
                                f.write(lt+'\n')

                    reader_options = connection_configurations[constants.READER_OPTIONS]
                    new_reader_options = json.loads(reader_options)
                    path = new_file
                    config = {constants.CONNECTOR_ID: ret_source.connector_id}
                    inspect_data = self.call_inspect(path,config)
                    #TODO delete the recreated sample file after preview functionality setup.
                    if inspect_data[constants.FILE_FORMAT] == constants.CSV:
                        if inspect_data[constants.DELIMETER] is not constants.NOT_APPL:
                            sep = inspect_data[constants.DELIMETER]
                        else:
                            sep = None
                        fileformat = constants.CSV
                        if sep:
                            new_reader_options[constants.SEP] = sep
                        # Delete old reader_option configuration
                        del new_reader_options[constants.NROWS]
                        del new_reader_options[constants.NAMES]
                        # Getting header list using file_descriptor json for bio conll ann
                        # Get from mongodb
                        db = self.client.introspectiondb
                        collection = db.file_descriptors
                        ret_value = collection.find_one(
                            {constants.EXTENSION: inspect_data[constants.EXTENSION]}
                            )
                        if ret_value:
                            if ret_value[constants.DISCRIPTOR_COL_NAMES] is not None:
                                new_reader_options[constants.NAMES] = ret_value[constants.DISCRIPTOR_COL_NAMES]
                        # Setting quoting option None for bio and conll format.
                        # This parameter is needed for proper ingestion of these files.
                        if inspect_data[constants.EXTENSION] in [constants.BIO,constants.CONLL]:
                            new_reader_options[constants.QUOTING] = 3
                        connection_configurations = ret_source.connection_configurations
                        connection_configurations[constants.READER_OPTIONS] = json.dumps(new_reader_options)
                    elif inspect_data[constants.FILE_FORMAT] in [constants.JSON,constants.JSONL]:
                        fileformat = inspect_data[constants.FILE_FORMAT]
                        # Delete old reader_option configuration
                        connection_configurations = ret_source.connection_configurations
                        del connection_configurations[constants.READER_OPTIONS]
                    else:
                        fileformat = None
                        # Delete old reader_option configuration
                        connection_configurations = ret_source.connection_configurations
                        del connection_configurations[constants.READER_OPTIONS]
                new_weav_source = ret_source
                if fileformat:
                    connection_configurations[constants.AIRBYTE_FORMAT] = fileformat
                new_weav_source.connection_configurations = connection_configurations
                self.update_connector(new_weav_source)
                sample_file_path = new_file
            else:
                del connection_configurations[constants.READER_OPTIONS]
                connection_configurations[constants.AIRBYTE_FORMAT] = ["csv","excel","jsonl","json","parquet","feather"]

                # Removing failed connectors from airbyte.
                self.remove_connector(WeavDataSource(connector_id = rule.source.id))
                self.remove_destination(rule.destination)
                raise ConnectionException(
                    status=constants.FAILED,
                    data=connection_configurations,
                    message=constants.SAMPLE_DOWNLOAD_EXCEPTION_MSG
                )
            self.delete_ingestion(ingestion_execution)
            success_msg = constants.FILE_CSV_CONNECTOR_SUCCESS_MSG
        else:
            success_msg = constants.OTHER_CONNECTOR_SUCCESS_MSG
        
        preview_string = None
        if type == constants.FILE and \
            connection_configurations[constants.AIRBYTE_FORMAT] in constants.PREVIEW_FORMATS:
            # #Docker
            if filename_ext_tup[1] is None:
                new_file = constants.WEAV_DATA_ING_PATH.format(
                    weav_source.connection_configurations[constants.DATASET_NAME],file_format)
            else:
                new_file = constants.WEAV_DATA_ING_PATH.format(
                    weav_source.connection_configurations[constants.DATASET_NAME],filename_ext_tup[1])

            # #Local 
            # if filename_ext_tup[0] == filename_ext_tup[1]:
            #     new_file = "/home/sheshan/Downloads/Original/{}.{}".format(
            #         weav_source.connection_configurations["dataset_name"],file_format)
            # else:
            #     new_file = "/home/sheshan/Downloads/Original/{}.{}".format(
            #         weav_source.connection_configurations["dataset_name"],filename_ext_tup[1])

            path = new_file
            file_preview_obj = self.call_file_preview(path, connection_configurations)
            preview_string = file_preview_obj.text
            # print(file_preview_obj.text)
            # decoded = base64.b64decode(file_preview_obj.text)
            # data = decoded.decode("utf-8")
            # print(data)

        # saving in database
        # Working with Mongodb
        try:
            db = self.client.ingestiondb
            collection = db.connectors
            collection.insert_one(asdict(ret_source))
        except Exception as e:
            raise MongoException(message = constants.MONGODB_ERROR_MSG.format(str(e)))

        return UniqueItem(
            connector_id=ret_source.connector_id,
            connection_configurations=connection_configurations,
            destination_id=ret_source.destination_id,
            sample_path = sample_file_path,
            sample_preview=preview_string,
            message=success_msg
            )

    def call_inspect(self, path,config):
        """Calling inspect api of introspection service to detect delimeter and format

        Args:
            path ([type]): sample file path
            config ([type]): default config
        Returns:
            [type]: inspection object with delimeter and format.
        """
        url = constants.INSPECT_URL.format(self.introspection_host)
        # url = constants.INSPECT_URL.format("http://localhost:7009")
        payload = json.dumps({constants.PATH: path, constants.CONFIG: config})
        headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
        try:
            response = requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
                )
        except requests.exceptions.RequestException as e:
            raise IntrospectionException(
                message=constants.INTROSPECTION_ERROR_MSG + str(e)
            )
        if response.status_code >= 300:
            raise IntrospectionException(
                message=constants.INTROSPECTION_ERROR_MSG + response.text,
                status_code=response.status_code
                )
        return response.json()[constants.DATA]
    
    def call_file_preview(self, path, config):
        """Calling preview api of introspection service to get preview encoded string

        Args:
            path ([type]): sample file path
            config ([type]): default config
        Returns:
            [type]: raw base64 and 'utf-8' encoded string
        """
        url = constants.FILE_PREVIEW_URL.format(self.introspection_host)
        # url = constants.FILE_PREVIEW_URL.format("http://localhost:7009")
        payload = json.dumps({constants.PATH: path, constants.CONFIG: config})
        headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
        try:
            response = requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
                )
        except requests.exceptions.RequestException as e:
            raise IntrospectionException(
                message=constants.INTROSPECTION_ERROR_MSG + str(e)
            )
        if response.status_code >= 300:
            raise IntrospectionException(
                message=constants.INTROSPECTION_ERROR_MSG + response.text,
                status_code=response.status_code
                )
        return response


    def update_connector(
        self, weav_source: WeavDataSource, *args, **kwargs
    ) -> WeavDataSource:
        """Update connector for source or destination using Airbyte Api

        Args:
            weav_source (WeavDataSource): WeavDataSource object
            describes the connector to be Updated

        Returns:
            WeavDataSource: WeavDataSource object with Unique connector_id
        """
        connection_configurations = weav_source.connection_configurations
        name = weav_source.user_defined_name
        connector_id = weav_source.connector_id
        source = DataSource(
            id=connector_id,
            connection_configurations=connection_configurations,
            name=name
        )
        # Update in Airbyte
        self.update_source(source)
        data_dict = {}
        # redefining returned dictionary with only keys which have any values
        # i.e. removing items with empty values.
        for k, v in asdict(weav_source).items():
            if v:
                data_dict[k] = v
        # Update in Weav DB
        try:
            db = self.client.ingestiondb
            collection = db.connectors
            collection.update_one(
                {constants.CONNECTOR_ID: connector_id},
                {"$set": data_dict}
                )
        except Exception as e:
            raise MongoException(message = constants.MONGODB_ERROR_MSG.format(str(e)))

        return UniqueItem(connector_id=connector_id)

    def get_connector(
        self, weav_source: WeavDataSource, *args, **kwargs
    ) -> WeavDataSource:
        """View connector for source or destination using Airbyte Api

        Args:
            weav_source (WeavDataSource): WeavDataSource object
            describes the connector to be Viewed

        Returns:
            WeavDataSource: WeavDataSource object with all the
            information for the connector
        """
        source = DataSource(id=weav_source.connector_id)
        connector = self.get_source(source)

        connector_id = weav_source.connector_id
        # Get from mongodb
        db = self.client.ingestiondb
        collection = db.connectors
        ret_value = collection.find_one(
            {constants.CONNECTOR_ID: connector_id}
            )
        data_dict = {}
        if ret_value:
            del ret_value[constants.COL_ID]
            for k, v in ret_value.items():
                if v:
                    data_dict[k] = v
            ret_val = get_request_json_as_dataclass(WeavDataSource, data_dict)
            return ret_val
        else:
            raise Exception(constants.NO_RECORD)

    def remove_connector(
        self, weav_source: WeavDataSource, *args, **kwargs
    ) -> WeavDataSource:
        """Delete connector for source or destination using Airbyte Api

        Args:
            weav_source (WeavDataSource): WeavDataSource object
            describes the connector to be Deleted

        Returns:
            WeavDataSource: WeavDataSource
            object with connector_id that was deleted
        """
        id = weav_source.connector_id
        source = DataSource(
            id=id,
        )
        connector = self.remove_source(source)
        ret_source = copy.deepcopy(weav_source)
        return_object = connector
        return_object = UniqueItem(id=ret_source.connector_id)
        return return_object

    def get_schema(self, weav_source: WeavDataSource, *args, **kwargs) -> IngestionStream:
        schema_response = self.post_response(
            constants.SOURCES,
            constants.DISCOVER_SCHEMA,
            data={constants.AIRBYTE_SOURCE_ID: weav_source.connector_id},
        )
        ingestion_stream = IngestionStream(
            json_schema=schema_response.json[constants.CATALOG]
        )
        weav_source_copy = self.get_connector(weav_source)
        return {
            constants.STREAMS: ingestion_stream.json_schema,
            constants.MESSAGE : constants.DISCOVER_SCHEMA_MSG.format(weav_source_copy.connector_name)}

    def add_connection(
        self, weav_source: WeavDataSource, *args, **kwargs
    ) -> WeavDataSource:
        """This function is used to create connection and call data service

        Args:
            weav_source (WeavDataSource): dataclass of weav data source

        Returns:
            WeavDataSource: dataclass of weav data source after
            connection creation
        """
        # using threading for keep execution
        # running after returning the connection_id
        # t1 gets connection details
        # t2 calls data service after t1 results are returned

        weav_source_copy = copy.deepcopy(weav_source)
        weav_source_copy = self.get_connector(weav_source_copy)
        weav_source_copy.catalog = weav_source.catalog
        if weav_source_copy.artifact_id is None:
            weav_source_copy.artifact_id = weav_source.artifact_id

        custom_destination_id = weav_source_copy.destination_id
        if weav_source.schedule:
            schedule_flag = False
            weav_source_copy.schedule = weav_source.schedule
        if weav_source_copy.schedule is None:
            schedule_flag = True
            weav_source_copy.schedule = Schedule()

        data = {
            constants.SOURCE: {constants.ID: weav_source.connector_id},
            constants.DESTINATION: {constants.ID: custom_destination_id},
            constants.SCHEDULE: dataclasses.asdict(weav_source_copy.schedule),
            constants.STATUS: constants.ACTIVE,
        }
        rule = get_request_json_as_dataclass(IngestionRule, data)
        t1 = ThreadWithReturnValue(
            target=self.add_conn_ui_response, args=(weav_source_copy, rule, schedule_flag))
        t1.start()
        ingestion_execution = t1.join()
        return {
            constants.MESSAGE: "Ingestion started for " +
            f"{weav_source_copy.user_defined_name}",
            constants.CONNECTION_ID: ingestion_execution.id
        }

    def add_conn_ui_response(
            self,
            weav_source: WeavDataSource, rule, schedule_flag) -> IngestionExecution:
        """This function is to create connection

        Args:
            weav_source (WeavDataSource): [description]

        Returns:
            IngestionExecution: [description]
        """
        self.check_connection(rule)

        rule = self.add_ingestion_rule(
            source=rule.source,
            destination=rule.destination,
            schema=weav_source.catalog,
            schedule=rule.schedule,
            status=rule.status,
        )
        ingestion_execution = self.ingestion_rule(rule, status=rule.status)
        ingestion_execution = self.start_ingestion(ingestion_execution)
        if schedule_flag:
            self.trigger_ingestion(ingestion_execution)

        t2 = ThreadWithReturnValue(
            target=self.add_conn_call_data_service, args=(
                ingestion_execution, weav_source,))
        t2.start()

        # Storing connection_id in mongodb collection
        db = self.client.ingestiondb
        collection = db.connectors
        collection.update_one(
            {constants.CONNECTOR_ID: rule.source.id},
            {"$set": {constants.CONNECTION_ID: ingestion_execution.id}}
            )

        return ingestion_execution

    def create_raw_files(self, weav_source_copy):
        path = constants.WEAV_DATA_AB_PATH.format(weav_source_copy.project_id)
        target_path = constants.WEAV_DATA_RAW_PATH1.format(weav_source_copy.project_id)
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        os.mkdir(target_path)
        filedf = pd.read_csv(path)
        all_streams = filedf.stream.unique()
        for stream_name in all_streams:
            streamdf = filedf[filedf.stream==stream_name]
            streamdata = [json.loads(text) for text in list(streamdf.data)]
            streamnorm = pd.json_normalize(streamdata)
            streamnorm.to_csv(constants.WEAV_DATA_RAW_PATH2.format(
                weav_source_copy.project_id,stream_name),index=False
                )

    def add_conn_call_data_service(self, ingestion_execution, weav_source):
        """this function calling data sevice

        Args:
            ingestion_execution ([type]): [description]
            weav_source ([type]): [description]

        Returns:
            [type]: [None]
        """
        weav_source_copy = copy.deepcopy(weav_source)
        if self.check_synching(ingestion_execution):
            # Call function for reconstruction of raw data from ingested data.
            self.create_raw_files(weav_source_copy)
            data = self.add_by_path_calling(weav_source_copy)
            data[constants.ID] = ingestion_execution.id
            ret_response = get_request_json_as_dataclass(DataService, data)
            return ret_response
        else:
            # Not returning coz of threading
            data = {
                constants.ID: ingestion_execution.id
            }
            return get_request_json_as_dataclass(DataService, data)

    def check_synching(self, ingestion_execution):
        """This function checking the status of dataset being ingested

        Args:
            ingestion_execution ([type]): [description]

        Returns:
            Boolien: True for Success
        """
        # Adding count to return after 10 tries when status is "Incomplete".
        # Since Airbyte takes more time to respond failed status.
        # TODO implement better way for timeout.
        count = 0
        while True:
            ingestion_execution = self.get_status_of_ingestion(ingestion_execution)
            if ingestion_execution.status == constants.SUCCEEDED:
                return True
            elif ingestion_execution.status == constants.FAILED:
                return False
            elif ingestion_execution.status == constants.INCOMPLETE:
                if count == 10:
                    return False
                else:
                    count = count+1

    def add_by_path_calling(self, weav_source_copy):
        """Calling add_by_path api of data_service

        Args:
            weav_source_copy ([type]): [description]

        Raises:
            DataserviceException: [description]

        Returns:
            Data service return
        """
        url = constants.WEAV_DATA_SERVICE_ADD_BY_PATH.format(
            self.weav_data_service)
        payload = json.dumps(
            {
                constants.PROJECT_ID: weav_source_copy.project_id,
                constants.DATASET_ID: constants.EMPTY_STR,
                constants.URL_PATH: constants.FORMAT_3IP.format(
                    environ.get(constants.SHARED_VOLUME_PATH),
                    constants.LIBRARY_NAME,
                    weav_source_copy.project_id,
                ),
                constants.ARTIFACT_ID: weav_source_copy.artifact_id,
                constants.DATASET_NAME: weav_source_copy.user_defined_name,
                constants.DESTINATION_PATH: constants.RAW,
                constants.DESTINATION: constants.AB_CUST_DEST,
                constants.TAGS: [],
                constants.FILE_TYPE:
                    weav_source_copy.connection_configurations.get(
                    constants.AIRBYTE_FORMAT, constants.DEFAULT),
                constants.CONNECTOR_ID: weav_source_copy.connector_id,
                constants.SOURCE_NAME: weav_source_copy.connector_name,
                constants.CONNECTOR_NAME: weav_source_copy.connector_name,
            }
        )
        headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
        data = dict()
        try:
            response = requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
            )
            return_response = response.json()
            
            if return_response.get(constants.STATUS).get(constants.CODE) >= 400:
                raise DataserviceException(status_code=return_response.get(
                    constants.STATUS).get(constants.CODE))
            elif return_response.get(constants.STATUS).get(constants.CODE) == 200:
                dataset_id = return_response[constants.DATA][constants.DATASET_ID]
                # Storing dataset_id in mongodb collection
                db = self.client.ingestiondb
                collection = db.connectors
                collection.update_one(
                    {constants.CONNECTOR_ID: weav_source_copy.connector_id},
                    {"$set": {constants.DATASET_ID: dataset_id}}
                    )
            
                data = return_response.get(constants.DATA)
                dag_id = constants.DICT_OF_DAGS_ID[weav_source_copy.transformation_dag]
                # Calling transformation
                transformation_url = constants.WEAV_DATAFLOW_DAG_TRIGGER.format(self.weav_dataflow_service)
                transformation_payload = json.dumps(
                    {
                    constants.EXECUTABLE_DAG:{
                        constants.DAG_ID: dag_id
                        },
                    constants.EXECUTION_CONTEXT:{        
                        constants.DAG_RUN_ID:weav_source_copy.project_id+"-"+return_response[constants.DATA][constants.DATASET_ID][:8],
                        constants.CONFIGURATION:{constants.DATASET_ID: dataset_id}        
                        }
                    }
                )
                headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
                response = requests.request(
                    constants.REQUEST_POST, transformation_url, headers=headers, data=transformation_payload
                )
        except Exception:
            pass
        return data

    def getall_list(self):
        """Getting list of all available airbyte sources

        Returns:
            [type]: [description]
        """
        response = self.post_response(
            constants.SOURCE_DEFINITIONS,
            constants.LIST,
        )
        data = json.loads(response.content)
        data = data[constants.AIRBYTE_SOURCE_DEFINITIONS]
        ret_response = [{constants.CONNECTOR_NAME: itm[constants.AIRBYTE_NAME],
                        constants.CONNECTOR_DEF_ID: itm[
                            constants.AIRBYTE_SOURCE_DEFINITION_ID]}
                        for itm in data]
        return ret_response

    def sort_properties(self, lst: list) -> list:
        """Sorting for properties in order

        Args:
            lst (properties list)

        Returns:
            list: properties in order
        """
        order_prop = [itm for itm in lst if "order" in itm.keys()]
        no_order_prop = [itm for itm in lst if "order" not in itm.keys()]
        newlist = sorted(order_prop, key=lambda d: d['order'])
        newlist = newlist + no_order_prop
        return newlist

    def sort_properties_object(self, lst: list) -> list:
        """Sorting for properties in order

        Args:
            lst (list): [description]

        Returns:
            list: [description]
        """
        oneof_prop = [itm for itm in lst if "oneOf" in itm.keys()]
        no_oneof_prop = [itm for itm in lst if "oneOf" not in itm.keys()]
        newlist = no_oneof_prop + oneof_prop
        return newlist

    def get_display_list(self, data):
        """Getting configuration for selected airbyte Source

        Args:
            data ([type]): [description]

        Returns:
            [type]: [description]
        """
        # Sending hardcoded configuration for "File" connector for Demo
        # TODO Revert/Modify according to client's feedback after Demo.
        if data[constants.SOURCE_DEFINITION_ID] == \
                "778daa7c-feaf-4db6-96f3-70fd645acc77":
            try:
                ret_response = json.loads("""{
                    "connectionSpecification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": false,
                        "properties": [
                        {
                        "description": "URL path to access the file to be replicated",
                        "name": "url",
                        "type": "string"
                        }
                        ],
                        "required": [
                            "dataset_name",
                            "format",
                            "url"
                        ],
                        "title": "File Source Spec",
                        "type": "object"
                    },
                    "documentationUrl":
                        "https://docs.airbyte.io/integrations/sources/file",
                    "sourceDefinitionId":
                        "778daa7c-feaf-4db6-96f3-70fd645acc77"
                    }""")
                return ret_response
            except Exception as e:
                return {"msg": e}
        else:
            response = self.post_response(
                constants.AB_SRC_DEF_SPEC,
                constants.GET,
                data={
                    constants.AIRBYTE_SOURCE_DEFINITION_ID:
                    data[constants.SOURCE_DEFINITION_ID]},
            )
            if response.status_code >= 300:
                raise AirbyteError(
                    message=response.json["message"],
                    status_code=response.status_code
                    )
            data = json.loads(response.content)
            ret_response = dict()
            ret_response[constants.AIRBYTE_SOURCE_DEFINITION_ID] = data[constants.AIRBYTE_SOURCE_DEFINITION_ID]
            ret_response[constants.AB_DOC_URL] = data[constants.AB_DOC_URL]
            ret_response[constants.AB_CONN_SPEC] = data[constants.AB_CONN_SPEC]
            prop_ori = data[constants.AB_CONN_SPEC][constants.PROPERTIES]
            prop_list = []
            for prop, config in prop_ori.items():
                temp_dict = dict()
                temp_dict[constants.NAME] = prop
                for k, v in config.items():
                    temp_dict[k] = v
                prop_list.append(temp_dict)
            new_prop = []
            for itm in prop_list:
                if itm[constants.TYPE] == constants.OBJECT:
                    if constants.ONEOF in itm.keys():
                        oneOf_list = itm[constants.ONEOF]
                        new_oneOf = []
                        for elmt in oneOf_list:
                            if constants.PROPERTIES in elmt.keys():
                                new_prop_val = []
                                for k, v in elmt[constants.PROPERTIES].items():
                                    v[constants.NAME] = k
                                    new_prop_val.append(v)
                                # sort new_prop_val here,then append to elmt
                                new_prop_val = self.sort_properties(new_prop_val)
                                elmt[constants.PROPERTIES] = new_prop_val
                            new_oneOf.append(elmt)
                        itm[constants.ONEOF] = new_oneOf
                        new_prop.append(itm)
                    else:
                        new_prop.append(itm)
                else:
                    new_prop.append(itm)
            # sort new_prop here and then add in ret_response
            new_prop = self.sort_properties(new_prop)
            new_prop = self.sort_properties_object(new_prop)
            ret_response[constants.AB_CONN_SPEC][constants.PROPERTIES] = new_prop
            return ret_response

    def getuser_conn_list(self, data: WeavDataSource) -> list:
        """Getting list of connection created by perticular user

        Args:
            data (WeavDataSource): [description]

        Returns:
            list: [description]
        """
        db = self.client.ingestiondb
        collection = db.connectors
        users_connections_cursor = collection.find(
            {constants.USER_ID: data.user_id})
        ret_value = []
        for connections in users_connections_cursor:
            if connections:
                del connections[constants.COL_ID]
                ret_value.append(connections)
        if len(ret_value):
            return ret_value
        else:
            return constants.NO_CONN_MSG

    def local_upload(self, data):
        """Uploader for local files using airbyte local file connector

        Args:
            data (UploadFile): input file/path

        Returns:
            [type]: [description]
        """
        uploaded_file = data[constants.FILE]
        uploaded_filename = uploaded_file.filename
        filename = uploaded_filename.split(".")[0]
        # Local upload
        # spath = "/tmp/airbyte_local/{}".format(uploaded_filename)
        # newspath = "/local" + spath[18:]

        # Docker upload
        spath = constants.WEAV_DATA_UPLOAD_RAW.format(uploaded_filename)
        newspath = constants.LOCAL_PREFIX.format(spath[10:])

        uploaded_file.save(spath)
        ab_format = self.filetype(spath)
        if ab_format is None:
            inspect_data = self.call_inspect(spath)
            ab_format = inspect_data[constants.FILE_FORMAT]
        if ab_format is None:
            ab_format = constants.CSV_READS
        connection_configurations = {
            constants.URL: newspath,
            constants.AIRBYTE_FORMAT: ab_format,
            constants.PROVIDER: {
                constants.STORAGE: constants.LOCAL
            },
            constants.DATASET_NAME: filename
        }
        if ab_format == constants.CSV_READS:
            connection_configurations[constants.AIRBYTE_FORMAT] = constants.CSV
            connection_configurations[constants.READER_OPTIONS]= constants.DEF_READER_OPT_LOCAL_UPLOAD

        source = DataSource(
            type=constants.FILE,
            connection_configurations=connection_configurations,
            name=filename,
        )
        # Add connector errors -- AirbyteError
        connector = self.add_source(source)
        connector_id = connector.id
        workspace_id = connector.workspace_id
        # Creating destination
        name = constants.AB_CUST_DEST + "_" + filename
        data = {
            constants.TYPE: constants.AB_CUST_DEST,
            constants.NAME: name,
            constants.CONNECTION_CONFIGURATIONS: {
                constants.AIRBYTE_CUSTOM_OUTPUT_DIRECTORY: "{}/{}/{}".format(
                    constants.LIBRARY_NAME, constants.LOCAL_INGESTED_FOLDER, filename
                )
            },
            constants.WORKSPACE_ID: workspace_id,
        }
        destination = get_request_json_as_dataclass(DataSource, data)
        # Add destination errors -- AirbyteError
        destination = self.add_destination(destination)
        custom_destination_id = destination.id
        data = {
                constants.SOURCE: {constants.ID: connector_id,
                constants.CONNECTION_CONFIGURATIONS: connection_configurations},
                constants.DESTINATION: {constants.ID: custom_destination_id},
                constants.SCHEDULE: Schedule(),
                constants.STATUS: constants.ACTIVE,
            }
        rule = get_request_json_as_dataclass(IngestionRule, data)
        # Testing source and destination for given config
        self.check_connection(rule)
        rule = self.add_ingestion_rule(
                source=rule.source,
                destination=rule.destination,
                schema=rule.schema,
                schedule=rule.schedule,
                status=rule.status,
                )
        ingestion_execution = self.ingestion_rule(rule, status=rule.status)
        ingestion_execution = self.start_ingestion(ingestion_execution)
        self.trigger_ingestion(ingestion_execution)
        if self.check_synching(ingestion_execution):
            ret_msg = f"Local file ingested successfully for {uploaded_filename}" 
        else:
            ret_msg = f"Local file ingestion is incomplete or failed for {uploaded_filename}"
        if os.path.exists(spath):
            os.remove(spath)
        self.remove_connector(WeavDataSource(connector_id = rule.source.id))
        self.remove_destination(rule.destination)
        return ret_msg

    def get_stepper_ui(self, data):
        """Sending stepper ui based on service.
        Returns:
            list: stepper list
        """
        ret_response = list()
        if data.service.lower() == "airbyte":
            # file
            ret_response = ["Add Connector", "Dataset Information", "Download Dataset", "Link Recipe",
                        "Search Recipe", "Save Pipeline"]
            # # other connector
            # ret_response = ["Add Connector", "Dataset Information and Streams", "Download Dataset",
            #                 "Preview Data", "Search Recipe", "Link Recipe"]
        return ret_response

    def get_stream_preview(self, data):
        """Getting preview string for selected stream.
        Returns:
            str: encoded preview string
        """
        encoded = ""
        connection_id = data.connection_id
        stream_name = data.stream_name
        # Get from mongodb
        db = self.client.ingestiondb
        collection = db.connectors
        ret_value = collection.find_one(
            {constants.CONNECTION_ID: connection_id}
            )
        if ret_value:
            # # Local
            # path = "/tmp/airbyte_local/airbyte/{}/default.csv".format(
            #     ret_value["project_id"])
            # Docker
            path = constants.WEAV_DATA_AB_PATH.format(
                    ret_value["project_id"])
            filedf = pd.read_csv(path)
            all_streams = filedf.stream.unique()
            if stream_name in all_streams:
                streamdf = filedf[filedf.stream==stream_name].head(10)
                streamdata = [json.loads(text) for text in list(streamdf.data)]
                streamnorm = pd.json_normalize(streamdata)
                # streamnorm.to_csv("/home/sheshan/Downloads/Original/file.csv")
                streamdata_to_csv = streamnorm.to_csv(index=False)
                data_bytes = streamdata_to_csv.encode("utf-8") # base64 needs bytes to encode
                encoded = base64.b64encode(data_bytes) # encoding to base64
                return encoded
            else:
                raise FileNotFoundError(constants.NO_STREAM.format(all_streams))
        else:
            raise FileNotFoundError(constants.NO_RECORD)
    
    def webhook_sync(self,data):
        """Getting list of all available airbyte sources

        Returns:
            [type]: [description]
        """
        connection_id = data["text"].split('\n')[3].split("/")[-1]
    
        ret_response = {constants.CONNECTION_ID: connection_id}
        current_app.logger.info(data["text"])
        return ret_response
