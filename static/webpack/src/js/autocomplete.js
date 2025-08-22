// ********** Imports **********
import * as fetches from "./fetches";

// ########## Intellisense Logic ##########
// ##### Script functions #####
async function userExists(userData) {
    // Calls the fetch call checkUserExists to verify
    // if the user already exists in our database
    // data return: {'exists': <boolean>}
    let user = await fetches.checkUserExists(userData);

    // checking the exists key
    return user.exists;
}

function addError(msg) {
    // getting the search input
    let searchInput = document.getElementsByClassName('auto-input')[0];
    // getting the search input's parent
    let parent = searchInput.parentElement;
    // checking to see if the error already exists
    let errorMsg = document.querySelectorAll('[data-user-exists]')[0];
    if (!errorMsg) {
        // creating the error p element
        let errorP = document.createElement('p');
        errorP.setAttribute('class', 'error-msg');
        errorP.dataset.userExists = 'true';
        errorP.innerText = msg;
        parent.appendChild(errorP);

        // adding the validation-error class to the parent
        parent.classList.add('validation-error');
    }
}

// ##### Main Logic #####
const mainInput = document.getElementsByClassName("auto-input")[0];
const mainInputParent = mainInput ? mainInput.parentElement: null;
const usernameInput = document.getElementById("id_username");
const firstnameInput = document.getElementById("id_first_name");
const lastnameInput = document.getElementById("id_last_name");
const emailInput = document.getElementById("id_email");

if (mainInput) {
    let getIntellisense = async (queryParams) => {
        return await fetches.fetchLdapUsers(queryParams);
    }

    var users = null;
    // creating autocomplete functionality
    var timer, timeoutVal = 500;
    mainInput.addEventListener("keypress", () => {
        // clearing the timer everytime a key pressed
        window.clearTimeout(timer);
    });
    // adding keydown logic when using the up and down arrow keys, space, and enter key
    mainInput.addEventListener("keydown", async (e) => {
        if(e.code === "ArrowDown"){
            let autoCompleteItems = document.getElementsByClassName("autocomplete-item");
            let focusedOption = document.getElementsByClassName("focused-option")[0];
            if(autoCompleteItems.length > 0){
                if(!focusedOption){
                    autoCompleteItems[0].classList.add("focused-option");
                }
                else{
                    for(let i = 0; i < autoCompleteItems.length; i++){
                        if(autoCompleteItems[i].getAttribute("name") === focusedOption.getAttribute("name")){
                            autoCompleteItems[i].classList.remove("focused-option");
                            if(i + 1 >= autoCompleteItems.length){
                                autoCompleteItems[0].classList.add("focused-option");
                                autoCompleteItems[0].scrollIntoView({ behavior: "smooth", block: "end", "inline": "nearest"});
                            }
                            else{
                                let nextItem = autoCompleteItems[i + 1];
                                nextItem.classList.add("focused-option");
                                nextItem.scrollIntoView({ behavior: "smooth", block: "end", "inline": "nearest"});
                            }
                        }
                    }
                }
            }
        }
        else if(e.code === "ArrowUp") {
            let autoCompleteItems = document.getElementsByClassName("autocomplete-item");
            let focusedOption = document.getElementsByClassName("focused-option")[0];
            if (autoCompleteItems.length > 0) {
                if (!focusedOption) {
                    autoCompleteItems[autoCompleteItems.length - 1].classList.add("focused-option");
                    autoCompleteItems[autoCompleteItems.length - 1].scrollIntoView({
                                    behavior: "smooth",
                                    block: "end",
                                    "inline": "nearest"
                                });
                } else {
                    for (let i = 0; i < autoCompleteItems.length; i++) {
                        if (autoCompleteItems[i].getAttribute("name") === focusedOption.getAttribute("name")) {
                            autoCompleteItems[i].classList.remove("focused-option");
                            if (i - 1 < 0) {
                                autoCompleteItems[autoCompleteItems.length - 1].classList.add("focused-option");
                                autoCompleteItems[autoCompleteItems.length - 1].scrollIntoView({
                                    behavior: "smooth",
                                    block: "end",
                                    "inline": "nearest"
                                });
                            } else {
                                let nextItem = autoCompleteItems[i - 1];
                                nextItem.classList.add("focused-option");
                                nextItem.scrollIntoView({behavior: "smooth", block: "start", "inline": "nearest"});
                            }
                        }
                    }
                }
            }
        }
        else if(e.code === "Enter"){
            // preventing default behavior
            e.preventDefault();

            let focusedOption = document.getElementsByClassName("focused-option")[0];
            if(focusedOption){
                for(let i = 0; i < users.length; i++){
                    if(users[i].name === focusedOption.getAttribute("name")){
                        let userData = users[i];
                        mainInput.value = userData["name"];
                        usernameInput.value = userData["username"];
                        firstnameInput.value = userData["first_name"];
                        lastnameInput.value = userData["last_name"];
                        emailInput.value = userData["email"];
                        let autoBox = document.getElementById("autocomplete-div");
                        mainInputParent.removeChild(autoBox);
                        mainInput.dataset.userSelected = 'true';
                        mainInput.classList.add('canSubmit');
                        e.stopImmediatePropagation();
                        break;
                    }
                }
            }
        }
        else if(e.code === "Escape") {
            let autoBox = document.getElementById("autocomplete-div");
            mainInputParent.removeChild(autoBox);
        }
    });
    mainInput.addEventListener("keyup",  (v) => {
        let alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
        if(alphabet.indexOf(v.key.toLowerCase()) !== -1) {
            window.clearTimeout(timer);
            timer = setTimeout(async () => {
                let autocompleteBox = document.getElementById("autocomplete-div");
                if (!autocompleteBox) {
                    autocompleteBox = document.createElement("div");
                    autocompleteBox.setAttribute("id", "autocomplete-div");
                    autocompleteBox.style.width = `${mainInput.parentElement.clientWidth}px`;
                    mainInputParent.appendChild(autocompleteBox);
                } else {
                    while (autocompleteBox.childElementCount > 0) {
                        autocompleteBox.removeChild(autocompleteBox.children[0]);
                    }
                }

                let q = v.target.value;
                let userObjects = await getIntellisense(q);
                users = userObjects
                let usersArr = [];
                for (let i = 0; i < userObjects.length; i++) {
                    if (userObjects[i].name.substring(0, q.length).toLowerCase() === q.toLowerCase()) {
                        usersArr.push(userObjects[i].name);
                    }
                }
                usersArr.sort();
                for (let i = 0; i < usersArr.length; i++) {
                    let autoSpan = document.createElement("span");
                    autoSpan.setAttribute("class", "autocomplete-item");
                    autoSpan.innerHTML = "<strong>" + usersArr[i].substring(0, q.length) + "</strong>";
                    autoSpan.innerHTML += usersArr[i].substring(q.length);
                    autoSpan.setAttribute("name", usersArr[i]);
                    autocompleteBox.appendChild(autoSpan);
                    autoSpan.addEventListener("click", async () => {
                        for (let j = 0; j < userObjects.length; j++) {
                            if (userObjects[j].name === usersArr[i]) {
                                let userData = userObjects[j];
                                mainInput.value = userData["name"];
                                usernameInput.value = userData["username"];
                                firstnameInput.value = userData["first_name"];
                                lastnameInput.value = userData["last_name"];
                                emailInput.value = userData["email"];
                                let autoBox = document.getElementById("autocomplete-div");
                                mainInputParent.removeChild(autoBox);
                                mainInput.dataset.userSelected = 'true';
                                mainInput.classList.add('canSubmit');
                                break;
                            }
                        }
                    });
                }
            }, timeoutVal);
        }
    });
}