from starlette_admin.contrib.sqla import ModelView


class EventParticipantModelView(ModelView):
    fields = [
        "id",
        "user_id",
        "event_id",
        "is_active",


    ]
    label = 'EventParticipant'
    identity = 'event_participants'