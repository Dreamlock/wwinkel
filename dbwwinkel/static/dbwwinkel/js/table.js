/**
 * Created by Robbe on 3/27/2017.
 */

$(document).ready(function ($) {
    $(".table-row").click(function () {
        window.document.location = $(this).data("href");
    });
});

$(document).ready(function () {
    $('#admin').DataTable({
        "language": {
            url: 'https://cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Dutch.json'
        }
    });
});

$(document).ready(function () {
    $('#question_list').DataTable({
        'searching':false,
        "language": {
            url: 'https://cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Dutch.json'
        }
    });
});
