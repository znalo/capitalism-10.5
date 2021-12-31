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

Time comparison extended to sales, money, consumption and production goods

TODO revenue step - need to transfer profit to the capitalists
TODO accumulation step - need to use the profit to expand
TODO time comparison for other magnitudes
* Supply, demand, etc
TODO superstates
TODO double header
TODO project selection
TODO history clickable selection of comparator
TODO choice of displaying value, quantity, price

## Commit rest and be thankful

TODO 29/12
* Extend the display DONE but some TBAs
* Finish comparisons IN PROGRESS
* Superstate stepper FRAMEWORK ESTABLISHED (ALL TABLE-DRIVEN NOW) BUT REMAINS TO CODE THE SUPERSTATE STEPS
* Commodity totals for quantity price and value either incomplete or incorrect
* Revenue and Accumulate steps
* De-activate disallowed action choices
* Amalgamate Demand and Supply 
* Project selection
* Full initialise vs one project initialise

NOTE the control database either has to be initialized at startup, or we have to assume it is in place.
TODO better to initialize the control database at startup.

## Commit stepping framework in place

## Commit stepping framework working,tested for sequencing but not for timestamp management

TODO rationalise it a bit: the whole thing should be data-driven and DRY

Created a simple dictionary for control substate
Minor tweak to 'next step' logic that does not yet use the dictionary
First commit the current working version

## Commit new dictionary for controlsubstate, not yet in use, but system works

Moved the logic to display the economy view into 'Views' and deleted 'helpers.py'
This logic is now only called from substate.

## Commit moved logic for economy display back into views

