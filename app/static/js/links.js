$('#linkModal').on('show.bs.modal', function (e) {
    populateLinks()
});

function addURL() {
    var URL = document.getElementById("urlField").value;
    $.post("/link/new", { URL: URL});
    document.getElementById("urlField").value = "";
    populateLinks();
}

function selectURL(ID){
    document.getElementById("linkID").value = ID;
    updateFormURL();
}

function populateLinks() {
    $.getJSON("/link/dump",function(data){
        $("#linkTable tbody").empty();
        for (link of data) {
            $("#linkTable tbody").append("<tr><td>" + link[0] + "</td><td>" + link[1] + "</td><td>" + "<button onclick='selectURL("+ link[0] +")' class='btn btn-primary form-control'>Select</button>" + "</td></tr>");
        }
    });
}

function updateFormURL() {
    var ID = document.getElementById("linkID").value;
    if (ID !== "") {
        $.getJSON("/link/" + ID + "/info",function(data){
            $('#linkURL').val(data['URL']);
        });
    }
}

//Runs on page load
//Populates the URL field based on the Link ID
updateFormURL()