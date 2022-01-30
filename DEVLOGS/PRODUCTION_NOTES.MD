This code to go in settings

AUTH_USER_MODEL='economy.User'

make sure to set up LOGGING so it's harmonised with this version

EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'

(We may want to change LOGIN_REDIRECT_URL but at present it just goes to the landing page so that's cool for now)

LOGOUT_REDIRECT_URL = '/' # new

INSTALLED_APPS add:
  'crispy_forms',
  'crispy_tailwind',

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"

To send emails: start here

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'c3p0manitoba.gmail.com'
EMAIL_HOST_PASSWORD = ''

The django setup stores the registration templates in a different place (dproject/templates).
So the new registration templates have to be copied to it separately

HUGE problem is that Django makes it hard to change the user model midstream. It does not create the new database table 'economy_users'
However, the problem is less messy than if the project is already running with users and a database
In that we should simply be able to remove all the migrations and start over with a clean install.




