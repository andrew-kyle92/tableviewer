import ldap
from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion
from django.conf import settings

# Set up our necessary values to do our bind with the LDAP server
# Here we are importing sensitive variables from our settings.py file so they don't exist in the repo
AUTH_LDAP_SERVER_URI = "ldap://central.tucsonaz.gov:389"
AUTH_LDAP_BIND_DN = 'CN=' + settings.COT_LDAP_USERNAME + ',OU=Service,OU=Accounts,OU=COT,DC=CENTRAL,DC=TUCSONAZ,DC=GOV'
AUTH_LDAP_BIND_PASSWORD = settings.COT_LDAP_PASSWORD

# Now we do the same for the City server, note the _CITY prefix
AUTH_LDAP_CITY_SERVER_URI = "ldap://city.tucsonaz.gov:389"
AUTH_LDAP_CITY_BIND_DN = 'CN=' + settings.COT_LDAP_USERNAME + ',OU=Service,OU=Accounts,DC=CITY,DC=TUCSONAZ,DC=GOV'
AUTH_LDAP_CITY_BIND_PASSWORD = settings.COT_LDAP_PASSWORD

# This will disable referrals, which is required for the COT LDAP
AUTH_LDAP_CONNECTION_OPTIONS = {ldap.OPT_REFERRALS: 0}
AUTH_LDAP_CITY_CONNECTION_OPTIONS = {ldap.OPT_REFERRALS: 0}

# Search both City and Central
AUTH_LDAP_USER_SEARCH = LDAPSearch("DC=CENTRAL,DC=TUCSONAZ,DC=GOV", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
AUTH_LDAP_CITY_USER_SEARCH = LDAPSearch("DC=CITY,DC=TUCSONAZ,DC=GOV", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

# Map our Django values to the LDAP values
# This will update the name and email with whatever is in LDAP
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
    'username': 'sAMAccountName',
}
AUTH_LDAP_CITY_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
    'username': 'sAMAccountName',
}

# We want to explicitly request the user values update
AUTH_LDAP_CENTRAL_ALWAYS_UPDATE_USER = True
AUTH_LDAP_CITY_ALWAYS_UPDATE_USER = True
# We can cache values to prevent unnecessary traffic to LDAP
AUTH_LDAP_CENTRAL_CACHE_TIMEOUT = 3600
AUTH_LDAP_CITY_CACHE_TIMEOUT = 3600

# Declare the backends that we will be using, both of these are needed to implement our LDAP
# Note that you can define a local backend by putting the backend file in your app directory (not your core directory)
# You would then use this format to include that backend: APP_NAME.FILE_NAME.CLASS_NAME
AUTHENTICATION_BACKENDS = [
    'tableviewer.backends.LDAPCOTCITY',
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
