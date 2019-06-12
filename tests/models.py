from __future__ import unicode_literals, absolute_import

from django.db import models
from tracking_model import TrackingModelMixin


class ModelB(TrackingModelMixin, models.Model):
    st_int_field = models.IntegerField(null=False)
    nd_int_field = models.IntegerField(null=True)


class ModelA(TrackingModelMixin, models.Model):
    text_field = models.TextField()
    related = models.ForeignKey(
        ModelB, related_name='ases', null=True, on_delete=models.CASCADE
    )
    related_self = models.OneToOneField(
        "self", related_name="ases_self", null=True, on_delete=models.CASCADE
    )


class SignalModel(TrackingModelMixin, models.Model):
    text_field = models.TextField(null=True)
    signal_field = models.TextField(null=True)
