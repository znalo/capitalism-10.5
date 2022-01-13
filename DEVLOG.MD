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