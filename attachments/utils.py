from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import get_storage_class
from django.conf import settings
import urllib
import uuid
import json

def get_context_key(context):
    if context:
        return 'attachments-%s' % context
    return 'attachments'

def session(request, template='attachments/list.html', context=''):
    from .models import Session
    try:
        key = get_context_key(context)
        s = Session.objects.get(uuid=request.POST[key])
        s._request = request
        return s
    except:
        for _i in range(5):
            try:
                s = Session.objects.create(user=request.user, uuid=uuid.uuid4().hex, template=template, context=context)
                s._request = request
                return s
            except:
                pass
        raise Exception('Could not create a unique attachment session')

def get_storage():
    cls, kwargs = getattr(settings, 'ATTACHMENT_STORAGE', (settings.DEFAULT_FILE_STORAGE, {}))
    return get_storage_class(cls)(**kwargs)

def get_default_path(upload, obj):
    ct = ContentType.objects.get_for_model(obj)
    return '%s/%s/%s/%s/%s' % (ct.app_label, ct.model, obj.pk, upload.session.context, upload.file_name)

def url_filename(filename):
    # If the filename is not US-ASCII, we need to urlencode it.
    try:
        return filename.encode('us-ascii')
    except:
        return urllib.quote(filename.encode('utf-8'), safe='/ ')

class JSONField (models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value == '':
            return None
        if isinstance(value, basestring):
            return json.loads(value)
        return value

    def get_prep_value(self, value):
        if value == '':
            return None
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(value, cls=DjangoJSONEncoder)
        return super(JSONField, self).get_prep_value(value)

    def value_to_string(self, obj):
        return self.get_prep_value(self._get_val_from_obj(obj))

#    def deconstruct(self):
#        name, _mod, args, kwargs = super(JSONField, self).deconstruct()
#        return name, 'attachments.utils.JSONField', args, kwargs