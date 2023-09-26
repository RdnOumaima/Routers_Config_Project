$(document).ready(function () {
    var errorMessage = $('#error-message').val();
    
    if (errorMessage) {
        $('#errorModal').modal('show');
    }
});
