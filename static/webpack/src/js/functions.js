// ********** Importing the fetches **********
import * as fetches from "./fetches";

// ********** Getting the csrf token for the fetch calls **********
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
export const csrftoken = getCookie('csrftoken');

// ********** async functions **********
export async function copyToClipboard(text) {
    await navigator.clipboard.writeText(text);
}

export async function saveColumn(data, btnParent, tableRow){
    let res = JSON.parse(await fetches.fetchSaveColumn(data));
    if (res.errors) {
        writeAlert(res.errors);
        return false;
    }
    else if (res.results.success) {
        let resData = JSON.parse(res.results.data);
        // adding the fields to the correct table cells
        let useColumnTitleCase = resData["use_column"].toString()[0].toUpperCase() + resData["use_column"].toString().substring(1);
        tableRow.children[0].innerText = useColumnTitleCase; // use column cell
        tableRow.children[2].innerText = resData["label"]; // label cell
        // updating the data-column-data data
        let editBtn = btnParent.querySelector(".column-edit-btn");
        editBtn.dataset.columnData = res.results.data;
        // removing the save and cancel buttons
        let saveBtn = btnParent.querySelector("#save-btn");
        let cancelBtn = btnParent.querySelector("#edit-btn");
        btnParent.removeChild(saveBtn);
        btnParent.removeChild(cancelBtn);
        // un-hiding the edit button
        editBtn.hidden = false;
        // flashing the table-row as success
        tableRow.classList.add("flash-success");
        writeAlert("success", "Column saved")
        // setting data-table-editing to false
        tableRow.dataset.tableEditing = "false";
    }
}

export async function addURLShortcut(shortcutData) {
    // getting the domain name
    let res = JSON.parse(await fetches.fetchDomainName());
    let domainName = res["domainName"];
    // parentDiv
    let parentDiv = document.getElementById("url-shortcuts");
    // creating the shortcut structure
    // - outer div
    let shortcutDiv = document.createElement("div");
    shortcutDiv.className = "input-group mb-3";
    shortcutDiv.id = `shortcut-${shortcutData.id}`;
    parentDiv.appendChild(shortcutDiv);
    // - domain span
    let domainSpan = document.createElement("span");
    domainSpan.className = "input-group-text";
    domainSpan.innerText = domainName;
    shortcutDiv.appendChild(domainSpan);
    let afterDomainP = document.createElement('p');
    afterDomainP.className = "my-auto mx-1";
    afterDomainP.innerText = "/";
    shortcutDiv.appendChild(afterDomainP);
    // - shortcut path split iteration
    let shortcutSplit = shortcutData.url.split('/');
    for (let i = 0; i< shortcutSplit.length; i++) {
        let path = shortcutSplit[i];
        let span = document.createElement("span");
        span.className = "input-group-text";
        span.innerText = path;
        shortcutDiv.appendChild(span);
        let p = document.createElement('p');
        p.className = "my-auto mx-1";
        p.innerText = "/";
        shortcutDiv.appendChild(p);
    }
    // - copy button
    let copyBtn = document.createElement("button");
    copyBtn.className = "copy-url-button btn btn-outline-secondary";
    copyBtn.dataset.urlId = shortcutData.id;
    copyBtn.dataset.link = domainName + "/" + shortcutData.url;
    copyBtn.innerHTML = `<i class="fa-solid fa-copy"></i>`;
    shortcutDiv.appendChild(copyBtn)
    // adding the listener
    addCopyListener(copyBtn);
    // - delete button
    let deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-url-btn btn btn-outline-secondary";
    deleteBtn.dataset.urlId = shortcutData.id;
    deleteBtn.innerHTML = `<i class="fa-solid fa-trash"></i>`;
    shortcutDiv.appendChild(deleteBtn);
    // adding the listener
    addDeleteListener(deleteBtn);
}

// ********** Script functions **********
export function addCopyListener(element) {
    element.addEventListener("click", async () => {
       let copyText = element.dataset.link;
       await copyToClipboard(copyText);
       writeAlert("success", "Shortcut copied!");
    });
}

export function addDeleteListener(element) {
    element.addEventListener("click", async () => {
        let shortcutId = element.dataset.urlId;
        let res = JSON.parse(await fetches.fetchRemoveShortcut(shortcutId));
        if(res.success === true) {
            let parentDiv = document.getElementById("url-shortcuts");
            parentDiv.removeChild(element.parentNode);
            writeAlert("success", "Shortcut deleted!");
        } else {
            writeAlert("warning", res.error);
        }

    });
}

export function searchTable(id, keyword, column) {
    let url = document.URL.includes("tableviewer") ? `/tableviewer/tables/search-table/${id}/` : `/tables/search-table/${id}/`;
    url = url + '?' + new URLSearchParams({"s": keyword, "c": column});
    window.location = url;
}

export function writeAlert(tag, msg) {
    // adding an alert to the top of the screen
    let alert = document.createElement("div");
    alert.className = `alert alert-${tag} alert-dismissible fade show fixed-top w-25 mt-3 m-auto`;
    alert.role = "alert";
    alert.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    document.body.appendChild(alert);
    setTimeout(() => {
        alert.classList.add("fade-out");
        setTimeout(() => {
            document.body.removeChild(alert);
        }, 1000)
    }, 3000);
}

export function cancelEdit(editBtn, tableRow) {
    // btns parent
    let btnParent = editBtn.parentElement;
    // getting the current data
    let currentData = JSON.parse(editBtn.dataset.columnData);
    // restoring the current values to the respective cells
    let useColumnTitleCase = currentData["use_column"].toString()[0].toUpperCase() + currentData["use_column"].toString().substring(1);
    tableRow.children[0].innerHTML = useColumnTitleCase;
    tableRow.children[2].innerHTML = currentData["label"];
    // removing the save and cancel buttons
    let saveBtn = btnParent.querySelector("#save-btn");
    let cancelBtn = btnParent.querySelector("#edit-btn");
    btnParent.removeChild(saveBtn);
    btnParent.removeChild(cancelBtn);
    // un-hiding the edit button
    editBtn.hidden = false;
    // setting data-table-editing to false
    tableRow.dataset.tableEditing = "false";
}

// ********** Reference function calls **********
const inlineUpdate = async (func, data) => {

}