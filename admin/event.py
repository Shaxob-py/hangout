from starlette_admin import IntegerField, EnumField, StringField
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.contrib.sqla import ModelView

from database import User


class EventsModelView(ModelView):
    fields = [
        StringField("name", label="Name", help_text="togri yoz"),
        StringField("description", label="Description"),
        IntegerField("owner_id", label="Owner id"),
        EnumField("is_active", enum=User.Role, label="is_active"),
        StringField("location", label="Location"),
        StringField("date_event", label="Datem Event"),
        StringField("location", label="Location"),
    ]

    label = 'Events'
    identity = 'event'
