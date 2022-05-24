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

    source = fields.Nested(
        ID,
        required=True,
        error_messages={
            "required": "source is required.",
            "invalid": "source is not valid.",
        },
    )
    destination = fields.Nested(
        ID,
        required=True,
        error_messages={
            "required": "destination is required.",
            "invalid": "destination is not valid.",
        },
    )
    schedule = fields.Nested(
        Schedule,
        required=True,
        error_messages={
            "required": "schedule is required.",
            "invalid": "schedule is not valid.",
        },
    )

    status = fields.String(
        required=True,
        error_messages={
            "required": "status is required.",
            "invalid": "status is not valid.",
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


class ListConnection(Schema):

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
