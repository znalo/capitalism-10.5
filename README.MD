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
  * TODOs
    * The next step is to create a Foreign Key in the TimeStamp that points to a simulation parameter object
      * Then, we plan that the user gets the option, at the start of a simulation, to modify the simulation parameters
      * This probably means the user will also get the option to re-initialize a single simulation
    * After that, we want to use the new field 'periods_per_year' (in the simulation parameter model)
      * This will replace project 3; it will be a general option, in a simulation, to chop it up into arbitrarily small sub-periods
      * When this happens, capital that was at one time circulating becomes fixed 
      * Hopefully the transition will be taken care of in a straightforward way, since currently the simulation is driven by stock sizes
        * the quantities to be traded, used, or produced are all calculated, not hardwired
        * this is an important departure from the standard Bortkiewicz imposition in which all capital is circulating and is used up in a year
        * it also allows for genuine stock-flow consistency, which is the principle that animates the project
      Bortkiewicz models in effect deduce stocks from flows (by wishing them away)
      We to the contrary deduce flows from stocks


