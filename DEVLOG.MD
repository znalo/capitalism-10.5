## Basic setup

`py -m venv capenv`
`activate capenv`
`pip install django`
`py -m pip install --upgrade pip`

(Copy the requirements file from 10.3)

`py -m pip install -r requirements.txt`
`django-admin startproject capitalism`
`cd capitalism`
`py manage.py startapp economy`
`py manage.py migrate`
`py manage.py createsuperuser`
`py manage.py runserver`

## Commit Initial Install

To make the migrations work, 
* created the `Models` folder 
* and placed in it an __init__.py file which imports all the models, to make it into a package

(This was the key thing that went wrong with 10.3)

Now working, as far as we got

## Commit ported 10.3 to this new version

Added Control Menu in navbar that takes its input from ControlSuperStates

## Commit primitive control menu, no actions as yet

Added actions, no progression yet

## Commit actions, no progression yet

* NOTE: we're using @staticmethods in general to get the logic clear. But we could consider @classmethods
* See https://www.programiz.com/python-programming/methods/built-in/classmethod
* Main disadvantage of static method seems to be that we can't easily subclass. But in the use cases so far, we don't want to.
* But see also https://www.geeksforgeeks.org/class-method-vs-static-method-python/
* Classmethod has access to the state of the class.
* However, we store all state information in the DB, so I don't think we need class state variables as such
* Keep a watching brief on this as development proceeds

Templates and Tags: see https://realpython.com/django-template-custom-tags-filters/#string-filters

Stepping is now implemented (but for substates only)

## Commit stepping implemented (substates only)

Time Comparison Color change (method works, has to be extended to all magnitudes)

## Commit Time comparison Color Changes working; to be extended to all magnitudes
