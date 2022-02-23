# Django Tracking Model / DTM 🏁
Track changes made to your model's instance fields.  
Changes are cleared on save.  
This package works well with [signals](https://seddonym.me/2018/05/04/django-signals/).  
Mutable fields (e.g. JSONField) are not handled with deepcopy to keep it fast and simple.  
Meant to be [model_utils](https://github.com/jazzband/django-model-utils)'s FieldTracker fast alternative.

*Available on [PyPi](https://pypi.org/project/django-tracking-model/)*  

## Installation
```sh
pip install django-tracking-model
```

## Usage
```python
from django.db import models
from tracking_model import TrackingModelMixin

# order matters
class Example(TrackingModelMixin, models.Model):
    text = models.TextField(null=True)
    myself = models.ForeignKey("self", null=True)
    array = models.ArrayField(TextField())
```
```python
In [1]: e = Example.objects.create(id=1, text="Sample Text")
In [2]: e.tracker.changed, e.tracker.newly_created
Out[1]: ({}, True)

In [3]: e.text = "Different Text"
In [4]: e.tracker.changed
Out[2]: {"text": "Sample Text"}

In [5]: e.save()
In [6]: e.tracker.changed, e.tracker.newly_created
Out[3]: ({}, False)
```
DTM will also detect changes made to ForeignKey/OneToOne fields.
```python
In [1]: Example.objects.create(myself=e)
In [2]: e.myself = None
In [3]: e.tracker.changed
Out[1]: {"myself_id": 1}
```
Because DTM does not handle mutable fields well, you handle them with copy/deepcopy.
```python
In [1]: e = Example.objects.create(array=["I", "am", "your"])
In [2]: copied = copy(e.array)
In [3]: copied.append("father")
In [4]: e.array = copied
In [5]: e.tracker.changed
Out[1]: {"array": ["I", "am", "your"]}

In [6]: e.array = ["Testing", "is", "the", "future"]  # in this case copy not needed
```
DTM works best with \*\_save signals.
```python
def pre_save_example(instance, *args, **kwargs):
    # .create() does not populate .changed, we use newly_created
    if "text" in instance.tracker.changed or instance.tracker.newly_created:
      if instance.text
          instance.array = instance.text.split()

pre_save.connect(pre_save_example, sender=Example)
```
```python
In [1]: e = Example.objects.create(text="I am your father")
In [2]: e.refresh_from_db() # not needed
In [3]: e.array
Out[1]: ["I", "am", "your", "father"]
```
DTM handles deferred fields well.
```python
In [1]: e = Example.objects.only("array").first()
In [2]: e.text = "I am not your father" 
In [3]: e.tracker.changed
Out[4]: {"text": DeferredAttribute}
```
You can narrow choice of tracked fields. By default everything is tracked.
```python
class Example(models.Model):
    TRACKED_FIELDS = ["first"]
    first = models.TextField()
    second = models.TextField()
```

## Requirements
 * Python >= 2.7, <= 3.9
 * Django >= 1.11, <= 4.0

## Todo
- [ ] Tests could be more readable
- [ ] Signals decorators
