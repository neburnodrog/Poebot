$(document).ready(function () {

    $('[data-toggle="popover"]').popover({
        trigger: "focus"
    })

    $(".errorlist").each(function () {
        $(this).addClass("alert-sm alert-danger");
    })

})
