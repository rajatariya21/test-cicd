from marshmallow import Schema, fields

# Writing api validations for connector endpoints
# Here we are creating schema by using marshmallow
# This schema will be used by validator which is presented in middleware folder


class CreateWorkspace(Schema):
    name = fields.String(
        required=False,
        error_messages={
            "invalid": "name is not valid.",
        },
    )
    email = fields.String(
        required=False,
        error_messages={
            "invalid": "email is not valid.",
        },
    )
    anonymous_data_collection = fields.Boolean(
        required=False,
        error_messages={
            "invalid": "anonymous_data_collection is not valid.",
        },
    )
    news = fields.Boolean(
        required=False,
        error_messages={
            "invalid": "news is not valid, need boolian value.",
        },
    )
    security_updates = fields.Boolean(
        required=False,
        error_messages={
            "invalid": "security_updates is not valid.",
        },
    )
    notifications = fields.List(
        fields.Dict(),
        required=False,
        error_messages={
            "invalid": "notifications is not valid.",
        },
    )
