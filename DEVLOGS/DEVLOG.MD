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

TODO revenue step - need to transfer profit to the capitalists DONE
TODO accumulation step - need to use the profit to expand
TODO time comparison for other magnitudes
* Supply, demand, etc
TODO superstates DONE
TODO double header DONE but needs improvement
TODO project selection
TODO history clickable selection of comparator
TODO choice of displaying value, quantity, price

## Commit rest and be thankful

TODO 29/12
* Extend the display DONE but some TBAs
* Finish comparisons IN PROGRESS
* Superstate stepper DONE
* Commodity totals for quantity price and value either incomplete or incorrect DONE
* Revenue and Accumulate steps DONE exept for last step
* De-activate disallowed action choices DONE
* Amalgamate Demand and Supply DONE
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

Data-driven stepping mechanism in place - substates only

## Commit data-driven stepping mechanism in place

Changed folder name to 'capitalism 10.5' after discarding a branch
Stepping now works, or seems to at a first run through


## Commit data-driven stepping now works

TODO move single control group for substep and superstep DONE
TODO we need to switch between quantity, value and price display

Initial capital introduced
TODO all stocks in the second table should be denominated in currency DONE

## Commit Initial Capital calculated

Comparators extended
Main logic for capital in place; some bugs remain

## Commit logic for capital and profit in place but some bugs remain

Log table spruced up with styling for object names and quantities, plus elementary collapse functionality
TODO complete collapse functionality PARTLY DONE

## Commit spruced up Log table

TODO complete circuit debug DONE
TODO Refresh should not repeat the action, only refresh the display

Tracking down bug in trade
Log display approaching the usable

## Commit Log display nearly usable

Some debugging

## Commit current capital, profit and profit rate now working, tested on Project 1

Rationalised static folder

## Commit reorganised static folder

Trimmed logging with "verbose/clean" setting
TODO rationalise what information is given to the user in clean mode DONE
TODO fix the Logging Table control buttons DONE
TODO make the table button group sticky

Very crude investment mechanism sketched out
Very last hurdle (to allocate the money) still to be done
But note that since we haven't introduced any money constraints, actually, the circuit can just proceed - if the money allocation is wrong, the industry will just go into debt
TODO impose some kind of monetary constraint

## Commit preparing to implement the investment action

Prior to implementation, some tidying up to try and create consistent naming for the various methods
and see if we can reduce the database hits. Since I'm not very familiar with Django internals, I'll 
use SILK to try and profile what's going on.

## Some name tidying and a commit


TODO Outstanding, in priority order
* time comparison for other magnitudes
* project selection
* history clickable selection of comparator
* complete collapse functionality 
* choice of displaying value, quantity, price
* impose some kind of monetary constraint
* accumulation step - need to use the profit to expand
* double header improve readability
* Session management


Created fixtures in case we need to start from scratch somewhere
Moved the complete set of data files back to the development area so we now load all 8 projects
Now we want to have a project selector

## Commit full dataset re-instated (all 8 projects, note project 7 never worked)

Removed all the 'verbose_names' from States and tested, including Admin.
Reason is that we don't use them so they just get in the way

Simplified navbar, basically just to include everything and be sticky at the top (so we can fit in the projec change, and worry later about where it should go)

## Commit simplified navbar

Switch to W3 - much simpler

## Commit switch to W3 before ditching bootstrap

Tidy up the css and js fetching
Finally created a navbar that sticks and allows dropdowns
Image for the landing page and experimented (unsuccessfully) to make it a background image with lower opacity (so table headers are visible)

## Commit navbar with dropdowns working; tidied up script and css loading

Project selection seems to be working

## Commit project selection installed (but not fully tested)

## Commit landing page with logo well-positioned

Investment stage code complete and the simulation now goes right round the circuit. But the money allocated seems to be wrong. To be debugged. But commit now because code is complete

## Commit investment step complete but needs to be debugged

Some more styling for the tables.
Comparator is wrong because instead of comparing with the previous superstate, it compares with the previous substate
TODO fix up the whole comparator thing.

## Commit table styling

Added sidebar and moved some menu items into it, to make space for the comparator table

## Commit sidebar added, some script rationalisation 

Created the stepping list but as yet haven't fixed the comparator

## Commit step selector list created; does not yet change the comparator

Created debug profile (which now works)
Tighted up initialize to try and eliminate the occasional problem of corrupt start point
Extracted 'initilize' as separate file, for ease of access

## Commit debug profile created; initialize abstracted as separate file

Simulation now working almost correctly for project 1 (Capitalists seem to keep losing money, but this can be fixed)

## Commit SR working for several periods almost correctly

TODO Outstanding, in priority order
* history clickable selection of comparator PART DONE
* extra time stamp for a superstate
* collapse functionality 
* choice of displaying value, quantity, price
* deploy?
* impose some kind of monetary constraint DON'T DO THIS YET IF AT ALL

Fixed up so user can click on an item in history and return parameters giving the superstate and the substate

## Commit clickable history created

TODO We need to make the naming a bit clearer. Try to move towards this: a 'State' consists of a period, a 'stage' and a 'step' DONE
TODO The period needs to be included in the history DONE
TODO Maybe: do we need an extra time stamp for the start of a state?

Renamed most references to 'substate' to 'step', and tested most functions
 
## Commit: refactor to rename 'substate' to 'step'

Renamed most references to 'superstate' to 'stage', and tested most functions
Created new fixture 'fixtures_15.01.2022 and deleted all old fixtures.
Did not move the new fixture into the fixtures folder yet

## Commit: refactor to rename 'superstate' to 'stage'

Comparator select now seems to be working
Fixtures file updated

## Commit: comparator select seems to be working

TODO Outstanding, in priority order
* Streamline the display of compared quantities. Is currently inconsistent.
* extra time stamp for a superstate?
* collapse functionality 
* choice of displaying value, quantity, price
* deploy?
* impose some kind of monetary constraint DON'T DO THIS YET IF AT ALL

Project 1 now working (at the end of a complete circuit, it is back to where it was)
Minor problems:
* demand and supply are not reset to their initial levels. This is not an error as such but could confuse the user
* similarly initial and current capital.

## Commit: project 1 working

Getting ready to establish production version 
trying DjangoEurope

Remove all the API stuff - we are not using it
Moved all configuration to economy app - the standard install doesn't realy justify keeping it separate
The strategy (initially, who knows if it will work) is basically to copy the entire economy app into a placeholder we will create on the host

Probably time for a commit

## Commit: localise everything in the economy app

Now trying to get ready for production (on djangoeurope at www.dascapital.org)
Hence remove as many quirks and peculiarities as possible
Since 'economy' is the only app, we propose to dispense with many if not all of Django's help with locating directories and simplify the folder structure as much as possible

Place all templates simply in 'economy/templates' (Note we cannot set APP_DIRS to false because it raises objections which we're not sure have answers in this production environment)
Put this directory into TEMPLATES.DIRS in settings

## Commit: templates now localised in economy app

Removed unused installs

## Commit: removed unused installs

Created variables in settings to reference static data files via django (staticfiles_storage.path)

## Commit: rationalised static storage in preparation for deployment

Rationalise the migrations. We don't really need the history (it should be stored in .git anyhow because I did not create a .gitignore) so
it will be cleaner to have one single migration at this point, when we are moving over to production. Following the procedure in this
[stackoverflow](https://stackoverflow.com/questions/58000680/django-safely-remove-old-migrations) answer 5, namely

  * Use the python manage.py migrate your_app_name XXXX in case you want to unapply migrations after the XXXX migration. Otherwise use python manage.py migrate your_app_name zero to completely unapply all migrations.

  * Remove the .pyc files under /migrations/_pycache_/ that you have unapplied.

  * Remove the .py files under migrations/ that you have unapplied.

  * If what you're looking for is to squash all the migrations into one, do the steps above removing all migrations and then run python manage.py makemigrations your_app_name to create a single migration file. After that just run python manage.py migrate your_app_name and you're done.

## Commit before squashing migrations, just in case
Ran into a problem with migration 10 - it says there is an integrity error
## Commit after removing all migrations as far back as 0010
Start the simulation and re-initialize

Actually, all this is not relevant to what we are doing now.
It's written on the assumption that the user already has a database, whose integrity must be maintained.
But we are at the development stage when we are always starting from scratch, so the problem does not arise.
We simply delete the old database and start over.
The real difficulty is that the database must be initialised, and the question is 'when'?
This relates to the problem, not yet addressed, of multiple users.

At what point do we start with a clean database?
And what should a clean database consist of?

There are two solutions:

(1) a clean database means a skeleton, in which there is just one timestamp and one state, and nothing else
(2) a clean database means a database with one complete project

The goal is (2) eventually
But (1) is easier and is also a 'recovery from failure' position.
Recall that in 'initialize' as at present constituted, the whole database is wiped out and reconstructed so any temporary but partial failsafe will be removed.
The point of a failsafe is that the site should allow the user to re-initialize, rather than falling over.

So we will first try to construct a little 'failsafe' procedure to be invoked when the state is found to be corrupt.
This should ideally also do a database dump but that's beyond our scope right now because it would get us into all the complications of serialization which we want to avoid until we're running in a production environment

(It could, however, do a dump of the Log table...)

State of play after much messing around:
* owner field removed from the state models. It should be put back in when we introduce proper login and authorization
* A 'failsafe' database is established by the landing page, if on arrival it is found that the State object is not initialized
* Tested starting from scratch by deleting the sqlite database and restarting
* created a new fixture file and reloaded it
* ran complete simulation of project 1
* examined all tables

We'll now make a commit of this working version

## Commit working version with failsafe initialization and fixture file

* This now works in the development version on the djangoEurope site (www.dev.dascapital.org)
* But the production version does not (as of 22 January). 
* We're working on that, but I think it's an install problem, so I'm assuming for now this version is good to go for production.

Added .gitignore, which should have been done a long time ago.

## Commit this is now assumed to be ready for production

Now working on the user model and logging in
This is needed so each user has a separate simulation model
At present everyone shares the same model, which is a bit weird - makes it like a multi-user video game
Would be interesting to explore as an option, but for now, we want to isolate each user experience

First off is to have a consistent user field throughout.
Following the practice explained in [Matt Friere's excellent course] (https://learn.justdjango.com/courses/getting-started-with-django/custom-user)

* TODO
 * User Model
  * use the django user model (from django.contrib.auth import get_user_model) throughout
  * rebuild the failsafe and initialization functions so that they create databases on a per-user basis
  * NOTE this means we cannot re-initialize the entire database just because one user's sim falls over
  * So the database becomes permanent and must be monitored for faults, properly maintained, etc
  * which suggests we need to develop some tests

 * Reporting
  * We should distinguish between Reporting and Logging
  * Reporting produces a user-friendly account of the simulation which allows the user to see what's been going on
  * Logging is for database maintenance
  * for this we need some kind of logging framework

It can be seen from the above that there are three related problems which need to be attacked in some kind of systematic way
  * User model
  * Database maintenance
  * Logging

Start with the user model, which from a design viewpoint is probably the worst place to start, but we need to figure out how the thing works before moving on to logging and DB maintenance. So this is not just a design exercise but a learning exercise.

First stab at introducing the user model - no functionality yet, just seeing what breaks

## Commit first tentative user model fields

* Decouple logging from reporting - start
  * (Moving this file to the folder DEVLOGS)
  * Created PRODUCTION_NOTES.MD to record changes that we need to ensure are in the production version
  * In 'settings' add the code from [this blog](https://www.freecodecamp.org/news/logging-in-python-debug-your-django-projects/)

Actually, the [docs](https://docs.djangoproject.com/en/3.2/topics/logging/#examples) are quite comprehensible
There seems to be a bug in the logging.Streamhandler so we get a broken pipe instead of an error message
But we only want file output anyhow, so we'll stick with a barebones for now.

* Very simple logging system created - just fires off info report to 'debug.log' - which is enough for now.

## Commit rudimentary logging system established
Separated `Log` out as a separate class in the file `report.py`
 (TODO this should be refactored to be named `Report`)
## Commit separate Log class created

We now added a 'user' class to all models, modified Initialise so it only initializes the logged in user, and tested this for one user (me)
* TODO table display should select only what the logged in user owns
* TODO in general, all functionality should be user-specific
* TODO some unit tests of integrity and isolation

First, construct some kind of authentication and logging in system

## Commit initial step in user isolation: models defined, and initialization

