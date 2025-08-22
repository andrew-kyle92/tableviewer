// ********** Imports **********
import * as fetches from "./fetches";
import * as functions from "./functions";
import { currentURL } from "./main";

// ********** Main Logic **********
if (currentURL.pathname.includes('tables/detail')) {
    window.addEventListener('DOMContentLoaded', function () {
        // settings configuration elements
        let tableSettings = document.getElementsByClassName("table-setting");
        for (let i = 0; i < tableSettings.length; i++) {
            let tableSetting = tableSettings[i];
            tableSetting.addEventListener("change", async () => {
                // let valueChanged = tableSetting.dataset.valueChanged === "false";
                let tableSettingValue = tableSetting.checked ? "true" : "false";
                if (tableSettingValue !== tableSetting.dataset.currentValue) {
                    tableSetting.dataset.valueChanged = "true";
                } else {
                    tableSetting.dataset.valueChanged = "false";
                }
            });
        }

        // Save button logic
        let saveBtn = document.getElementById("settings-save-btn");
        saveBtn.addEventListener("click", async () => {
            let tableSettings = document.getElementsByClassName("table-setting");
            let changedData = {id: parseInt(saveBtn.dataset.settings)}; // dictionary of db values that need to be updated
            let changedInputs = []; // list of HTML inputs
            for (let i = 0; i < tableSettings.length; i++) {
                let tableSetting = tableSettings[i];
                if (tableSetting.dataset.valueChanged === "true") {
                    switch (tableSetting.id) {
                        case "publishedInput":
                            changedData.published = !!tableSetting.checked; // adding to changedData object
                            changedInputs.push(tableSetting); // adding to changedInputs array
                            break;
                    }
                }
            }
            // saving the changes to the database
            let res = JSON.parse(await fetches.saveTableSettings(changedData));
            if (res.success) {
                functions.writeAlert("success", "Settings saved");
                for (let i = 0; i < changedInputs.length; i++) {
                    changedInputs[i].dataset.valueChanged = "false";
                }
            }
            else {
                functions.writeAlert("warning", res.error);
            }
        });
    });
}