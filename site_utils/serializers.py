# Python
from __future__ import unicode_literals
import datetime
import decimal
import json

# Six
import six

# Django
from django.conf import settings
from django.core.serializers import base
from django.core.serializers.base import DeserializationError
from django.db import models, DEFAULT_DB_ALIAS
from django.utils.encoding import smart_text, is_protected_type
from django.utils.timezone import is_aware

__all__ = ['SiteSerializer', 'SiteDeserializer', 'SiteJsonEncoder']


def _get_model(model_identifier):
    """
    Helper to look up a model from an "app_label.module_name" string.
    """
    try:
        Model = models.get_model(*model_identifier.split("."))
    except TypeError:
        Model = None
    if Model is None:
        raise base.DeserializationError("Invalid model identifier: '%s'" % model_identifier)
    return Model


class SiteSerializer(base.Serializer):
    """Serialize a queryset to JSON. Copy of serializer from Django 1.5."""

    internal_use_only = False

    def serialize(self, queryset, **options):
        """Serialize a queryset."""
        self.options = options
        self.stream = options.pop('stream', six.StringIO())
        self.selected_fields = options.pop('fields', None)
        self.use_natural_keys = options.pop('use_natural_keys', True)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            for field in concrete_model._meta.local_fields:
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

    def start_serialization(self):
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        self.stream.write('[')

    def end_serialization(self):
        if self.options.get('indent'):
            self.stream.write('\n')
        self.stream.write(']')
        if self.options.get('indent'):
            self.stream.write('\n')

    def start_object(self, obj):
        self._current = {}

    def end_object(self, obj):
        # self._current has the field data
        indent = self.options.get('indent')
        if not self.first:
            self.stream.write(',')
            if not indent:
                self.stream.write(' ')
        if indent:
            self.stream.write('\n')
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=SiteJsonEncoder, **self.json_kwargs)
        self._current = None

    def get_dump_object(self, obj):
        obj_dump = {
            'pk': smart_text(obj._get_pk_val(), strings_only=True),
            'model': smart_text(obj._meta),
            'fields': self._current,
        }
        if self.use_natural_keys and hasattr(obj, 'natural_key'):
            obj_dump['nk'] = obj.natural_key()
        return obj_dump

    def handle_field(self, obj, field):
        value = field._get_val_from_obj(obj)
        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to string first.
        if is_protected_type(value):
            self._current[field.name] = value
        else:
            self._current[field.name] = field.value_to_string(obj)

    def handle_fk_field(self, obj, field):
        if self.use_natural_keys and hasattr(field.rel.to, 'natural_key'):
            related = getattr(obj, field.name)
            if related:
                value = related.natural_key()
            else:
                value = None
        else:
            value = getattr(obj, field.get_attname())
        self._current[field.name] = value

    def handle_m2m_field(self, obj, field):
        if field.rel.through._meta.auto_created:
            if self.use_natural_keys and hasattr(field.rel.to, 'natural_key'):
                def m2m_value(value):
                    return value.natural_key()
            else:
                def m2m_value(value):
                    return smart_text(value._get_pk_val(), strings_only=True)
            self._current[field.name] = [m2m_value(related) for related in getattr(obj, field.name).iterator()]

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()


def SiteDeserializer(stream_or_string, **options):
    """Deserialize a JSON string or stream back into Django ORM instances."""

    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    try:
        object_list = json.loads(stream_or_string)

        db = options.pop('using', DEFAULT_DB_ALIAS)
        ignore = options.pop('ignorenonexistent', False)

        models.get_apps()
        for d in object_list:
            # Look up the model and starting build a dict of data for it.
            Model = _get_model(d["model"])
            data = {Model._meta.pk.attname: Model._meta.pk.to_python(d["pk"])}
            m2m_data = {}
            model_fields = Model._meta.get_all_field_names()

            # Handle each field
            for (field_name, field_value) in six.iteritems(d["fields"]):

                if ignore and field_name not in model_fields:
                    # skip fields no longer on model
                    continue

                if isinstance(field_value, str):
                    field_value = smart_text(field_value, options.get("encoding", settings.DEFAULT_CHARSET), strings_only=True)

                field = Model._meta.get_field(field_name)

                # Handle M2M relations
                if field.rel and isinstance(field.rel, models.ManyToManyRel):
                    if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
                        def m2m_convert(value):
                            if hasattr(value, '__iter__') and not isinstance(value, six.text_type):
                                return field.rel.to._default_manager.db_manager(db).get_by_natural_key(*value).pk
                            else:
                                return smart_text(field.rel.to._meta.pk.to_python(value))
                    else:
                        def m2m_convert(value):
                            return smart_text(field.rel.to._meta.pk.to_python(value))
                    m2m_data[field.name] = [m2m_convert(pk) for pk in field_value]

                # Handle FK fields
                elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                    if field_value is not None:
                        if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
                            if hasattr(field_value, '__iter__') and not isinstance(field_value, six.text_type):
                                obj = field.rel.to._default_manager.db_manager(db).get_by_natural_key(*field_value)
                                value = getattr(obj, field.rel.field_name)
                                # If this is a natural foreign key to an object that
                                # has a FK/O2O as the foreign key, use the FK value
                                if field.rel.to._meta.pk.rel:
                                    value = value.pk
                            else:
                                value = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                            data[field.attname] = value
                        else:
                            data[field.attname] = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                    else:
                        data[field.attname] = None

                # Handle all other fields
                else:
                    data[field.name] = field.to_python(field_value)

            yield base.DeserializedObject(Model(**data), m2m_data)

    except Exception as e:
        # Map to deserializer error
        raise DeserializationError(e)


class SiteJsonEncoder(json.JSONEncoder):
    """JSONEncoder subclass to handle date/time and decimal types."""

    # From Django 1.5 source.

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(SiteJsonEncoder, self).default(o)
