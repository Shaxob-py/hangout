from starlette_admin.contrib.sqla import Admin

from admin.eventp import EventParticipantModelView
from admin.login import UsernameAndPasswordProvider
from admin.event import EventsModelView
from admin.users import UserModelView, AdminModelView
from database import User, EventParticipant, Event
from database.base import db
from root.config import settings

admin = Admin(
    engine=db.engine,
    title="Trip",
    templates_dir="template",
    auth_provider=UsernameAndPasswordProvider(),
    base_url=settings.SECRETE_ADMIN_URL
)

admin.add_view(EventsModelView(Event))
admin.add_view(UserModelView(User))
admin.add_view(AdminModelView(User))
admin.add_view(EventParticipantModelView(EventParticipant))
