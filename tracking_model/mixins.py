from django.db.models.query_utils import DeferredAttribute


class Tracker(object):
    def __init__(self, instance):
        self.instance = instance
        self.newly_created = False
        self.changed = {}
        self.tracked_fields = self.instance.TRACKED_FIELDS


class TrackingModelMixin(object):

    TRACKED_FIELDS = None

    def __init__(self, *args, **kwargs):
        super(TrackingModelMixin, self).__init__(*args, **kwargs)
        self._initialized = True

    @property
    def tracker(self):
        if hasattr(self._state, "_tracker"):
            tracker = self._state._tracker
        else:
            # populate tracked fields for the first time
            # by default all fields
            if not self.TRACKED_FIELDS:
                instance_class = type(self)
                instance_class.TRACKED_FIELDS = {f.attname for f in instance_class._meta.concrete_fields}
            tracker = self._state._tracker = Tracker(self)
        return tracker

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.tracker.newly_created = self._state.adding
        super(TrackingModelMixin, self).save(
            force_insert, force_update, using, update_fields
        )
        if self.tracker.changed:
            if update_fields:
                for field in update_fields:
                    self.tracker.changed.pop(field, None)
            else:
                self.tracker.changed = {}

    def __setattr__(self, name, value):
        if hasattr(self, "_initialized"):
            if name in self.tracker.tracked_fields:
                if name not in self.tracker.changed:
                    if name in self.__dict__:
                        old_value = getattr(self, name)
                        if value != old_value:
                            self.tracker.changed[name] = old_value
                    else:
                        self.tracker.changed[name] = DeferredAttribute
                else:
                    if value == self.tracker.changed[name]:
                        self.tracker.changed.pop(name)

        super(TrackingModelMixin, self).__setattr__(name, value)
