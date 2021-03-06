from copy import deepcopy

from django.db.models.query_utils import DeferredAttribute
from django.test import TestCase

from .models import ModelA, ModelB, SignalModel, MutableModel, NarrowTrackedModel
from .signals import *


class AllFieldsTrackedModelTests(TestCase):
    def setUp(self):
        related = ModelB.objects.create(st_int_field=1, nd_int_field=None)
        related_self = ModelA.objects.create(text_field="related_value")
        self.a = ModelA.objects.create(
            text_field="init_value", related=related, related_self=related_self
        )
        self.b = ModelB.objects.create(st_int_field=2, nd_int_field=None)
        ModelB.objects.create(st_int_field=3, nd_int_field=None)

    def test_new_object_does_not_changed(self):
        self.assertEqual(self.a.tracker.changed, {})
        self.assertEqual(self.b.tracker.changed, {})

    def test_simple_change(self):
        self.a.text_field = "changed_value"
        self.assertEqual(self.a.tracker.changed, {"text_field": "init_value"})

    def test_save_clears_changed(self):
        self.a.text_field = "changed_value"
        self.a.save()
        self.assertEqual(self.a.tracker.changed, {})

    def test_foreign_key_change(self):
        expected_id = self.a.related_id
        self.a.related = self.b
        self.assertEqual(self.a.tracker.changed, {"related_id": expected_id})

    def test_multiple_changes_to_same_field(self):
        self.a.text_field = "changed_value"
        self.a.text_field = "nd_changed_value"
        self.assertEqual(self.a.tracker.changed, {"text_field": "init_value"})

    def test_tracker_is_unique_to_object(self):
        self.a.text_field = "changed_value"
        self.b.st_int_field = 10
        self.assertEqual(self.a.tracker.changed, {"text_field": "init_value"})
        self.assertEqual(self.b.tracker.changed, {"st_int_field": 2})

    def test_tracker_is_unique_same_class(self):
        ids = {id(m.tracker) for m in ModelB.objects.all()}
        self.assertEqual(len(ids), 3)

    def test_all_objects_are_not_newly_created(self):
        newly_created = {m.tracker.newly_created for m in ModelB.objects.all()}
        self.assertSetEqual(newly_created, {False})

    def test_modified_objects_are_not_newly_created(self):
        self.b.st_int_field = "test"
        self.assertNotEqual(self.b._state.adding, True)

    def test_no_change(self):
        self.b.st_int_field = 2
        self.assertEqual(self.b.tracker.changed, {})

    def test_filter_should_not_be_newly_created(self):
        b = ModelB.objects.filter(st_int_field=2).first()
        self.assertEqual(b.tracker.newly_created, False)

    def test_get_should_not_be_newly_created(self):
        b = ModelB.objects.get(st_int_field=1)
        self.assertEqual(b.tracker.newly_created, False)

    def test_create_should_be_newly_created(self):
        b = ModelB.objects.create(st_int_field=1)
        self.assertEqual(b.tracker.newly_created, True)

    def test_new_raw_object(self):
        b = ModelB(st_int_field=1)
        self.assertEqual(b.tracker.changed, {})
        self.assertEqual(b.tracker.newly_created, False)
        b.save()
        self.assertEqual(b.tracker.newly_created, True)

    def test_raw_object_triple_save(self):
        b = ModelB(st_int_field=1)
        b.save()
        b.st_int_field = 2
        self.assertEqual(b.tracker.changed, {"st_int_field": 1})
        b.save()
        self.assertEqual(b.tracker.newly_created, False)
        b.save()
        self.assertEqual(b.tracker.newly_created, False)

    def test_reverting_change_should_not_be_tracked(self):
        self.a.text_field = "next_value"
        self.a.text_field = "init_value"
        self.assertDictEqual(self.a.tracker.changed, {})


class DeferredFieldsTests(TestCase):
    def setUp(self):
        related = ModelB.objects.create(st_int_field=1, nd_int_field=None)
        related_self = ModelA.objects.create(text_field="related_value")
        ModelA.objects.create(
            text_field="init_value", related=related, related_self=related_self
        )
        ModelB.objects.create(st_int_field=2, nd_int_field=None)

    def test_simple_deferred_field(self):
        a = ModelA.objects.only("id").first()
        a.text_field = "nd_value"
        self.assertDictEqual(a.tracker.changed, {"text_field": DeferredAttribute})

    def test_update_fields_save(self):
        a = ModelA.objects.only("related_id").filter(related_id__isnull=False).first()
        a.text_field = "nd_value"
        a.save(update_fields=["related_id"])
        self.assertDictEqual(a.tracker.changed, {"text_field": DeferredAttribute})

    def test_no_fetch_from_db(self):
        a = ModelA.objects.only("id").first()
        with self.assertNumQueries(0):
            a.text_field = "nd_value"

    def test_multiple_set_with_save(self):
        a = ModelA.objects.only("id").first()
        a.text_field = "nd_value"
        a.save()
        a.text_field = "rd_value"
        self.assertDictEqual(a.tracker.changed, {"text_field": "nd_value"})
        a.save()
        self.assertDictEqual(a.tracker.changed, {})

    def test_complex_deferred_field(self):
        b = ModelB.objects.only("st_int_field").get(st_int_field=2)
        b.st_int_field = 4
        b.nd_int_field = 8
        self.assertDictEqual(
            b.tracker.changed, {"st_int_field": 2, "nd_int_field": DeferredAttribute}
        )


class SignalTests(TestCase):
    def setUp(self):
        self.signal_model = SignalModel.objects.create(text_field="init_value")

    def test_simple_pre_save_signal(self):
        self.signal_model.text_field = "changed_value"
        self.signal_model.save()
        self.assertEqual(self.signal_model.signal_field, "pre_save_changed")

    def test_signal_newly_created(self):
        s = SignalModel.objects.create(text_field="changed_value")
        self.assertEqual(s.signal_field, "pre_save_newly_created")

    def test_signal_not_changed(self):
        self.signal_model.save()
        self.assertEqual(self.signal_model.signal_field, "pre_save_not_changed")

    def test_post_save_signal(self):
        self.signal_model.text_field = "post_save_change"
        self.assertEqual(
            self.signal_model.tracker.changed, {"text_field": "init_value"}
        )
        self.signal_model.save()
        self.assertEqual(self.signal_model.post_signal_field, "post_save_changed")

    def test_post_save_newly_created(self):
        self.assertEqual(self.signal_model.post_signal_field, "post_save_newly_created")
        self.signal_model.save()
        self.assertEqual(self.signal_model.post_signal_field, "post_save_not_changed")


class MutableFieldsTests(TestCase):
    def setUp(self):
        self.mutable = MutableModel.objects.create(
            array_field=["I", "am", "your", "father"]
        )

    def test_mutable_field_does_not_deepcopy(self):
        self.mutable.array_field.append(", Luke")
        self.assertDictEqual(self.mutable.tracker.changed, {})

    def test_mutable_deep_copy_works(self):
        orig_array_field = self.mutable.array_field
        deep_array_field = deepcopy(orig_array_field)
        deep_array_field.append(", Luke")
        self.mutable.array_field = deep_array_field
        self.assertDictEqual(
            self.mutable.tracker.changed, {"array_field": orig_array_field}
        )

    def test_on_create_pre_signal(self):
        m = MutableModel.objects.create(text="I am your father")
        self.assertEqual(m.array_field, ["I", "am", "your", "father"])
        m.refresh_from_db()
        self.assertEqual(m.array_field, ["I", "am", "your", "father"])


class TrackedFieldsOnlyTests(TestCase):
    def setUp(self):
        self.obj = NarrowTrackedModel(first="Ciao", second="Siciliano")

    def test_only_track_first(self):
        self.obj.first = "Ciao ciao"
        self.obj.second = "Italiano"
        self.assertDictEqual(self.obj.tracker.changed, {"first": "Ciao"})
