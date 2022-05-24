from marshmallow import Schema, fields



class Get_display_list(Schema):

    source_definition_id = fields.String(
        required=True,
        error_messages={
            "required": "source_definition_id is required.",
            "invalid": "source_definition_id is not valid.",
        },
    )

class Getuser_conn_list(Schema):
    user_id = fields.String(
        required=True,
        error_messages={
            "required": "user_id is required.",
            "invalid": "user_id is not valid.",
        },
    )

class Get_stepper_object(Schema):
    service = fields.String(
        required=True,
        error_messages={
            "required": "service is required.",
            "invalid": "service is not valid.",
        },
    )

class Get_stream_preview(Schema):
    connection_id = fields.String(
        required=True,
        error_messages={
            "required": "connection_id is required.",
            "invalid": "connection_id is not valid.",
        },
    )
    stream_name = fields.String(
        required=True,
        error_messages={
            "required": "stream_name is required.",
            "invalid": "stream_name is not valid.",
        },
    )