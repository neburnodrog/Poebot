$(document).ready(function () {
    // jQuery SELECTOR variables
    var $rhySeq = $("#id_rhy_seq");
    var $hiddenContainer = $("#hidden-container");
    var $hidden = $("#hidden");
    var $verLen = $("#id_verse_length");
    var $verNum = $("#id_ver_num");
    var $selVer = $('#id_select_verses');
    var $hiddenSelGroup = $('#hidden_select_group');
    //## VARIABLES ##//
    var asson_words = [
        ["gominola", "-oa"],
        ["naranja", "-aa"],
        ["sombrero", "-eo"],
        ["tomate", "-ae"],
        ["áureo", "-aueo"],
        ["toronja", "-oa"],
        ["tuerca", "-ea"],
        ["óxido", "-oio"],
        ["hastío", "-io"],
        ["arbusto", "-uo"],
        ["onomatopeya", "-ea"],
        ["artífice", "-iie"],
        ["mendrugo", "-uo"],
        ["gamberro", "-eo"],
        ["lápiz", "-ai"],
        ["tonificante", "-ae"],
        ["tórrido", "-oio"],
        ["estío", "-io"],
    ];
    var conson_words = [
        ["alcoba", "-oba"],
        ["muñeco", "-eco"],
        ["sonajero", "-ero"],
        ["nabo", "-abo"],
        ["mano", "-ano"],
        ["risa", "-isa"],
        ["ungüento", "-ento"],
        ["dientes", "-entes"],
        ["ministro", "-istro"],
        ["señora", "-ora"],
        ["fleco", "-eco"],
        ["gotera", "-era"],
        ["altramuz", "-uz"],
        ["marrano", "-ano"],
        ["sacapuntas", "-untas"],
        ["argento", "-ento"],
        ["mientes", "-entes"],
        ["astrofísico", "-isico"],
    ];
    /*## HELPER FUNCTIONS ##*/
    function choose_message(rhyme_type) {
        if (rhyme_type === "consonante") {
            var word = conson_words[Math.floor(Math.random() * conson_words.length)];
        }
        else {
            var word = asson_words[Math.floor(Math.random() * asson_words.length)];
        }
        return "O la palabra: '" + word[0] + "', o la rima: '" + word[1] + "'";
    }
    function uniqueChar(rhymeSequence) {
        var uniqueValuesArray = [];
        for (var i = 0; i < rhymeSequence.length; i++) {
            if (uniqueValuesArray.includes(rhymeSequence[i])) { }
            else {
                uniqueValuesArray.push(rhymeSequence[i]);
            }
        }
        return uniqueValuesArray;
    }
    function uniqueRhymes(rhymeSequenceString) {
        /* return it as array without the whitespaces */
        var rhySequenceArray = rhymeSequenceString
            .split(' ')
            .join('')
            .split('');
        return uniqueChar(rhySequenceArray);
    }
    /*## CREATE FORM DINAMICALLY FUNCS ##*/
    function createInput(rhymeKey, rhymeType) {
        var input = $("<input>", {
            type: "text",
            "class": "form-control rhyme_validator",
            name: rhymeKey,
            id: rhymeKey,
            required: true
        });
        input.keyup(function () {
            if ($(this).val() === "") {
                resetToNeutral($(this), choose_message(rhymeType));
            }
        });
        input.change(function () {
            var inputVal = String($(this).val());
            if (/^-?[a-zA-ZñÑÓóÁáÉéíÍúÚü]+$/.test(inputVal)) {
                $.ajax({
                    url: "/validate/",
                    data: $(this).serialize() + "&" + $rhySeq.serialize() + "&" + $verLen.serialize(),
                    dataType: 'json',
                    success: function (data) {
                        if (data.not_valid) {
                            validInvalid($(this), data.error_message, false);
                        }
                        else {
                            validInvalid($(this), "La rima es válida y existe en la base de datos.", true);
                        }
                    }
                });
            }
            else {
                var err_msg = "Solo se permiten caracteres alfabéticos y el guión.";
                validInvalid($(this), err_msg, false);
            }
        });
        return input;
    }
    function createRhymeField(rhymeKey) {
        var $rhymeDivRow = $("<div>", {
            "class": 'row justify-content-center'
        });
        var $rhymeDivCol = $("<div>", {
            "class": 'col-auto col-sm-8 mb-2'
        });
        var rhymeType;
        if (rhymeKey === rhymeKey.toUpperCase()) {
            rhymeType = "consonante";
        }
        else {
            rhymeType = "asonante";
        }
        var $label = $("<label>").attr("for", rhymeKey).text("Rima " + rhymeType + " " + rhymeKey + ":");
        var $input = createInput(rhymeKey, rhymeType);
        var $small = $("<small>", {
            "class": 'form-text text-muted'
        })
            .text(choose_message(rhymeType));
        $hiddenContainer.append($rhymeDivRow);
        $rhymeDivRow.append($rhymeDivCol);
        $rhymeDivCol.append($label, $input, $small);
    }
    function createFormDinamically() {
        var rhySeqVal = String($rhySeq.val());
        $hiddenContainer.empty();
        var sequenceSet = uniqueRhymes(rhySeqVal);
        for (var i = 0; i < sequenceSet.length; i++) {
            createRhymeField(sequenceSet[i]);
        }
        $hidden.show();
    }
    /*## CHANGE ELEMENTS TO VALID/INVALID/NEUTRAL STATE FUNCS ##*/
    function validInvalid(inputElem, msg, valid) {
        if (valid) {
            inputElem.removeClass("is-invalid").addClass("is-valid");
        }
        else {
            inputElem.removeClass("is-valid").addClass("is-invalid");
        }
        if (inputElem.next().length === 0) {
            inputElem.parent().append("<small></small>");
        }
        var small = inputElem.next().removeClass("text-muted");
        if (inputElem.hasClass("is-valid")) {
            small.removeClass("invalid-feedback")
                .addClass("valid-feedback");
        }
        else if (inputElem.hasClass("is-invalid")) {
            small.removeClass("valid-feedback")
                .addClass("invalid-feedback");
        }
        small.text(msg);
    }
    function resetToNeutral(inputElem, msg) {
        inputElem.removeClass("is-invalid").removeClass("is-valid");
        var small = inputElem.next().removeClass("invalid-feedback")
            .removeClass("valid-feedback")
            .addClass("text-muted")
            .text(msg);
    }
    /*## RHYMES SEQUENCE INPUT VALIDATION FUNCS ##*/
    function validateRhymesSequence() {
        var verNumVal = String($verNum.val());
        var rhySeqVal = String($rhySeq.val());
        if (/^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == true &&
            rhySeqVal.split(" ").join("").length == Number(verNumVal)) {
            validInvalid($rhySeq, "Tiene buena pinta", true);
            return true;
        }
        else {
            if (/^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == false) {
                var err_msg = "Solo valen caracteres del abecedario y espacios en blanco";
                validInvalid($rhySeq, err_msg, false);
                return false;
            }
            else if (rhySeqVal.split(" ").join("").length != Number(verNumVal)) {
                var err_msg = "El número de caracteres ha de coincidir con el número de versos (sin contar espacios)";
                validInvalid($rhySeq, err_msg, false);
                return false;
            }
        }
    }
    function rhySeqOnLoad() {
        if ($rhySeq.val() === "") {
            resetToNeutral($rhySeq, "Ejemplo: ABBA ABBA");
            $hidden.hide();
            $hiddenSelGroup.hide();
        }
        else {
            $hiddenSelGroup.show();
            if ($selVer.val() === "yes" && validateRhymesSequence()) {
                createFormDinamically();
                $hidden.show();
            }
        }
    }
    /*## NUMBER OF VERSES INPUT FIELD VALIDATION FUNCS ##*/
    function verNumIsValid() {
        var verNumVal = $verNum.val();
        if (0 < verNumVal && verNumVal < 21) {
            return true;
        }
        else {
            return false;
        }
    }
    function verNumOnLoad() {
        if ($verNum.val() == "") {
            resetToNeutral($verNum, "Min: 1, Max: 20");
        }
        else if (verNumIsValid()) {
            validInvalid($verNum, "Tiene buena pinta.", true);
        }
        else {
            validInvalid($verNum, "Solo números. Min: 1, Max: 20", false);
        }
    }
    /*## LENGTH OF VERSES INPUT FIELD VALIDATION FUNCS ##*/
    function verLenIsValid() {
        var verLenVal = $verLen.val();
        if (4 < verLenVal && verLenVal < 15) {
            return true;
        }
        else {
            return false;
        }
    }
    function verLenOnLoad() {
        if ($verLen.val() == "") {
            resetToNeutral($verLen, "Min: 5, Max: 14");
        }
        else if (verLenIsValid()) {
            validInvalid($verLen, "Tiene buena pinta.", true);
        }
        else {
            validInvalid($verLen, "Solo números. Min: 5, Max: 14", false);
        }
    }
    /*## POPOVER ACTIVATION ##*/
    $(".popover").each(function () {
        var text = $(this).parent().prev()
            .children().eq(0).children()
            .eq(0).text();
        if (text === "Número de versos:") {
            var message = "Un número entre 1 y 20 para que germine un poema. Si se deja en blanco será un número aleatorio de versos.";
            var where = "top";
        }
        else if (text === "Longitud de los versos:") {
            var message = "Longitud de los versos, medidos en número de sílabas. Si el campo queda vacío serán versos de tamaño variable.";
            var where = "top";
        }
        else {
            var message = "Mayúsculas: rima consonante. Minúsculas: asonante. Espacio en blanco: verso en blanco. El campo vacío producirá poemas sin rima.";
            var where = "bottom";
        }
        $(this).attr("data-placement", where).attr("data-content", message);
    });
    $('[data-toggle="popover"]').popover({
        trigger: "focus"
    });
    /* ON READY VERIFICATION OF FIELDS */
    verNumOnLoad();
    verLenOnLoad();
    rhySeqOnLoad();
    /*## EVENT LISTENERS ##*/
    $verNum.on("change, blur", function () {
        var verNumVal = $(this).val();
        if (verNumVal === "") {
            resetToNeutral($(this), "Min: 1, Max: 20");
        }
        else if (0 < verNumVal && verNumVal < 21) {
            validInvalid($(this), "Esto número tiene buena pinta.", true); /* Tiene buena pinta */
        }
        else {
            var error_message = "Sólo números. Min: 1, Max: 20";
            validInvalid($(this), error_message, false);
        }
        if ($rhySeq.val() !== "") {
            validateRhymesSequence();
        }
    });
    $verLen.on("change, blur", function () {
        var verLenVal = $(this).val();
        if (verLenVal === "") {
            resetToNeutral($(this), "Min: 5, Max: 14");
        }
        else if (4 < verLenVal && verLenVal < 15) {
            var message = "Me gusta, no parece un número indigesto.";
            validInvalid($(this), message, true);
        }
        else {
            var error_message = "Sólo números. Min: 5, Max: 14";
            validInvalid($(this), error_message, false);
        }
    });
    $rhySeq.keyup(function () {
        $hiddenSelGroup.show();
        if ($(this).val() === "") {
            resetToNeutral($(this), "Ejemplo: ABBA ABBA");
            $hiddenContainer.empty;
            $hiddenSelGroup.hide();
            $hidden.hide();
        }
    });
    $rhySeq.on("change blur", function () {
        validateRhymesSequence();
    });
    $selVer.change(function () {
        if ($(this).val() === 'yes') {
            if ($rhySeq.hasClass("is-valid")) {
                if ($(this).hasClass("is-invalid")) {
                    validInvalid($(this), "", true);
                }
                createFormDinamically();
                $hidden.show();
            }
            else {
                var error_message = "La secuencia de rimas ha de ser válida.";
                validInvalid($(this), error_message, false);
            }
            ;
        }
        else {
            $hidden.hide();
        }
        ;
    });
    $("form").submit(function (event) {
        if ($(".is-invalid").length > 0) {
            alert("Todavía hay valores incorrectos");
            event.preventDefault();
        }
        else {
            $(this).trigger("submit");
        }
    });
});
