from starlette_admin import IntegerField, EnumField, StringField
from starlette_admin.contrib.sqla import ModelView

from database import User


class UserModelView(ModelView):
    fields = [
        StringField("username", label="Username", help_text="togri yoz"),
        StringField("phone", label="Phone"),
        IntegerField("telegram_id", label="Telegram ID"),
        EnumField("role", enum=User.Role, label="Role"),
        StringField("password", label="Password"),
    ]

    label = 'Userlar'
    identity = 'users'
    exclude_fields_from_list = ["password"]
    searchable_fields = ["username", "phone"]

    field_overrides = {
        "phone": {"id": "phone"}
    }

    extra_js = [
        "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js",
        "/static/js/phone-mask.js",
    ]

    def get_list_query(self, request):
        return super().get_list_query(request).where(User.role == User.Role.USER)

    def get_count_query(self, request):
        return super().get_count_query(request).where(User.role == User.Role.USER)


class AdminModelView(ModelView):
    fields = [
        IntegerField("id", label="ID", read_only=True),  # id обычно делают только для чтения
        StringField("username", label="Username"),
        StringField("phone", label="Phone"),
        IntegerField("telegram_id", label="Telegram ID"),
        EnumField("role", enum=User.Role, label="Role"),
        StringField("password", label="Password"),
    ]

    label = 'Adminlar'
    identity = 'admins'
    searchable_fields = ["username", "phone"]

    def get_list_query(self, request):
        return super().get_list_query(request).where(User.role == User.Role.ADMIN)

    def get_count_query(self, request):
        return super().get_count_query(request).where(User.role == User.Role.ADMIN)