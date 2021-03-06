import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md"), errors="replace").read()

setup(
    name="django-tracking-model",
    version="0.1.3",
    packages=["tracking_model"],
    description="Track changes made to django model instance.",
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
