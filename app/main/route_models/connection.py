from marshmallow import Schema, fields


class ID(Schema):

    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )


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


class CreateConnection(Schema):

    connector_id = fields.String(
        required=True,
        error_messages={
            "required": "connector_id is required.",
            "invalid": "connector_id is not valid.",
        },
    )
    artifact_id = fields.String(
        error_messages={
            "invalid": "artifact_id is not valid.",
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
    catalog = fields.Dict(
        error_messages={
            "invalid": "catalog is not valid.",
        },
    )


class DeleteConnection(Schema):

    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )


class InspectConnection(Schema):

    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )


class TriggerConnection(Schema):

    id = fields.String(
        required=True,
        error_messages={
            "required": "id is required.",
            "invalid": "id is not valid.",
        },
    )
