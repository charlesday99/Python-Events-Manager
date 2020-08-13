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

  			$.ajax({
				 url : '/image/' + id,
				 method : 'delete',
            })
            
            document.getElementById(id).outerHTML = "";

        }
        location.reload();
    }
}

function uploadImage() {
    var title = document.getElementById("uploadText").value;
    var caption = document.getElementById("uploadCaption").value;
    
    var formData = new FormData();
    formData.append('title', title);
    formData.append('caption', caption); 
    formData.append('file', $('input[type=file]')[0].files[0]);

    $.ajax({
        type: 'POST',
        url: '/image/',
        data: formData,
        processData: false,
        contentType: false,
        }).done(function(){
            location.reload();
        }).fail(function(){
            console.log("An error occurred, the files couldn't be sent!");
    });
}
