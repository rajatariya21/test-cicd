from marshmallow import Schema, fields


class CreateDestination(Schema):
    type = fields.String(
        required=True,
        error_messages={
            "required": "type is required.",
            "invalid": "type is not valid.",
        },
    )
    connection_configurations = fields.Dict(
        required=True,
        error_messages={
            "required": "connection_configurations is required.",
            "invalid": "connection_configurations is not valid.",
        },
    )
    workspace_id = fields.String(
        required=False,
        error_messages={
            "invalid": "workspace_id is not valid.",
        },
    )

    name = fields.String(
        required=True,
        error_messages={
            "required": "name is required.",
            "invalid": "name is not valid.",
        },
    )


class ViewDestination(Schema):

    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )


class DeleteDestination(Schema):

    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )


class UpdateDestination(Schema):
    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )
    connection_configurations = fields.Dict(
        required=True,
        error_messages={
            "required": "connection_configurations is required.",
            "invalid": "connection_configurations is not valid.",
        },
    )
    name = fields.String(
        required=True,
        error_messages={
            "required": "name is required.",
            "invalid": "name is not valid.",
        },
    )
