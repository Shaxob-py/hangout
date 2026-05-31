from starlette_admin import IntegerField, EnumField, StringField
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import StringField, IntegerField, EnumField, DateTimeField , UUIDField




class EventsModelView(ModelView):
    fields = [
        StringField("name", label="Name", help_text="togri yoz"),
        StringField("description", label="Description"),
        UUIDField("owner_id", label="Owner id")
        StringField("location", label="Location"),
        DateTimeField("date_event", label="Date Event"),
    ]

    label = 'Events'
    identity = 'events'
