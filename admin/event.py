from starlette_admin.contrib.sqla import ModelView


class EventsModelView(ModelView):
    label = 'Events'
    identity = 'event'