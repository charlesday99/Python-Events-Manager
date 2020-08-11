var SELECTED_IMAGES = [];
var delete_enabled = false;
var select_enabled = true;

function addImageClickers() {
    for (image of document.getElementsByClassName("photo-cell")) {
        image.onclick = function() {
            if (!select_enabled) {
                if (SELECTED_IMAGES.includes(this.id)) {
                    this.style["background-color"] = "#fff";
    
                    const index = SELECTED_IMAGES.indexOf(this.id);
                    if (index > -1) {
                        SELECTED_IMAGES.splice(index, 1);
                    }
                } else {
                    this.style["background-color"] = "#2196f3";
                    SELECTED_IMAGES.push(this.id);
                }
            } else {
                document.getElementById("photo-preview-image").src = "/content/" + this.id;
                document.getElementById("photo-preview").style['visibility'] = "visible";
            }
        }
    }
}

function unselectImages() {
    for (id of SELECTED_IMAGES) {
        document.getElementById(id).style["background-color"] = "#fff";
    }
    SELECTED_IMAGES = [];
}

function selectClicked() {
    if (select_enabled) {
        delete_enabled = true;
        select_enabled = false;
        document.getElementById("selectBtn").textContent = "Unselect All";
        document.getElementById("deleteBtn").className = "btn btn-primary";
    } else {
        delete_enabled = false;
        select_enabled = true;
        document.getElementById("selectBtn").textContent = "Select";
        document.getElementById("deleteBtn").className = "btn";
        unselectImages();
    }
}

function deleteClicked() {
    if (delete_enabled) {
        for (id of SELECTED_IMAGES) {
            document.getElementById(id).style["background-color"] = "#FF0000";
            //Delete code here
        }
    }
}