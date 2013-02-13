from django.conf import settings
from django import forms
from django.utils.translation import ugettext as _
from taggit.utils import parse_tags, edit_string_for_tags


class TagWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, basestring):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
        return super(TagWidget, self).render(name, value, attrs)

class TagField(forms.CharField):
    widget = TagWidget

    def clean(self, value):
        value = super(TagField, self).clean(value)
        try:
            parsed_values =  parse_tags(value)
            TAGGIT_ALLOWED_TAGS =  getattr(settings, "TAGGIT_ALLOWED_TAGS", None)
            if TAGGIT_ALLOWED_TAGS:
                LOWER_TAGS = [x.lower() for x in TAGGIT_ALLOWED_TAGS]
                for value in parsed_values:
                    if value.lower() not in LOWER_TAGS:
                        raise forms.ValidationError('Tag %s not valid (should be one of: %s)' %(value, ",".join(TAGGIT_ALLOWED_TAGS)))
            TAGGIT_FORCE_LOWERCASE = getattr(settings, 'TAGGIT_FORCE_LOWERCASE', False)
            if TAGGIT_FORCE_LOWERCASE:
                parsed_values = [x.lower() for x in parsed_values]
            return parsed_values
        except ValueError:
            raise forms.ValidationError(_("Please provide a comma-separated list of tags."))
