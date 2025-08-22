// ********** Imports **********
import * as fetches from "./fetches";
import * as functions from "./functions";

let firstNameInput = document.getElementById("memberFirstName");
let lastNameInput = document.getElementById("memberLastName");
let autoInputs = document.getElementsByClassName("local-autocomplete");

if (autoInputs.length > 0) {
    // ********** Header search logic **********
    let searchInput;
    let searchInputDiv;
    let inputTimeout = 500;
    let dropdownDivActive = false;
    let dropdownDiv;
    let activeTimeout;
    // relating to the dropdown list
    let currentItem;
    for (let i = 0; i < autoInputs.length; i++) {
        let input = autoInputs[i];
        input.addEventListener("input", () => {
            let type = input.dataset.type;
            let filter = input.dataset.filter;
            searchInput = input;
            searchInputDiv = input.parentElement;
            clearTimeout(activeTimeout)
            activeTimeout = setTimeout(async () => {
                let q = searchInput.value;
                if (q !== "") {
                    let queryData = {
                        type: type,
                        filter: filter,
                        q: q,
                    }
                    let res = JSON.parse(await fetches.getInstances(queryData));
                    if (res.error) {
                        console.log(res.message);
                    } else {
                        if (res.length > 0) {
                            if (dropdownDivActive === false) {
                                // created the list div
                                createDropDownDiv(searchInputDiv);
                                dropdownDivActive = true;
                            }

                            // removing all user suggestions from old search
                            removeDropDownChildren(dropdownDiv);

                            for (let i = 0; i < res.length; i++) {
                                let user = res[i];
                                // creating each list item
                                let span = document.createElement("span");
                                span.className = "user-dropdown-item";
                                if (filter.includes("_name")) {
                                    span.dataset.data = JSON.stringify({
                                        id: user["id"],
                                        firstName: user["firstName"],
                                        lastName: user["lastName"],
                                        inputId: input.id,
                                    });
                                    span.innerText = `${user["firstName"]} ${user["lastName"]}`;
                                } else {
                                    span.dataset.data = JSON.stringify({
                                        id: user["id"],
                                        name: user["name"],
                                        inputId: input.id,
                                    });
                                    span.innerText = `${user["name"]}`;
                                }
                                addListener("mouseup", span);
                                dropdownDiv.appendChild(span);
                            }

                            // adding listeners to the users list
                            addListener("keydown", searchInput, Array.from(dropdownDiv.children));
                            addListener("focusout", searchInput);
                        }
                    }
                } else {
                    dropdownDivActive = false;
                    removeListener("keydown", searchInput);
                    removeListener("focusout", searchInput);
                }
            }, inputTimeout);
        });
    }

    // ***** Header search functions *****
    function createDropDownDiv(parent) {
        dropdownDiv = document.createElement("div");
        dropdownDiv.id = "usersDiv";
        parent.appendChild(dropdownDiv);
    }

    function removeDropDownDiv(parent, elId) {
        let el = document.getElementById(elId);
        if (el) {
            parent.removeChild(el)
        }
    }

    function removeDropDownChildren(parent) {
        while (parent.childElementCount > 0) {
            parent.removeChild(parent.firstElementChild);
        }
    }

    function selectUser(data) {
        let fnInput;
        let lnInput;
        let nameInput;
        let input = document.getElementById(data["inputId"]);
        let inputFilter = input.dataset.filter;
        if (inputFilter === "first_name" ||  inputFilter === "last_name") {
            if (inputFilter === "first_name") {
                fnInput = input;
                lnInput = fnInput.parentElement.nextElementSibling.firstElementChild;
                lnInput.focus();
            } else {
                lnInput = input;
                fnInput = lnInput.parentElement.previousElementSibling.firstElementChild;
                fnInput.focus();
            }
            fnInput.value = data["firstName"];
            lnInput.value = data["lastName"];
        } else {
            nameInput = input;
            nameInput.value = data["name"];
            nameInput.blur(); // removes focus from an element
        }
    }

    const keyDownFunction = (ev, refList = null) => {
        let currentItem = getCurrentItem();
        let itemIndex = !currentItem ? 0 : refList.indexOf(currentItem);
        let nextItem = refList[itemIndex] === refList[refList.length - 1] ? refList[0] : refList[itemIndex + 1];
        let previousItem = refList[itemIndex] === refList[0] ? refList[refList.length - 1] : refList[itemIndex - 1];
        let newCurrentItem;
        switch(ev.key) {
            case "ArrowDown":
                newCurrentItem = !currentItem ? refList[0] : nextItem;
                // adding the active class to the current Item
                newCurrentItem.classList.add("active-item");
                // removing the active class from previous item
                refList.filter(item => {
                    if (item.className.includes("active-item") && item !== newCurrentItem) {
                        item.classList.remove("active-item");
                    }
                });
                // setting the new currentIndex
                setCurrentItem(newCurrentItem);
                break;
            case "ArrowUp":
                newCurrentItem = previousItem;
                // adding the active class to the current Item
                newCurrentItem.classList.add("active-item");
                // removing the active class from previous item
                refList.filter(item => {
                    if (item.className.includes("active-item") && item !== newCurrentItem) {
                        item.classList.remove("active-item");
                    }
                });
                // setting the new currentIndex
                setCurrentItem(newCurrentItem);
                break;
            case "Escape":
                removeDropDownDiv(searchInputDiv, dropdownDiv.id);
                break;
            case "Enter":
                let activeItem = dropdownDiv.querySelector(".active-item");
                let data = JSON.parse(activeItem.dataset.data);
                selectUser(data);
                break;
            default:
                break;
        }
    }

    function focusOutFunction() {
        setTimeout(() => {
            removeDropDownDiv(searchInputDiv, dropdownDiv.id);
        }, 250);
    }

    function clickFunction(ev) {
        let data = JSON.parse(ev.target.dataset.data);
        selectUser(data);
    }

    function getCurrentItem() {
        return currentItem
    }

    function setCurrentItem(newItem) {
        currentItem = newItem;
    }

    // ***** Header search listeners *****
    let eventTypes = {
        keydown: keyDownFunction,
        focusout: focusOutFunction,
        mouseup: clickFunction,
    }

    function addListener(type, el, refList=null) {
        el.addEventListener(type, (ev) => eventTypes[type](ev, refList));
    }

    function removeListener(type, el) {
        el.removeEventListener(type, eventTypes[type]);
    }
}