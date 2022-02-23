import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, "README.md"), errors="replace").read()
except TypeError:
    README = ""

setup(
    name="django-tracking-model",
    version="0.1.5",
    packages=["tracking_model"],
    description="Track changes made to django model instance fields.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="drozdowsky",
    author_email="hdrozdow+github@pm.me",
    url="https://github.com/drozdowsky/django-tracking-model/",
    license="MIT",
    install_requires=[
        "Django>=1.11",
    ],
)
