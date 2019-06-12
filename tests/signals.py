from django.db.models.signals import pre_save, post_save
from .models import SignalModel


def pre_save_signal_model(instance, *args, **kwargs):
    if instance.tracker.changed:
        instance.signal_field = 'pre_save_changed'
    elif instance.tracker.newly_created:
        instance.signal_field = 'pre_save_newly_created'
    else:
        instance.signal_field = 'pre_save_not_changed'


#def post_save_model_c(instance, created, *args, **kwargs):
#    instance.signal_field = 'post_save'

pre_save.connect(pre_save_signal_model, sender=SignalModel)
#post_save.connect(post_save_model_c, sender=SignalModel)
