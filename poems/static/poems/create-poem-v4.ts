$(document).ready(function () {

    // jQuery SELECTOR variables
    const $rhySeq = $("#id_rhy_seq");
    const $hiddenContainer = $("#hidden-container");
    const $hidden = $("#hidden");
    const $verLen = $("#id_verse_length");
    const $verNum = $("#id_ver_num");
    const $selVer = $('#id_select_verses');
    const $hiddenSelGroup = $('#hidden_select_group');

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

    /*## HELPER FUNCTIONS ##*/
    function choose_message(rhyme_type: string) {
        if (rhyme_type === "consonante") {
            var word = conson_words[Math.floor(Math.random() * conson_words.length)];
        } else {
            var word = asson_words[Math.floor(Math.random() * asson_words.length)];
        }
        return `O la palabra: '${word[0]}', o la rima: '${word[1]}'`
    }
    function uniqueChar(rhymeSequence: string[]) {
        let uniqueValuesArray: Array<string> = [];
        for (let i = 0; i < rhymeSequence.length; i++) {
            if (uniqueValuesArray.includes(rhymeSequence[i])) { } else {
                uniqueValuesArray.push(rhymeSequence[i]);
            }
        }
        return uniqueValuesArray;
    }
    function uniqueRhymes(rhymeSequenceString: string): string[] {
        /* return it as array without the whitespaces */
        let rhySequenceArray: string[] = rhymeSequenceString
            .split(' ')
            .join('')
            .split('');
        return uniqueChar(rhySequenceArray);
    }

    /*## CREATE FORM DINAMICALLY FUNCS ##*/
    function createInput(rhymeKey: string, rhymeType: string) {
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
                let inputVal = String($(this).val());
                if (/^-?[a-zA-ZñÑÓóÁáÉéíÍúÚü]+$/.test(inputVal)) {
                    $.ajax({
                        url: "/validate/",
                        data: $(this).serialize() + "&" + $rhySeq.serialize() + "&" + $verLen.serialize(),
                        dataType: 'json',
                        success: function (data) {
                            if (data.not_valid) {
                                validInvalid($(this), data.error_message, false)
                            } else {
                                validInvalid($(this), "La rima es válida y existe en la base de datos.", true)
                            }
                        }
                    });

                } else {
                    let err_msg = "Solo se permiten caracteres alfabéticos y el guión."
                    validInvalid($(this), err_msg, false);
                }
            }
        );

        return input;
    }
    function createRhymeField(rhymeKey: string): void {
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

        $hiddenContainer.append($rhymeDivRow);
        $rhymeDivRow.append($rhymeDivCol);
        $rhymeDivCol.append($label, $input, $small);
    }
    function createFormDinamically(): void {
        let rhySeqVal = String($rhySeq.val())
        $hiddenContainer.empty();

        let sequenceSet = uniqueRhymes(rhySeqVal);
        for (var i = 0; i < sequenceSet.length; i++) {
            createRhymeField(sequenceSet[i]);
        }
        $hidden.show();
    }


    /*## CHANGE ELEMENTS TO VALID/INVALID/NEUTRAL STATE FUNCS ##*/
    function validInvalid(inputElem, msg: string, valid: boolean) {
        if (valid) {
            inputElem.removeClass("is-invalid").addClass("is-valid");
        } else {
            inputElem.removeClass("is-valid").addClass("is-invalid");
        }

        if (inputElem.next().length === 0) {
            inputElem.parent().append("<small></small>");
        }

        let small = inputElem.next().removeClass("text-muted");

        if (inputElem.hasClass("is-valid")) {
            small.removeClass("invalid-feedback")
                .addClass("valid-feedback");
        } else if (inputElem.hasClass("is-invalid")) {
            small.removeClass("valid-feedback")
                .addClass("invalid-feedback");
        }

        small.text(msg);
    }
    function resetToNeutral(inputElem, msg: string) {
        inputElem.removeClass("is-invalid").removeClass("is-valid");
        let small = inputElem.next().removeClass("invalid-feedback")
            .removeClass("valid-feedback")
            .addClass("text-muted")
            .text(msg);
    }


    /*## RHYMES SEQUENCE INPUT VALIDATION FUNCS ##*/
    function rhySeqIsValid(): boolean {
        let verNumVal = String($verNum.val());
        let rhySeqVal = String($rhySeq.val());

        if (
            /^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == true &&
            rhySeqVal.split(" ").join("").length == Number(verNumVal)
        ) {
            selVerIsValid();
            validInvalid($rhySeq, "Tiene buena pinta", true);
            return true;

        } else {
            if (/^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == false) {
                let err_msg = "Solo valen caracteres del abecedario y espacios en blanco";
                validInvalid($rhySeq, err_msg, false);
                selVerIsValid();
                return false;

            } else if (rhySeqVal.split(" ").join("").length != Number(verNumVal)) {
                let err_msg = "El número de caracteres ha de coincidir con el número de versos (sin contar espacios)"
                validInvalid($rhySeq, err_msg, false);
                selVerIsValid();
                return false;
            }
        }
    }
    function rhySeqOnLoad(): void {
        if ($rhySeq.val() === "") {
            resetToNeutral($rhySeq, "Ejemplo: ABBA ABBA");
            $hidden.hide();
            $hiddenSelGroup.hide();
        } else {
            $hiddenSelGroup.show();

            if ($selVer.val() === "yes" && rhySeqIsValid()) {
                createFormDinamically();
                $hidden.show();
            }
        }
    }

    /*## NUMBER OF VERSES INPUT FIELD VALIDATION FUNCS ##*/
    function verNumIsValid() {
        let verNumVal = $verNum.val();

        if ($verNum.val() == "") {
            resetToNeutral($verNum, "Min: 1, Max: 20");
            return true;
        } else if (0 < verNumVal && verNumVal < 21) {
            validInvalid($verNum, "Tiene buena pinta.", true);
            return true;
        } else {
            validInvalid($verNum, "Solo números. Min: 1, Max: 20", false);
            return false;
        }
    }

    /*## LENGTH OF VERSES INPUT FIELD VALIDATION FUNCS ##*/
    function verLenIsValid() {
        let verLenVal = $verLen.val();

        if ($verLen.val() == "") {
            resetToNeutral($verLen, "Min: 5, Max: 14");
        } else if (4 < verLenVal && verLenVal < 15) {
            validInvalid($verLen, "Tiene buena pinta.", true);
            return true;
        } else {
            validInvalid($verLen, "Solo números. Min: 5, Max: 14", false);
            return false;
        }
    }

    function selVerIsValid() {
        if (String($selVer.val()) === 'yes') {
            if ($rhySeq.hasClass("is-valid")) {
                if ($selVer.hasClass("is-invalid")) {
                    validInvalid($selVer, "", true);
                }
                createFormDinamically();
                $hidden.show();

            } else {
                let error_message = "La secuencia de rimas ha de ser válida.";
                validInvalid($selVer, error_message, false);
                $hiddenContainer.empty();
                $hidden.hide();
            };
        } else {
            $hiddenContainer.empty();
            $hidden.hide();
        };
    }

    /*## POPOVER ACTIVATION ##*/
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


    /* ON READY VERIFICATION OF FIELDS */
    verNumIsValid();
    verLenIsValid();
    rhySeqOnLoad();
    selVerIsValid();


    /*## EVENT LISTENERS ##*/
    $verNum.on(
        "change, blur",
        function () {
            let verNumVal = $(this).val();

            if (verNumVal === "") {
                resetToNeutral($(this), "Min: 1, Max: 20");
            } else if (0 < verNumVal && verNumVal < 21) {
                validInvalid($(this), "Esto número tiene buena pinta.", true); /* Tiene buena pinta */
            } else {
                let error_message = "Sólo números. Min: 1, Max: 20"
                validInvalid($(this), error_message, false);
            }

            if ($rhySeq.val() !== "") {
                rhySeqIsValid();
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
                validInvalid($(this), message, true);
            } else {
                let error_message = "Sólo números. Min: 5, Max: 14"
                validInvalid($(this), error_message, false);
            }
        }
    );
    $rhySeq.keyup(
        function () {
            $hiddenSelGroup.show();
            if ($(this).val() === "") {
                resetToNeutral($(this), "Ejemplo: ABBA ABBA")
                $hiddenContainer.empty;
                $hiddenSelGroup.hide();
                $hidden.hide();
            }
        }
    );
    $rhySeq.on(
        "change blur",
        function () {
            rhySeqIsValid();
        }
    );
    $selVer.change(
        function () {
            selVerIsValid();
        }
    );
    $("form").submit(
        function (event) {
            if ($(".is-invalid").length > 0) {
                alert("Todavía hay valores incorrectos")
                event.preventDefault();
            } else {
                /*<button class="btn btn-primary" type="button" disabled>
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
                </button>*/
                let $submit = $("#submit").attr("disabled", "true").text(" Generar Poema");
                let $loadingGif = $(
                    "<span>", {
                    class: "spinner-border spinner-border-sm",
                }
                );

                $submit.prepend($loadingGif);

                $(this).off().submit();
            }
        }
    );
});
