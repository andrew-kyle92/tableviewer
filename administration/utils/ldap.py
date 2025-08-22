from ldap3 import Connection
from ldap3.core.exceptions import LDAPException
from django.conf import settings


class Ldap:
    """
    Provides an api like instance for querying LDAP servers.
    Methods: get_users, check_user_exists, ldap_login
    """
    def __init__(self):
        self.ldap_username = settings.COT_LDAP_USERNAME
        self.ldap_password = settings.COT_LDAP_PASSWORD
        self.pd_ldap_username = settings.PD_LDAP_USERNAME
        self.pd_ldap_password = settings.PD_LDAP_PASSWORD
        self.ldap_server_central = 'central.tucsonaz.gov'
        self.ldap_server_city = 'city.tucsonaz.gov'
        self.ldap_server_pd = 'pd.ci.tucson.az.us'
        self.current_server = self.ldap_server_central
        self.domain = self.current_server.split(".")[0]

    def get_users(self, query_string, domain=None):
        # getting users from the central domain
        results = []
        try:
            with Connection(self.current_server, user=f'{self.domain}\\{self.ldap_username}', password=self.ldap_password) as conn:
                if conn.result['description'] == "success":
                    conn.search(
                        search_base="dc=central,dc=tucsonaz,dc=gov",
                        search_scope="SUBTREE",
                        search_filter=f"(name={query_string.lower()}*)",
                        attributes=['name', 'samaccountname', 'mail', "givenName", "sn"]
                    )
                    entries = conn.entries
                    for entry in entries:
                        if entry.mail.value is not None:
                            results.append({
                                "name": entry.name.value,
                                "username": entry.samaccountname.value,
                                "first_name": entry.givenName.value,
                                "last_name": entry.sn.value,
                                "email": entry.mail.value,

                            })

            # making the connection to the city domain
            if domain is None or domain.lower() != 'central' or domain.lower() == 'city':
                self.current_server = self.ldap_server_city
                self.domain = self.current_server.split(".")[0]
                with Connection(self.current_server, user=f'{self.domain}\\{self.ldap_username}', password=self.ldap_password) as conn:
                    user_list = [user['username'] for user in results]
                    if conn.result['description'] == "success":
                        conn.search(
                            search_base="dc=city,dc=tucsonaz,dc=gov",
                            search_scope="SUBTREE",
                            search_filter=f"(name={query_string.lower()}*)",
                            attributes=['name', 'samaccountname', 'mail', "givenName", "sn"]
                        )
                        entries = conn.entries
                        for entry in entries:
                            if entry.mail.value is not None and entry.samaccountname.value not in user_list:
                                results.append({
                                    "name": entry.name.value,
                                    "username": entry.samaccountname.value,
                                    "first_name": entry.givenName.value,
                                    "last_name": entry.sn.value,
                                    "email": entry.mail.value,

                                })

            # making the connection to the PD domain
            if domain is None or domain.lower() != 'central' or domain.lower() != 'city':
                self.current_server = self.ldap_server_pd
                self.domain = self.current_server.split(".")[0]
                with Connection(self.current_server, user=f'CN={self.pd_ldap_username},OU=ServiceAccounts,OU=_Restricted,DC=pd,DC=ci,DC=tucson,DC=az,DC=us',
                                password=self.pd_ldap_password) as conn:
                    user_list = [user['username'] for user in results]
                    if conn.result['description'] == "success":
                        conn.search(
                            search_base="OU=Exchange,OU=Users,OU=TPD,DC=pd,DC=ci,DC=tucson,DC=az,DC=us",
                            search_scope="SUBTREE",
                            search_filter=f"(name={query_string.lower()}*)",
                            attributes=['name', 'samaccountname', 'mail', "givenName", "sn"]
                        )
                        entries = conn.entries
                        for entry in entries:
                            if entry.mail.value is not None and entry.samaccountname.value not in user_list:
                                results.append({
                                    "name": entry.name.value,
                                    "username": entry.samaccountname.value,
                                    "first_name": entry.givenName.value,
                                    "last_name": entry.sn.value,
                                    "email": entry.mail.value,

                                })

            return True, results
        except LDAPException as e:
            print('Unable to connect to LDAP server')
            print(e)
            return False, {'results': e}

    def check_user_exists(self, username, method):
        filter_type = "samaccountname" if method == "username" else "mail"
        try:
            with Connection(
                    server=self.current_server,
                    user=f"{self.domain}\\{self.ldap_username}",
                    password=self.ldap_password) as conn:
                if conn.result["description"] == "success":
                    conn.search(search_base=f"dc={self.domain},dc=tucsonaz,dc=gov",
                                search_filter=f"({filter_type}={username})",
                                attributes=["*"]
                                )
                    results = conn.entries, self.domain
            if len(results[0]) < 1:
                self.current_server = self.ldap_server_city
                self.domain = self.current_server.split(".")[0]
                with Connection(
                        server=self.current_server,
                        user=f"{self.domain}\\{self.ldap_username}",
                        password=self.ldap_password) as conn:
                    if conn.result["description"] == "success":
                        conn.search(search_base=f"dc={self.domain},dc=tucsonaz,dc=gov",
                                    search_filter=f"(samaccountname={username})",
                                    attributes=["*"]
                                    )
                        results = conn.entries, self.domain
                if len(results) > 0:
                    return conn.entries, self.domain
                else:
                    return False, "User doesn't exist in the central and city domain"
            else:
                return conn.entries, self.domain
        except LDAPException as e:
            print(f"User doesn't exist\nError: {e}")
            return [], e

    # The section below is not used as we are using a different method for ldap login.
    def ldap_login(self, username, password, domain):
        if domain != "central":
            self.current_server = self.ldap_server_city
            self.domain = self.current_server.split(".")[0]
        try:
            with Connection(self.current_server, user=f'{self.domain}\\{username}', password=password) as conn:
                if conn.result['description'] == "success":
                    user_data = {}
                    conn.search(
                        f"dc={self.domain},dc=tucsonaz,dc=gov",
                        f"(samaccountname={username})",
                        attributes=['*']
                    )
                    results = conn.entries
                    user_data["id"] = results[0]["objectSid"].value
                    user_data["first_name"] = results[0]["givenName"].value
                    user_data["last_name"] = results[0]["sn"].value
                    user_data["username"] = results[0]["samaccountname"].value
                    user_data["email"] = results[0]["mail"].value
                    return True, user_data
                else:
                    print("User authentication failed")
                    return False, None
        except LDAPException:
            print("Unable to connect to LDAP server")
            return False, None
