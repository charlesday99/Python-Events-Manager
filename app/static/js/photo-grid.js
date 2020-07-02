var SELECTED_IMAGES = [];

function addImageClickers() {
    for (image of document.getElementsByClassName("photo-cell")) {
        image.onclick = function() {
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
        }
    }
}

function clearShadows() {
    for (id of SELECTED_IMAGES) {
        document.getElementById(id).style["background-color"] = "#fff";
    }
    SELECTED_IMAGES = [];
}