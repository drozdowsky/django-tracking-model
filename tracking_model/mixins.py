from django.db.models.query_utils import DeferredAttribute


class Tracker(object):
    def __init__(self, instance, fields=None):
        self.instance = instance
        self.newly_created = False
        self.changed = {}
        self.tracked_fields = {f.attname for f in self.instance._meta.concrete_fields}
        if fields is not None:
            self.tracked_fields &= set(fields)


class TrackingModelMixin(object):
    def __init__(self, *args, **kwargs):
        super(TrackingModelMixin, self).__init__(*args, **kwargs)
        self._initialized = True

    @property
    def tracker(self):
        self._state._tracker = getattr(self._state, "_tracker", None) or Tracker(
            self, getattr(self, "TRACKED_FIELDS", None)
        )
        return self._state._tracker

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
