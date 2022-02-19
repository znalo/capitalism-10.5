# Capitalism 10.5

Simulation project based on the [General Theory of Value](https://www.academia.edu/49503297/A_General_Theory_of_Value_and_Money_part_1)

General platform for simulating period circuit representations of a capitalist economy such as Marx's Schemas of reproduction, circuitist approaches, physiocracy or plain old circular flow of income.

A port of [Capitalism 9.0](https://github.com/axfreeman/capitalism-9.0) which was written in JavaFX. Details of the rationale and features are still hosted in the README file of that project

To contact me use alan.freeman@umanitoba.ca: I haven't been able to add this to my github profile, for reasons I don't understand.

## Production version
At 30 January 2022 this is now running at [this experimental site](www.dascapital.org)

## Buglist 
### Project 1
Too much money is allocated to industries in the distribution stage

## Changes
### 1 February 2022
  * Fixed problems with tables because jquery version was wrong
  * Fixed trace display did not display all entries
  * The above migrated to the live site  
## 2 February 2022
  * Improvements to trace display
  * Fixed problem in the investment step, in which replenishment demand was incorrectly calculated
  * The above migrated to the live site
## 2 february 2022 pm
  * Fixed problem that project table needs to be initialized by the administrator, for all users to avail themselves of
  * Began study of project 3
## 4 February
  * Created new model 'Simulation Parameters'
    * Abstracts from 'TimeStamp' all fields that will remain constant throughout a simulation
    * A single standard parameter object is created at signup, on a per-user basis
  * Created Scaffolded User Dashboard. Here the user will be able to
    * Create simulations
    * Manage existing simulations
    The User Dashboard replaces the project selection option
## 5 February
  * New model debugged and tested
  * Next step is to flesh out the user dashboard
## 6 February
  * Added a form to create a new simulation
  * Installed crispy with bootstrap5 (NOTE this will require a pip install in production)
## 7 February
  * New simulation form is working, but with very primitive validation
  * Next steps:
    * better information to the user about which simulation is actually running
    * switch simulation functionality
    * delete simulation functionality
    * restart simulation functionality
    * debug the actual simulations (ONLY simple reproduction is working)
## 7 February
  * Can now switch simulations
  * Next steps:
    * Test that we are returning to the latest state of the selected simulation
    * Display some information about the selected simulation
    * debug the actual simulations
    * postpone the delete and restart functionality for now?
## 8 February
  * A halfway house: internal changes to the models implemented, but dashboard functionality now needs to be restored
## 8 February
  * Dashboard functionality restored: user can create and switch simulations, but cannot delete, restart, download or upload yet
  * We now resume work on debugging the actual projects
## This version now running at www.dascapital.org
## 10 February
  * Now working for multiple periods (with simple reproduction)
  * Next steps:
    * Delete simulation
    * Restart simulation
    * Eliminate project 3 (now redundant)
    * Scaffold an about page
    * Complete the refactoring by making 'simulation' the parameter for all actions
## 10 February
  * Added rudimentary 'about' page
## 11 February
  * Cleaner Dashboard with delete simulation facility
## 12 February
  * Gradually moving all the activities associated with a user, to the current_simulation of a user
  * This is not quite complete, but got us to the point where we can run project 4 though we haven't fully checked the result
## 13 February
  * Check it out: [Capitalism 10.5](www.dascapital.org)
## 14 February
  * price response variable incorporated, along with economy-wide profit rate. However this is not yet displayed. It is Traced, however.
## 15 February
  * refactored to simplify comparator logic
  * we now display the economy-wide data (initial capital, current capital, profit, profit rate)
## 17 February
  * fixes to comparator logic, fixes to capital calculations
## 17 February
  * Trace List can now select level of detail to display. Rudimentary implementation, should be done with dropdown list or spinner, but is helpful
## 18 February
  * Debugged a fault in trade in which industries end up with less money than they should
  * A good opportunity to sharpen up the Trace reporting
## 18 February
  * This one seems to run right through without obvious error so I will migrate it to the site
  * Doesn't do profit rate equalization yet (or at least if it does, I didn't verify it)
  * But the Trace is much more helpful especially for bug tracking, and the logic seems to work OK
## 18 February
  * gonna [rip it up](https://www.youtube.com/watch?v=pc_F3PaYgl0)
  * wiped out migrations and database, encouraged by conversation with Ambrose Andrews, and push it over to the server
  * [understand origins](https://www.youtube.com/watch?v=VH40n5lchQo)
   
  

  


    
