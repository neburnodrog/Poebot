$(document).ready(function () {
    $(".form-group").each(function () {
        let $input_child = $(this).children().eq(1);
        $input_child.addClass("form-control")
    })

    $("#submit").addClass("btn btn-light")
})