/* eslint-env jquery */

$(document).ready(function () {

    // jQuery SELECTOR variables
    const $rhySeq = $("#id_rhy_seq");
    const $hiddenForm = $("#hidden-form");
    const $hidden = $("#hidden");
    const $verLen = $("#id_verse_length");
    const $verNum = $("#id_ver_num");
    const $selVer = $('#id_select_verses');
    const $submit = $("#submit");


    //## VARIABLES ##//
    const asson_words = [
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

    const conson_words = [
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


    /*## FUNCTIONS ##*/
    function choose_message(rhyme_type) {
        if (rhyme_type === "consonante") {
            word = conson_words[Math.floor(Math.random() * conson_words.length)];
        } else {
            word = asson_words[Math.floor(Math.random() * asson_words.length)];
        }
        return `O la palabra: '${word[0]}', o la rima: '${word[1]}'`
    }


    function uniqueChar(rhymeSequence) {
        let uniqueValuesArray = [];
        for (let i = 0; i < rhymeSequence.length; i++) {
            if (uniqueValuesArray.includes(rhymeSequence[i])) { } else {
                uniqueValuesArray.push(rhymeSequence[i]);
            }
        }
        return uniqueValuesArray;
    }


    function uniqueRhymes(rhymeSequenceString) {
        /* return it as array without the whitespaces */
        let rhySequenceArray = rhymeSequenceString
            .split(' ')
            .join('')
            .split('');
        return uniqueChar(rhySequenceArray);
    }


    function createInput(rhymeKey, rhymeType) {
        let input = $(
            "<input>", {
            type: "text",
            class: "form-control rhyme_validator",
            name: rhymeKey,
            id: rhymeKey,
            required: true,
        }
        );

        input.keyup(
            function () {
                if ($(this).val() === "") {
                    resetToNeutral($(this), choose_message(rhymeType));
                }
            }
        );

        input.change(
            function () {
                rhyme_input = $(this);
                if (/^-?[a-zA-ZñÑÓóÁáÉéíÍúÚü]+$/.test(rhyme_input.val())) {
                    $.ajax({
                        url: "/validate/",
                        data: `${rhyme_input.serialize()}&${$rhySeq.serialize()}&${$verLen.serialize()}`,
                        dataType: 'json',
                        success: function (data) {
                            if (data.not_valid) {
                                validInvalid(rhyme_input, data.error_message, valid = false)
                            } else {
                                validInvalid(rhyme_input, "Tiene buena pinta", valid = true)
                            }
                        }
                    });

                } else {
                    error_message = "Solo se permiten caracteres alfabéticos y el guión."
                    validInvalid(rhyme_input, error_message, valid = false);
                }
            }
        );

        return input;
    }


    function createRhymeField(rhymeKey) {
        let $rhymeDivRow = $("<div>", {
            class: 'row justify-content-center'
        })
        let $rhymeDivCol = $("<div>", {
            class: 'col-auto col-sm-8 mb-2'
        });

        let rhymeType;
        if (rhymeKey === rhymeKey.toUpperCase()) {
            rhymeType = "consonante";
        } else {
            rhymeType = "asonante";
        }

        let $label = $("<label>").attr("for", rhymeKey).text(`Rima ${rhymeType} ${rhymeKey}:`);
        let $input = createInput(rhymeKey, rhymeType);
        let $small = $("<small>", {
            class: 'form-text text-muted'
        })
            .text(choose_message(rhymeType));

        $hiddenForm.append($rhymeDivRow);
        $rhymeDivRow.append($rhymeDivCol);
        $rhymeDivCol.append($label, $input, $small);
    }


    function createFormDinamically() {
        $hiddenForm.empty();

        let sequenceSet = uniqueRhymes($rhySeq.val());
        for (i = 0; i < sequenceSet.length; i++) {
            createRhymeField(sequenceSet[i]);
        }
    }


    function showSelect() {
        $selVer.show()
            .prev()
            .show();
    }


    function hideSelect(select) {
        $selVer.hide()
            .prev()
            .hide();
    }


    function validInvalid(inputElem, msg, valid) {
        if (valid) {
            inputElem.removeClass("is-invalid").addClass("is-valid");
        } else {
            inputElem.removeClass("is-valid").addClass("is-invalid");
        }

        if (inputElem.next().length === 0) {
            inputElem.parent().append("<small></small>");
        }

        small = inputElem.next().removeClass("text-muted");

        if (inputElem.hasClass("is-valid")) {
            small.removeClass("invalid-feedback")
                .addClass("valid-feedback");
        } else if (inputElem.hasClass("is-invalid")) {
            small.removeClass("valid-feedback")
                .addClass("invalid-feedback");
        }

        small.text(msg);
    }

    function resetToNeutral(inputElem, msg) {
        inputElem.removeClass("is-invalid").removeClass("is-valid");
        small = inputElem.next().removeClass("invalid-feedback")
            .removeClass("valid-feedback")
            .addClass("text-muted")
            .text(msg);
    }

    function validateRhymesSequence() {
        let verNumVal = $verNum.val();
        let rhySeqVal = $rhySeq.val();

        if (rhySeqVal === "") {

        } else if (rhymeSeqIsValid(rhySeqVal, verNumVal)) {

            validInvalid($rhySeq, "Tiene buena pinta", true);
            createFormDinamically();

            showSelect();

            if ($selVer.val() == "yes") {
                validInvalid($selVer, "", valid = true);
                $($hidden).show();
            }

        } else {

            if (/^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == false) {
                let err_msg = "Solo valen caracteres del abecedario y espacios en blanco";
                validInvalid($rhySeq, err_msg, false);

            } else if (rhySeqVal.split(" ").join("").length != verNumVal) {
                let err_msg = "El número de caracteres ha de coincidir con el número de versos (sin contar espacios)"
                validInvalid($rhySeq, err_msg, false);
            }
        }
    }

    function rhymeSeqIsValid(rhySeqVal, verNumVal) {
        if (
            /^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == true &&
            rhySeqVal.split(" ").join("").length == verNumVal
        ) {
            return true;
        } else {
            return false;
        }
    }

    function rhySeqOnLoad() {
        if ($rhySeq.val() === "") {
            resetToNeutral($rhySeq, "Ejemplo: ABBA ABBA");
            $hidden.hide();
            hideSelect();
        } else {
            validateRhymesSequence();
        }
    }

    function verNumIsValid() {
        let verNumVal = $verNum.val();

        if (0 < verNumVal && verNumVal < 21) {
            return true;
        } else {
            return false;
        }
    }

    function verNumOnLoad() {
        if ($verNum.val() == "") {
            resetToNeutral($verNum, "Min: 1, Max: 20");
        } else if (verNumIsValid()) {
            validInvalid($verNum, "Tiene buena pinta.", valid = true);
        } else {
            validInvalid($verNum, "Solo números. Min: 1, Max: 20", valid = false);
        }
    }

    function verLenIsValid() {
        let verLenVal = $verLen.val();
        if (4 < verLenVal && verLenVal < 15) {
            return true;
        } else {
            return false;
        }
    }

    function verLenOnLoad() {
        if ($verLen.val() == "") {
            resetToNeutral($verLen, "Min: 5, Max: 14");
        } else if (verLenIsValid()) {
            validInvalid($verLen, "Tiene buena pinta.", valid = true);
        } else {
            validInvalid($verLen, "Solo números. Min: 5, Max: 14");
        }
    }

    // LOGIC AND LISTENERS
    $(".popover").each(function () {
        let text = $(this).parent().prev()
            .children().eq(0).children()
            .eq(0).text();
        if (text === "Número de versos:") {
            var message = "Un número entre 1 y 20 para que germine un poema. Si se deja en blanco será un número aleatorio de versos.";
            var where = "top";
        } else if (text === "Longitud de los versos:") {
            var message = "Longitud de los versos, medidos en número de sílabas. Si el campo queda vacío serán versos de tamaño variable.";
            var where = "top";
        } else {
            var message = "Mayúsculas: rima consonante. Minúsculas: asonante. Espacio en blanco: verso en blanco. El campo vacío producirá poemas sin rima.";
            var where = "bottom";
        }

        $(this).attr("data-placement", where).attr("data-content", message);
    })

    $('[data-toggle="popover"]').popover({
        trigger: "focus"
    })

    verNumOnLoad();
    verLenOnLoad();
    rhySeqOnLoad();

    $verNum.on(
        "change, blur",
        function () {
            let verNumVal = $(this).val();

            if (verNumVal === "") {
                resetToNeutral($(this), "Min: 1, Max: 20");
            } else if (0 < verNumVal && verNumVal < 21) {
                validInvalid($(this), "Esto número tiene buena pinta.", valid = true); /* Tiene buena pinta */
            } else {
                let error_message = "Sólo números. Min: 1, Max: 20"
                validInvalid($(this), error_message, valid = false);
            }

            if ($rhySeq.val() !== "") {
                validateRhymesSequence();
            }
        }
    );


    $verLen.on(
        "change, blur",
        function () {
            let verLenVal = $(this).val();

            if (verLenVal === "") {
                resetToNeutral($(this), "Min: 5, Max: 14");
            } else if (4 < verLenVal && verLenVal < 15) {
                let message = "Me gusta, no parece un número indigesto.";
                validInvalid($(this), message, valid = true);
            } else {
                let error_message = "Sólo números. Min: 5, Max: 14"
                validInvalid($(this), error_message, valid = false);
            }
        }
    );


    $rhySeq.keyup(
        function () {
            showSelect();
            if ($(this).val() === "") {
                resetToNeutral($(this), "Ejemplo: ABBA ABBA")
                hideSelect($selVer);
                $hidden.hide();
            }
        }
    );


    $rhySeq.on(
        "change blur",
        function () {
            validateRhymesSequence();
        }
    );


    $selVer.change(
        function () {
            if ($(this).val() === 'yes') {
                if ($rhySeq.hasClass("is-valid")) {
                    if ($(this).hasClass("is-invalid")) {
                        ;
                        validInvalid($(this), "", valid = true);
                    }
                    $hidden.show();

                } else {
                    let error_message = "La secuencia de rimas ha de ser válida.";
                    validInvalid($(this), error_message, valid = false);
                };
            } else {
                $hidden.hide();
            };
        }
    );


    $("form").submit(
        function (event) {
            if ($(".is-invalid").length > 0) {
                alert("Todavía hay valores incorrectos")
                event.preventDefault();
            }
        }
    );
});
