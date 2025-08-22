from django_auth_ldap.backend import LDAPBackend

class LDAPCOTCITY(LDAPBackend):
    settings_prefix = "AUTH_LDAP_CITY_"
