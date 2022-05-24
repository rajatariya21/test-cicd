from marshmallow import Schema, fields


class Schedule(Schema):
    months = fields.Integer(
        required=True,
        error_messages={
            "required": "months is required.",
            "invalid": "months is not valid.",
        },
    )

    weeks = fields.Integer(
        required=True,
        error_messages={
            "required": "weeks is required.",
            "invalid": "weeks is not valid.",
        },
    )

    days = fields.Integer(
        required=True,
        error_messages={
            "required": "days is required.",
            "invalid": "days is not valid.",
        },
    )
    hours = fields.Integer(
        required=True,
        error_messages={
            "required": "hours is required.",
            "invalid": "hours is not valid.",
        },
    )
    minutes = fields.Integer(
        required=True,
        error_messages={
            "required": "minutes is required.",
            "invalid": "minutes is not valid.",
        },
    )


class CreateConnector(Schema):

    user_id = fields.String(
        required=True,
        error_messages={
            "required": "user_id is required.",
            "invalid": "user_id  is not valid.",
        },
    )
    workspace_id = fields.String(
        required=True,
        error_messages={
            "required": "workspace_id is required.",
            "invalid": "workspace_id is not valid.",
        },
    )
    connector_name = fields.String(
        required=True,
        error_messages={
            "required": "connector_name is required.",
            "invalid": "connector_name is not valid.",
        },
    )
    auth_method = fields.String(
        error_messages={
            "invalid": "auth_method is not valid.",
        },
    )
    auth_token = fields.String(
        error_messages={
            "invalid": "auth_token is not valid.",
        },
    )
    token_expiry_time = fields.String(
        error_messages={
            "invalid": "token_expiry_time is not valid.",
        },
    )
    password = fields.String(
        error_messages={
            "invalid": "password is not valid.",
        },
    )
    api_key = fields.String(
        error_messages={
            "invalid": "api_key is not valid.",
        },
    )
    connection_configurations = fields.Dict(
        required=True,
        error_messages={
            "required": "connection_configurations is required.",
            "invalid": "connection_configurations is not valid.",
        },
    )
    project_id = fields.String(
        error_messages={
            "invalid": "project_id is not valid.",
        },
    )
    user_defined_name = fields.String(
        required=True,
        error_messages={
            "required": "user_defined_name is required.",
            "invalid": "user_defined_name is not valid.",
        },
    )
    schedule = fields.Nested(
        Schedule,
        required=False,
        error_messages={
            "required": "schedule is required.",
            "invalid": "schedule is not valid.",
        },
    )


class ViewConnector(Schema):

    connector_id = fields.String(
        required=True,
        error_messages={
            "required": "connector_id is required.",
            "invalid": "connector_id is not valid.",
        },
    )


class DeleteConnector(Schema):

    connector_id = fields.String(
        required=True,
        error_messages={
            "required": "connector_id is required.",
            "invalid": "connector_id is not valid.",
        },
    )


class UpdateConnector(Schema):
    connector_id = fields.String(
        required=True,
        error_messages={
            "required": "connector_id is required.",
            "invalid": "connector_id  is not valid.",
        },
    )
    connector_name = fields.String(
        error_messages={
            "invalid": "connector_name is not valid.",
        },
    )
    auth_method = fields.String(
        error_messages={
            "invalid": "auth_method is not valid.",
        },
    )
    user_id = fields.String(
        required=False,
        error_messages={
            "invalid": "user_id  is not valid.",
        },
    )
    auth_token = fields.String(
        error_messages={
            "invalid": "auth_token is not valid.",
        },
    )
    token_expiry_time = fields.String(
        error_messages={
            "invalid": "token_expiry_time is not valid.",
        },
    )
    password = fields.String(
        error_messages={
            "invalid": "password is not valid.",
        },
    )
    api_key = fields.String(
        error_messages={
            "invalid": "api_key is not valid.",
        },
    )
    connection_configurations = fields.Dict(
        required=True,
        error_messages={
            "required": "connection_configurations is required.",
            "invalid": "connection_configurations is not valid.",
        },
    )
    project_id = fields.String(
        error_messages={
            "invalid": "project_id is not valid.",
        },
    )
    user_defined_name = fields.String(
        required=True,
        error_messages={
            "required": "user_defined_name is required.",
            "invalid": "user_defined_name is not valid.",
        },
    )


class ViewConnector(Schema):

    connector_id = fields.String(
        required=True,
        error_messages={
            "required": "connector_id is required.",
            "invalid": "connector_id is not valid.",
        },
    )
