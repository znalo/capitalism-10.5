# Capitalism 10.5
Simulation project based on the [General Theory of Value](https://www.academia.edu/49503297/A_General_Theory_of_Value_and_Money_part_1)

General platform for simulating period circuit representations of a capitalist economy such as Marx's Schemas of reproduction, circuitist approaches, physiocracy or plain old circular flow of income.

A port of [Capitalism 9.0](https://github.com/axfreeman/capitalism-9.0) which was written in JavaFX. Details of the rationale and features are still hosted in the README file of that project

This version written in Django with various extensions including

* Bootstrap (v5)
* Datatables
* Pandas
* Djangorestframework (not used but included as a possible avenue for styling tables, serving other apps, etc)
* Postgres (available as an option for when we deploy, but currently using SQLite for speed purposes)

Since the project was also a learning process, there have been several versions where various features were tested out. To remember what was done, for each of these I've created a file called DEVLOG where I record what was done as a kind of memo. The earlier versions are still on github but as private projects (happy to give access as a collaborator if interested, but I can't think of any special benefits)

DEVLOG.MD contains a record of what I did to create this version (10.5)

In the DEVLOGS folder I put all the old DEVLOGS

Every time I make a commit, I record this in DEVLOG, or at least, that's the discipline I try to self-impose

## to fork this project

You'll need to create a virtual environment.
You can then use Pip to install all the packages (pip freeze - r requirements.txt)
The css and script files are all imported via CDNs in base.html but this should not require action but it could be a bad idea to override them
Should then work out of the box, but I haven't tested this. 

py manage.py loaddata fixtures.json should create an initial database with no projects in it
py manage.py loaddata fixtures_full.json should create an initial database with all projects in it

To contact me use alan.freeman@umanitoba.ca: I haven't been able to add this to my github profile, for reasons I don't understand.




