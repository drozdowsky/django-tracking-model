from __future__ import absolute_import, unicode_literals

from django.contrib.postgres.fields import ArrayField
from django.db import models

from tracking_model import TrackingModelMixin


class ModelB(TrackingModelMixin, models.Model):
    st_int_field = models.IntegerField(null=False)
    nd_int_field = models.IntegerField(null=True)


class ModelA(TrackingModelMixin, models.Model):
    text_field = models.TextField()
    related = models.ForeignKey(
        ModelB, related_name="ases", null=True, on_delete=models.CASCADE
    )
    related_self = models.OneToOneField(
        "self", related_name="ases_self", null=True, on_delete=models.CASCADE
    )


class SignalModel(TrackingModelMixin, models.Model):
    text_field = models.TextField(null=True)
    signal_field = models.TextField(null=True)
    post_signal_field = models.TextField(null=True)


class MutableModel(TrackingModelMixin, models.Model):
    text = models.TextField(null=True)
    array_field = ArrayField(models.TextField(), null=True)


class NarrowTrackedModel(TrackingModelMixin, models.Model):
    TRACKED_FIELDS = ["first"]
    first = models.TextField(null=True)
    second = models.TextField(null=True)
