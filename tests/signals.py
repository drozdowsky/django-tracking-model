from django.db.models.signals import pre_save, post_save
from .models import SignalModel, MutableModel


def pre_save_signal_model(instance, *args, **kwargs):
    if instance.tracker.changed:
        instance.signal_field = "pre_save_changed"
    elif instance.tracker.newly_created:
        instance.signal_field = "pre_save_newly_created"
    else:
        instance.signal_field = "pre_save_not_changed"


def pre_save_example(instance, *args, **kwargs):
    old_text = instance.tracker.changed.get("text", None)
    if old_text:
        instance.array = old_text.split(" ")


def post_save_signal_model(instance, created, *args, **kwargs):
    if "text_field" in instance.tracker.changed:
        if instance.text_field == "post_save_change":
            instance.post_signal_field = "post_save_changed"
    elif instance.tracker.newly_created:
        instance.post_signal_field = "post_save_newly_created"
    else:
        instance.post_signal_field = "post_save_not_changed"


def pre_save_mutable_model(instance, *args, **kwargs):
    if "text" in instance.tracker.changed or instance.tracker.newly_created:
        text = instance.text
        if text:
            instance.array_field = text.split()


pre_save.connect(pre_save_mutable_model, sender=MutableModel)
pre_save.connect(pre_save_signal_model, sender=SignalModel)
post_save.connect(post_save_signal_model, sender=SignalModel)
