## Developer notes

This version is now working on an [experimental production server](www.dascapital.org)

I've therefore started this new Developer Log, and have hived off the previous notes to 10.5 DEVLOG.MD

## Commit Created rudimentary admin dashboard to view and delete users
TODO security for this action
TODO admin should probably not be able to delete self

## Commit Status page and a short message for new signers

Fixed problems with table display, arising from mismatch of jquery and datatables js scripts
Fixed problem that Trace table displays only partially

## 1 February Commit Bug fixes for Table displays and Trace displays
## 2 February Commit Bug fixes for Trace display and replenishment_demand
## 4 February Commit Introduced Simulation_Parameters Object (before coupling it to the Time Stamp objects)
## 4 February Commit Scaffolded User Dashboard
## 5 February Commit debugged and tested new Simulation_Parameter object and its corresponding structures and actions
## 6 February Commit create new simulation seems to be working; choice of simulations still to be done; validation very primitive so errors in creating simulations will not be trapped
## 7 February Commit switch simulation seems to be working; not tested however that we correctly selected the most recent time stamp
## 7 February Commit minor change, renamed Simulation_Parameter to Simulation, migrated the change, and tested it
## 7 February Commit transitional - refactoring User and Simulation models so that the time stamp and user are both associated with the simulation. This is a halfway house. There is also now a simulation table
## 8 February Commit still transitional. Refactored User and Simulation models so that all actions are conducted by the Simulation, not the User. This works, but user dashboard is not working correctly. Saving as a reference point
## 8 February Commit Refactoring complete. Now we start work on debugging the simulations
## 8 February Commit Refactored version uploaded to production site. Production version is working but development version is generating unexpected errors. Awaiting response to ticket lodged with provider
## 10 February Commit Working and tested with multiple periods per year and simple reproduction
## 10 February Commit added about page
## 10 February Commit this version (with some minor corrections) uploaded to server, where it is now functioning
## 11 February Commit Cleaner Dashboard with delete simulation facility
## 12 February Commit Project 4 (two consumption goods) now seems to run all the way through. Improved reporting
## 13 February Commit Halfway House to refactoring in which objects are owned by simulations, not users. Saved at this point because, well, it's working
## 13 February Commit Yet Another Halfway House. All objects are now owned by the simulation except the Time Stamp, but have funky defaults

Here's what we are trying to do. I'm going to call it the 'big bang' problem
Everything works OK (ish) when the simulation is going
But I need to be able to start the whole thing from scratch
From scratch means
  * Start with a clean database
  * Delete all migrations
  * Create a superuser
  * Go

Now, I've restricted the administrator to create the projects, which is a kind of set-up operation
But, the database objects have no defaults, because nothing exists but they reference each other
Now, the 'initialize' procedure creates all the objects in a rational order, so that is taken care of
However, I don't like defining these objects with null=True and no default. This allows them to exist, for however short a halflife, in a corrupt state
Therefore, I'd like to migrate them, on a new install, with no default and null=False

First I will save everything with a commit called 'shoot the tortoise' which signifies there seems to be an infinite sequence of halfway houses but eventually I hope to get there
Then I will delete the database
Then I will change all the Simulation Foreign Keys so there is no null and no default
Then I will see what happens
Then I will report here

## Commit Shoot the Tortoise
Hey, it worked
 * No animals were injured in the course of this experiment
  * First, because it was a purely mental experiment
  * Second, because Tortoises have shells

## Commit The Tortoise has Landed

Now for the big test which is an install on a new site
We had to fix one line in the url file and the install worked

## Commit ONE LAST CHANGE MADE AND IT WORKS

We now start work on the actual price-value relation, which is at the heart of treatments to date.
The ultimate aim is to allow prices to change independent of values.
  * Historically, there have been three concepts of the way values affect prices, of which the first two are as widespread as they are idiotic. They are
    * prices are simply equal to values
    * prices are equal to the rates of exchange that would equalize profit rates in all industries
    * prices vary dynamically and are driven on the one hand by the relation between demand and supply, and on the other by the movement of capital
  * It is however important to study cases (1) and (2) not as representations of reality but as the abstract basis that allows us to theorise (3) correctly
    * 'correctly' means 'in such a way that it is inductively possible for these prices to correspond to reality'
  * The 'price_response_type' variable allows the user to choose any one of the above three options

In this commit, we 
  * allow the user to create simulations with each of the above three options
  * introduce economy-wide capital, profit, and profit rate

At this point we've calculated this rate and the model doesn't simply break (ie collapse with an error)
Next, we're going to display it.

## Commit prelude to a critique of price-value dynamics...

Removed quite a bit of historical stuff, specifically past datasets and Development Logs. They can be retrieved from the record if 
of historical interest but aren't really useful so carving them out.

Removed 'Initialize' from the main navbar since it's now incorporated in the user dashboard

Digression: refactor so that comparator_time_stamp is an attribute of 'simulation' not of 'time_stamp'
This works for stocks but we haven't applied it to other magnitudes.
We'll track these down by removing the field from the TimeStamp object, but this might not work, so we'll make an interim commit at this point

## Commit interim commit of partially refactored comparator logic
## Commit refactoring complete

Will tidy up by removing some of the '_FK' suffixes which don't seem to be the Django way these things are done
Removed the '_FK' suffix from the 'simulation_FK' attribute of Time Stamp
Migration couldn't cope with it. Steps taken:
  * Delete the database
  * Delete all the migrations
  * Create admin as a superuser
  * Restart
  * Login as admin
  * Go to the administrator dashboard
  * Rebuild the project table

It would be really nice if the last two steps could be automated, so that it becomes impossible to start in a corrupt state

## Commit removed _FK suffix from simulation_FK attribute of TimeStamp and started from scratch
## Commit removed _FK suffix from most objects (and had to start from scratch)
## Commit minor tidy

Shifted economy-wide data (initial_capital, profit, etc) into the TimeStamp Object
Rebuild from scratch (Delete Database, etc) so we have the basis for a clean install
Display economy-wide data with comparisons
Tested perfunctorily

## Commit Economy-wide data recorded and displayed

## Commit Improvements to calculation of capital price, and value; price mechanism yet to be completed but logic in place

Fiddled with the trace list to create a crude facility to limit the display of detail.
TODO this should be done with a dropdown list, or perhaps checkboxes, within the trace list form. But it will do for now.

## Commit Trace List can now select level of detail to display
 * TODO debug 'restart simulation' - at present, this deletes all simulations :-(

## Commit intermediate save of a non-working version prior to refactoring Trace.o and Trace.q
## Commit Trade and Trace now working: debugging produce
## Commit Apparently working verion of refactored step management structure with rudimentary profit equalization logic in place but not checked. Much improved Trace reporting
## Commit rip it up - migration-free restart ready to install on the server
## Commit [The original] (https://www.youtube.com/watch?v=aZ308aOOX04) No changes, just felt the tribute was needed
## [understand origins](https://www.youtube.com/watch?v=VH40n5lchQo) Understand origins
## Commit This version installed on remote server and tested for project 1
