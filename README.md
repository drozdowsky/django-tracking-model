# Django Tracking Model 🏁
Track changes made to your model's instance.  
Changes are cleared on save.  
This package is intented to be used mainly with signals.  
Mutable fields (e.g. JSONField) are not handled with deepcopy to keep it fast and simple.  
Meant to be model_utils's FieldTracker fast alternative.


## Usage
```python
from django.db import models
from tracking_model import TrackingModelMixin

# order matters
class Example(TrackingModelMixin, models.Model)
    text = models.TextField(null=True)
    self = models.ForeignKey("self", null=True)
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
DTM will also detect changes made to ForeignKey/OneToOne fields
```python
In [1]: Example.objects.create(self=e)
In [2]: e.self = None
In [3]: e.tracker.changed
Out[1]: {"self_id": 1}
```

## Requirements
 * Python >= 2.7, <= 3.7
 * Django >= 1.9, <= 2.2

## Todo
 - [ ] mutable fields tests
