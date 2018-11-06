import circa.settings

# Simple script for  keys so it's easier to switch between test and production keys. 
# REMOVE FROM VERSION CONTROL AFTER POPULATING KEYS
def secret_key():
    if circa.settings.DEBUG:
        return #STRIPE TEST SECRET KEY
    else:
        return #STRIPE LIVE SECRET KEY
def public_key():
    if circa.settings.DEBUG:
        return #STRIPE TEST PUBLIC KEY
    else:
        return #STRIPE LIVE PUBLIC KEY

# Stripe Connect Keys:
def test_client_id():
    return #STRIPE CONNECT TEST KEY
def client_id():
    return #STRIPE CONNECT LIVE KEY

# Keys for Mandrill access.  The test key is to be used solely in the test suite.
def mandrill_key():
    return #MANDRILL LIVE KEY
def mandrill_test_key():
    return #MANDRILL TEST KEY

# Keys for Facebook integration.
def facebook_app_id():
    return #FACEBOOK APP ID

def facebook_app_secret():
    return #FACEBOOK APP SECRET

# NOTE: These keys will ONLY work on localhost.  They are not compatible with production.
def facebook_test_app_id():
    return #FACEBOOK TEST APP ID

def facebook_test_app_secret():
return #FACEBOOK TEST APP SECRET
