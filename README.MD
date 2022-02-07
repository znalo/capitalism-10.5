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
## 8 February
  * Can now switch simulations
  * Next steps:
    * Test that we are returning to the latest state of the selected simulation
    * Display some information about the selected simulation
    * debug the actual simulations
    * postpone the delete and restart functionality for now?