This code to go in settings

AUTH_USER_MODEL='economy.User'

make sure to set up LOGGING so it's harmonised with this version

EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'

(We may want to change LOGIN_REDIRECT_URL but at present it just goes to the landing page so that's cool for now)

