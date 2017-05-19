/**
 * Created by Robbe on 3/27/2017.
 */

$(document).ready(function($) {
    $(".table-row").click(function() {
        window.document.location = $(this).data("href");
    });
});

