$(document).ready(function () {
    $('#reload').click(function () {
        location.reload();
    });
    /**AJAX TO CHANGE THE VERSES WITH AN EQUIVALENT FROM DB*/
    $(".oi").click(function () {
        var $verse_to_change = $(this).parent().prev().children();
        $.ajax({
            url: '/change_verse/',
            data: "id=" + $verse_to_change.attr("id"),
            dataType: "json",
            success: function (data) {
                if (data.not_valid) {
                    $verse_to_change.css("color", "red");
                }
                else {
                    $verse_to_change.attr("id", data.id).text(data.verse_text);
                }
                ;
            }
        });
    });
});
