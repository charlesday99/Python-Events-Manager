var SELECTED_IMAGES = [];
var delete_enabled = false;
var select_enabled = true;

function addImageClickers() {
    for (image of document.getElementsByClassName("photo-cell")) {
        image.onclick = function() {
            var ID = this.id;

            if (!select_enabled) {
                if (SELECTED_IMAGES.includes(ID)) {
                    this.style["background-color"] = "#fff";
    
                    const index = SELECTED_IMAGES.indexOf(ID);
                    if (index > -1) {
                        SELECTED_IMAGES.splice(index, 1);
                    }
                } else {
                    this.style["background-color"] = "#2196f3";
                    SELECTED_IMAGES.push(ID);
                }
            } else {
                $.getJSON("/image/" + ID, function(data){
                    document.getElementById("titleField").value = data['title'];
                    document.getElementById("captionField").value = data['caption'];
                    document.getElementById("previewImage").src = "/content/" + data['filename'];

                    document.getElementById("imageDeleteButton").setAttribute("onClick","deleteImage('" + ID + "');location.reload();");
                    document.getElementById("captionUpdateButton").setAttribute("onClick","updateImageFromField('" + ID + "','caption');");
                    document.getElementById("titleUpdateButton").setAttribute("onClick","updateImageFromField('" + ID + "','title');");
                });
                $("#imageModal").modal('show');
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
        document.getElementById("deleteBtn").className = "btn btn-primary form-control";
    } else {
        delete_enabled = false;
        select_enabled = true;
        document.getElementById("selectBtn").textContent = "Select";
        document.getElementById("deleteBtn").className = "btn form-control";
        unselectImages();
    }
}

function deleteClicked() {
    if (delete_enabled) {

        for (id of SELECTED_IMAGES) {
            deleteImage(id);
              
            document.getElementById(id).outerHTML = "";
        }
        location.reload();
    }
}

function deleteImage(id) {
    $.ajax({
        url : '/image/' + id,
        method : 'delete',
    }).fail(function(){
        alert("An error occurred, the image couldnt be deleted!");
    });
}

function updateImageFromField(id, field) {
    var data = "";

    if (field == "title") {
        data = document.getElementById("titleField").value;
        updateImage(id, field, data);
    } else {
        data = document.getElementById("captionField").value;
        updateImage(id, field, data);
    }
}

function updateImage(id, field, data) {
    var parameter =  {"value": data, "field": field};
    $.ajax({
        type: 'PUT',
        url: '/image/' + id,
        data: JSON.stringify(parameter),
        contentType: 'application/json',
        }).fail(function(){
            alert("An error occurred, the image couldn't be updated!");
    });
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
            alert("An error occurred, the image couldn't be uploaded!");
    });
}
