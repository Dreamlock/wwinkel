/**
 * Created by Robbe on 3/27/2017.
 */

jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data('href');
    });
});