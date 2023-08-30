from django import forms
from django.conf import settings
from pod.main.forms_utils import add_placeholder_and_asterisk
from pod.podfile.widgets import CustomFileWidget
from django.contrib.sites.models import Site
from django_select2 import forms as s2forms
from django.db.models import Q

from pod.video.models import Video
from .models import Dressing

__FILEPICKER__ = False
if getattr(settings, "USE_PODFILE", False):
    __FILEPICKER__ = True
    from pod.podfile.widgets import CustomFileWidget


class OwnerWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "username__icontains",
        "email__icontains",
    ]


class AddOwnerWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "username__icontains",
        "email__icontains",
    ]


class AddAccessGroupWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "display_name__icontains",
        "code_name__icontains",
    ]


class AddVideoHoldWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "slug__icontains",
        "title__icontains"
    ]


class DressingForm(forms.ModelForm):
    is_staff = True
    is_superuser = False
    admin_form = True
    site = forms.ModelChoiceField(Site.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        self.is_staff = (
            kwargs.pop("is_staff") if "is_staff" in kwargs.keys() else self.is_staff
        )
        self.is_superuser = (
            kwargs.pop("is_superuser")
            if ("is_superuser" in kwargs.keys())
            else self.is_superuser
        )
        self.user = kwargs.pop("user", None)

        super(DressingForm, self).__init__(*args, **kwargs)
        if __FILEPICKER__:
            self.fields["watermark"].widget = CustomFileWidget(type="image")

        if not self.is_superuser or not hasattr(self, "admin_form"):
            self.fields["owners"].queryset = self.fields["owners"].queryset.filter(
                owner__sites=Site.objects.get_current()
            )
            self.fields["users"].queryset = self.fields["users"].queryset.filter(
                owner__sites=Site.objects.get_current()
            )

        # change ckeditor config for no staff user
        if not hasattr(self, "admin_form") and (
            self.is_staff is False and self.is_superuser is False
        ):
            del self.fields["watermark"]
        # hide default langage
        if self.fields.get("title_%s" % settings.LANGUAGE_CODE):
            self.fields["title_%s" % settings.LANGUAGE_CODE].widget = forms.HiddenInput()

        self.fields = add_placeholder_and_asterisk(self.fields)
        self.fields['opacity'].widget.attrs.update({'max': '100'})
        self.fields["owners"].initial = self.user

    class Meta(object):
        model = Dressing
        fields = "__all__"
        widgets = {
            "owners": AddOwnerWidget,
            "users": AddOwnerWidget,
            "allow_to_groups": AddAccessGroupWidget,
            "opening_credits": AddVideoHoldWidget,
            "ending_credits": AddVideoHoldWidget,
        }
