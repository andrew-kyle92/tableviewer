// ********** Imports **********
import * as fetches from "./fetches";
import * as functions from "./functions";

// ********** Script Variables **********
// ***** Logic for editing table columns on the table-details view *****
export let currentURL = new URL(document.URL);

// ********** Main Content **********
window.addEventListener('DOMContentLoaded', function () {
    // ##### show password button
    if (document.URL.includes("login")) {
        let eyeBtn = document.getElementById("eye-btn");
        let passwordInput = document.getElementById("id_password");
        eyeBtn.addEventListener("click", () => {
            let isHidden = eyeBtn.dataset.status === "hidden";
            if (isHidden) {
                passwordInput.type = "text";
                eyeBtn.dataset.status = "revealed";
                eyeBtn.innerHTML = "<i class='fa-solid fa-eye-slash'></i>";
            } else {
                passwordInput.type = "password";
                eyeBtn.dataset.status = "hidden";
                eyeBtn.innerHTML = "<i class='fa-solid fa-eye'></i>"
            }
        });
    }
    // ################################################################################

    // making sure the correct we're on the correct page
    if (currentURL.pathname.includes('tables/detail')) {
        // getting all column edit buttons
        let editColumnBtns = document.querySelectorAll('.column-edit-btn');
        // adding a listener to each button
        editColumnBtns.forEach(function (btn) {
            btn.addEventListener('click', () => {
                // getting the column data attribute
                let columnData = JSON.parse(btn.dataset.columnData);
                // getting all table-datas (td) within the table-row (tr)
                let tableRow = btn.parentElement.parentElement;
                // setting data-editing attribute to true
                tableRow.dataset.tableEditing = 'true';
                // creating a JSON object for each editable table column
                // which should only be indexes 0 and 2
                let currentActive = tableRow.children[0].innerText === "True";
                let editableColumns = {
                    0: {current: tableRow.children[0].innerText, new: `<input id='use_column_new-${columnData["id"]}' class='form-check-input' type='checkbox'>`},
                    2: {current: tableRow.children[2].innerText, new: `<input id='label_new-${columnData["id"]}' class='form-control' type='text' value="${tableRow.children[2].innerText}">`}
                }
                for (let key in editableColumns) {
                    tableRow.children[key].innerHTML = "<div class='current-value'>Current:<br>" + editableColumns[key].current + "</div>New:<br>" + editableColumns[key].new;
                    if (currentActive) {
                        let newCheckBox = document.getElementById(`use_column_new-${columnData["id"]}`)
                        newCheckBox.checked = true;
                    }
                }

                // creating a cancel and save button and hiding the edit button
                let editBtnParent = btn.parentElement;
                // hiding the edit button
                btn.hidden = true;
                // save button
                let saveBtn = document.createElement("button");
                saveBtn.id = "save-btn";
                saveBtn.className = "btn btn-primary btn-sm me-2";
                saveBtn.type = "button";
                saveBtn.innerText = "Save"
                editBtnParent.appendChild(saveBtn);
                // cancel button
                let cancelBtn = document.createElement("button");
                cancelBtn.id = "edit-btn";
                cancelBtn.className = "btn btn-secondary btn-sm";
                cancelBtn.type = "button";
                cancelBtn.innerText = "Cancel"
                editBtnParent.appendChild(cancelBtn);
                // adding the button logic
                saveBtn.addEventListener("click", async () => {
                    let newUseColumnInput = document.getElementById(`use_column_new-${columnData['id']}`);
                    let newLabelInput = document.getElementById(`label_new-${columnData['id']}`);
                    let colData = {
                        id: columnData["id"],
                        use_column: newUseColumnInput.checked,
                        label: newLabelInput.value === '' ? columnData["label"] : newLabelInput.value
                    }
                    await functions.saveColumn(colData, btn.parentElement, tableRow);
                    // reloading the iframe to reflect the changes
                    let previewIframe = document.getElementById("table-preview-iframe");
                    previewIframe.contentWindow.location.reload();
                });

                cancelBtn.addEventListener("click", () => {
                    functions.cancelEdit(btn, tableRow);
                });
            });
        });

        // ***** Button Logic *****
        // regenerate column headers
        let regenerateBtn = document.getElementById("regenerate-columns-btn");
        regenerateBtn.addEventListener("click", async () => {
            let tableId = regenerateBtn.dataset.tableId;
            let res = JSON.parse(await fetches.fetchRegenerateColumns(tableId));
            if (res.success) {
                window.location.reload();
            }
            else {
                functions.writeAlert("error", res.error);
            }
        });

        // add url shortcut
        let addURLBtn = document.getElementById("add-url-btn");
        let addURLInput = document.getElementById("new-url");
        addURLBtn.addEventListener("click", async () => {
            let tableId = addURLBtn.dataset.tableId;
            let results = JSON.parse(await fetches.fetchAddUrlShortcut(tableId, addURLInput.value));
            if (results.success === true) {
                await functions.addURLShortcut(results.instance);
                functions.writeAlert("success", "URL Shortcut added");
                addURLInput.value = "";
            }
            else {
                functions.writeAlert("warning", results.error);
            }
        });

        // copy URL to clipboard
        let copyBtns = document.getElementsByClassName("copy-url-btn");
        for (let i = 0; i < copyBtns.length; i++) {
            copyBtns[i].addEventListener("click", async () => {
               let copyText = copyBtns[i].dataset.link;
               await functions.copyToClipboard(copyText);
               functions.writeAlert("success", "Shortcut copied!");
            });
        }

        // remove shortcut
        let deleteBtns = document.getElementsByClassName("delete-url-btn");
        for (let i = 0; i < deleteBtns.length; i++) {
            deleteBtns[i].addEventListener("click", async () => {
                let shortcutId = deleteBtns[i].dataset.urlId;
                let res = JSON.parse(await fetches.fetchRemoveShortcut(shortcutId));
                if(res.success === true) {
                    let parentDiv = document.getElementById("url-shortcuts");
                    parentDiv.removeChild(deleteBtns[i].parentNode);
                    functions.writeAlert("success", "Shortcut deleted!");
                } else {
                    functions.writeAlert("warning", res.error);
                }

            });
        }
    }

    if (currentURL.pathname.includes("tables/detail") || currentURL.pathname.includes("administration/view-group") || currentURL.pathname.includes("administration/")) {
        // ***** Tabs logic *****
        let tabs = document.getElementsByClassName("tab-btn");
        let tabContents = document.getElementsByClassName("tab-content");
        // adding an event listener to each btn
        for (let i = 0; i < tabs.length; i++) {
            let tab = tabs[i];
            let contentId = tab.dataset.target;
            tab.addEventListener("click", () => {
                tab.classList.add("active");
                // un-hiding the tab content
                let tabContent = document.getElementById(contentId);
                let isHidden = tabContent.dataset.hidden === "true";
                if (isHidden) {
                    tabContent.classList.remove("hidden");
                    tabContent.dataset.hidden = "false";
                }
                // hiding all other tabs
                for (let j = 0; j < tabContents.length; j++) {
                    let t = tabContents[j];
                    if (t.id !== contentId && t.dataset.hidden === "false") {
                        t.dataset.hidden = "true";
                        t.classList.add("hidden");
                    }
                }
                // setting other tabs as non-active
                for (let j = 0; j < tabs.length; j++) {
                    let tBtn = tabs[j];
                    if (tBtn.className.includes("active") && tBtn.id !== tab.id) {
                        tBtn.classList.remove("active");
                    }
                }
            });
        }
    }

    if (currentURL.pathname.includes('tables/view') || currentURL.pathname.includes("tables/search-table")) {
        // search mechanic
        let searchBtn = document.getElementById("searchBtn");
        let searchInput = document.getElementById("searchInput");
        let searchDropdown = document.getElementById("searchSelect");
        searchBtn.addEventListener("click", () => {
            let id = searchBtn.dataset.table;
            let keyword = searchInput.value;
            let column = searchDropdown.value;
            functions.searchTable(id, keyword, column);
        });
    }
});