// ********** Imports **********
import * as fetches from "./fetches";
import * as functions from "./functions";

// ***** Script Functions *****
// adding the selected user to the table
// takes 3 arguments: data = <JSON>{objectData}, <str>tableId, <str>membership
function addRowToTable(data, tableId, membership) {
    let memberId = data["id"];
    delete data["id"];
    // getting table
    let table = document.getElementById(tableId);
    // getting the tbody
    let tbody = table.querySelector("tbody");
    // create tr
    let tr = document.createElement("tr");
    tr.id = `member-${memberId}`;
    tbody.appendChild(tr);
    // creating the table data
    for (let key in data) {
        let td = document.createElement("td");
        td.innerText = data[key];
        tr.appendChild(td);
    }
    // adding the action links
    let actionsTd = document.createElement("td");
    actionsTd.className = "d-flex justify-content-evenly"
    if (membership === "member") {
        actionsTd.innerHTML = `<a role="button" class="member-remove-btn text-danger" data-member-id="${memberId}" title="Remove member"><i class="fa-solid fa-square-minus"></i></a> | 
                                <a role="button" class="upgrade-to-owner-btn text-success" data-member-id="${memberId}" title="Make owner"><i class="fa-solid fa-arrow-up-from-bracket"></i></a>`;
    } else if (membership === "owner") {
        if (tableId === "membersTable") {
            actionsTd.innerHTML = `<a role="button" class="member-remove-btn text-danger disabled" data-member-id="${memberId}" title="Can't remove because the member is an owner.<br>To remove from group, remove them from the owners tab."><i class="fa-solid fa-square-minus"></i></a>`;
        } else {
            actionsTd.innerHTML = `<a role="button" class="owner-remove-btn" data-member-id="${memberId}"><i class="fa-solid fa-square-minus"></i></a>`
        }
    } else {
        actionsTd.innerHTML = `<a role="button" class="table-remove-btn text-danger" data-table-id="${memberId}" title="Remove table"><i class="fa-solid fa-square-minus"></i></a>`;
    }
    tr.appendChild(actionsTd);
}

async function removeMember(memberId, groupId, membership, fullRemove=false) {
    let res = await fetches.removeMemberFromGroup(memberId, groupId, membership, fullRemove);
}

// ***** Script Variables *****
let currentUrl = new URL(document.URL);

if (currentUrl.pathname.includes("/administration/")) {
    window.addEventListener("DOMContentLoaded", async function () {
        // ***** User Logic *****

        // ***** Group Logic *****
        if (currentUrl.pathname.includes("/administration/view-group/")) {
            const groupId = parseInt(/view-group\/(?<groupId>\d+)\//g.exec(currentUrl.pathname).groups.groupId);
            let memberAddBtn = document.getElementById("memberAddBtn");
            let ownerAddBtn = document.getElementById("ownerAddBtn");
            let tableAddBtn = document.getElementById("tableAddBtn");

            memberAddBtn.addEventListener("click", async function () {
                let memberFirstName = document.getElementById("memberFirstName").value;
                let memberLastName = document.getElementById("memberLastName").value;
                let filterBy = {
                    filter_by: {
                        "first_name": memberFirstName,
                        "last_name": memberLastName,
                    }
                }
                // check to make sure the user exists within the database (ldap excluded)
                let res = await fetches.checkUserExists(filterBy);
                if (res.exists) {
                    let addRes = await fetches.saveMemberToGroup(res.user.id, groupId);
                    if (addRes.success) {
                        addRowToTable({
                            id: res.user.id,
                            firstName: res.user.first_name,
                            lastName: res.user.last_name,
                        }, "membersTable", "member");
                    }
                }
            });
        }
    });
}