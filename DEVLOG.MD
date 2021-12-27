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

