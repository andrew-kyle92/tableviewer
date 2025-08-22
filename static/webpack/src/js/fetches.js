// ********** Imports **********
import { csrftoken } from "./functions";

// ********** Fetch Requests **********
export const fetchSaveColumn = async (data) => {
    let url = document.URL.includes("tableviewer") ? '/tableviewer/save-column/' : '/save-column/';
    return await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(data),
    }).then(async (response) => {
        return response.json();
    });
}

export const fetchRegenerateColumns = async (table_id) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/regenerate-columns/${table_id}` : `/regenerate-columns${table_id}`;
    return await fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrftoken,
        },
    }).then(async (response) => {
        return response.json();
    });
}

export const fetchAddUrlShortcut = async (table_id, shortcut) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/add-url-shortcut/${table_id}` : `/add-url-shortcut/${table_id}`;
    url = url + "?" + new URLSearchParams({shortcut: shortcut});
    return fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers: {
            "X-CSRSToken": csrftoken
        }
    }).then(async response => {
        return response.json();
    });
}

export const fetchRemoveShortcut = async (shortcutId) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/remove-shortcut/` : `/remove-shortcut/`;
    url = url + "?" + new URLSearchParams({"shortcutId": shortcutId});
    return fetch(url, {
       method: "GET",
       credentials: "same-origin",
       headers: {
           "X-CSRFToken": csrftoken
       }
    }).then(async response => {
        return response.json();
    });
}

export const fetchDomainName = async () => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/get-domain-name/` : `/get-domain-name/`;
    return fetch(url, {
       method: "GET",
       credentials: "same-origin",
       headers: {
           "X-CSRFToken": csrftoken
       }
    }).then(async response => {
        return response.json();
    });
}

export const saveTableSettings = async (data) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/save-table-settings/` : `/save-table-settings/`;
    return await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(data),
    }).then(async (response) => {
        return response.json();
    });
}

export const saveMemberToGroup = async (userId, groupId) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/administration/change-user-membership/` : `/administration/change-user-membership/`;
    url = url + "?" + new URLSearchParams(
        {
            user_id: userId,
            group_id: groupId,
            change_type: "add",
            membership: "member",
        }
    );
    return fetch(url, {
       method: "GET",
       credentials: "same-origin",
       headers: {
           "X-CSRFToken": csrftoken
       }
    }).then(async response => {
        return response.json();
    });
}

export const saveOwnerToGroup = async (memberId, groupId) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/administration/save-to-group/` : `/administration/save-to-group/`;
    url = url + "?" + new URLSearchParams({memberId: memberId, groupId: groupId, membership: "owner"});
    return fetch(url, {
       method: "GET",
       credentials: "same-origin",
       headers: {
           "X-CSRFToken": csrftoken
       }
    }).then(async response => {
        return response.json();
    });
}

export const removeMemberFromGroup = async (userId, groupId, membership, fullRemove=false) => {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/administration/change-user-membership/` : `/administration/change-user-membership/`;
    url = url + "?" + new URLSearchParams(
        {
            user_id: userId,
            group_id: groupId,
            change_type: "remove",
            membership: membership,
            full_remove: fullRemove,
        }
    );
    return fetch(url, {
       method: "GET",
       credentials: "same-origin",
       headers: {
           "X-CSRFToken": csrftoken
       }
    }).then(async response => {
        return response.json();
    });
}

export const fetchLdapUsers = async (searchQuery) => {
    let urlPath = new URL(document.URL).pathname.includes("tableviewer") ? '/tableviewer/administration/fetch-ldap-users/?': '/administration/fetch-ldap-users/?';
    let url = urlPath + new URLSearchParams({
       "q": searchQuery
    });

    return await fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrftoken
        }
    }).then(async (response) => {
            return response.json();
    });
}

export const checkUserExists = async (filterBy) => {
    let url = new URL(document.URL).pathname.includes("tableviewer") ? '/tableviewer/administration/check-user-exists/': '/administration/check-user-exists/';

    return await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(filterBy),
    }).then(async (response) => {
            return response.json();
    });
}

export const getInstances =  async (queryData) => {
    let url = new URL(document.URL).pathname.includes("tableviewer") ? '/tableviewer/administration/get-instances/': '/administration/get-instances/';
    let fullUrl = url + "?" + new URLSearchParams({
       "type": queryData.type,
        "filter": queryData.filter,
        "q": queryData.q,
    });
    return await fetch(fullUrl, {
        method: "GET",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrftoken,
        }
    }).then(async (response) => {
        return response.json();
    });
}