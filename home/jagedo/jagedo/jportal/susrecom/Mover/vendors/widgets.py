# widgets.py
from import_export import widgets
from django.core.exceptions import ObjectDoesNotExist


class ForeignKeyWidget(widgets.Widget):
    def __init__(self, model, field_name=None):
        self.model = model
        self.field_name = field_name

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        if self.field_name:
            kwargs = {self.field_name: value}
        else:
            kwargs = {"pk": value}

        try:
            return self.model.objects.get(**kwargs)
        except ObjectDoesNotExist:
            raise ValueError(f"{self.model.__name__} with {kwargs} does not exist")

    def render(self, value, obj=None):
        if value is None:
            return ""
        if self.field_name:
            return getattr(value, self.field_name)
        else:
            return value.pk
