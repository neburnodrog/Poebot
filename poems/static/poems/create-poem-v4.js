"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var jquery_1 = __importDefault(require("jquery"));
jquery_1.default(document).ready(function () {
    // jQuery SELECTOR variables
    var $rhySeq = jquery_1.default("#id_rhy_seq");
    var $hiddenContainer = jquery_1.default("#hidden-container");
    var $hidden = jquery_1.default("#hidden");
    var $verLen = jquery_1.default("#id_verse_length");
    var $verNum = jquery_1.default("#id_ver_num");
    var $selVer = jquery_1.default("#id_select_verses");
    var $hiddenSelGroup = jquery_1.default("#hidden_select_group");
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
            if (uniqueValuesArray.includes(rhymeSequence[i])) {
            }
            else {
                uniqueValuesArray.push(rhymeSequence[i]);
            }
        }
        return uniqueValuesArray;
    }
    function uniqueRhymes(rhymeSequenceString) {
        /* return it as array without the whitespaces */
        var rhySequenceArray = rhymeSequenceString
            .split(" ")
            .join("")
            .split("");
        return uniqueChar(rhySequenceArray);
    }
    /*## CREATE FORM DINAMICALLY FUNCS ##*/
    function createInput(rhymeKey, rhymeType) {
        var input = jquery_1.default("<input>", {
            type: "text",
            class: "form-control rhyme_validator",
            name: rhymeKey,
            id: rhymeKey,
            required: true,
        });
        input.keyup(function () {
            if (jquery_1.default(this).val() === "") {
                resetToNeutral(jquery_1.default(this), choose_message(rhymeType));
            }
        });
        input.change(function () {
            var $input = jquery_1.default(this);
            var inputVal = String($input.val());
            if (/^-?[a-zA-ZñÑÓóÁáÉéíÍúÚü]+$/.test(inputVal)) {
                jquery_1.default.ajax({
                    url: "/validate/",
                    data: jquery_1.default(this).serialize() +
                        "&" +
                        $rhySeq.serialize() +
                        "&" +
                        $verLen.serialize(),
                    dataType: "json",
                    success: function (resp_data) {
                        if (resp_data.not_valid) {
                            validInvalid($input, resp_data.error_message, false);
                        }
                        else {
                            validInvalid($input, "La rima es válida y existe en la base de datos.", true);
                        }
                    },
                });
            }
            else {
                var err_msg = "Solo se permiten caracteres alfabéticos y el guión.";
                validInvalid(jquery_1.default(this), err_msg, false);
            }
        });
        return input;
    }
    function createRhymeField(rhymeKey) {
        var $rhymeDivRow = jquery_1.default("<div>", {
            class: "row justify-content-center",
        });
        var $rhymeDivCol = jquery_1.default("<div>", {
            class: "col-auto col-sm-8 mb-2",
        });
        var rhymeType;
        if (rhymeKey === rhymeKey.toUpperCase()) {
            rhymeType = "consonante";
        }
        else {
            rhymeType = "asonante";
        }
        var $label = jquery_1.default("<label>")
            .attr("for", rhymeKey)
            .text("Rima " + rhymeType + " " + rhymeKey + ":");
        var $input = createInput(rhymeKey, rhymeType);
        var $small = jquery_1.default("<small>", {
            class: "form-text text-muted",
        }).text(choose_message(rhymeType));
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
            small.removeClass("invalid-feedback").addClass("valid-feedback");
        }
        else if (inputElem.hasClass("is-invalid")) {
            small.removeClass("valid-feedback").addClass("invalid-feedback");
        }
        small.text(msg);
    }
    function resetToNeutral(inputElem, msg) {
        inputElem.removeClass("is-invalid").removeClass("is-valid");
        var small = inputElem
            .next()
            .removeClass("invalid-feedback")
            .removeClass("valid-feedback")
            .addClass("text-muted")
            .text(msg);
    }
    /*## RHYMES SEQUENCE INPUT VALIDATION FUNCS ##*/
    function rhySeqIsValid() {
        var verNumVal = String($verNum.val());
        var rhySeqVal = String($rhySeq.val());
        if (/^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == true &&
            rhySeqVal.split(" ").join("").length == Number(verNumVal)) {
            selVerIsValid();
            validInvalid($rhySeq, "Tiene buena pinta", true);
            return true;
        }
        else if (/^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) == false) {
            var err_msg_1 = "Solo valen caracteres del abecedario y espacios en blanco";
            validInvalid($rhySeq, err_msg_1, false);
            selVerIsValid();
            return false;
        }
        var err_msg = "El número de caracteres ha de coincidir con el número de versos (sin contar espacios)";
        validInvalid($rhySeq, err_msg, false);
        selVerIsValid();
        return false;
    }
    function rhySeqOnLoad() {
        if ($rhySeq.val() === "") {
            resetToNeutral($rhySeq, "Ejemplo: ABBA ABBA");
            $hidden.hide();
            $hiddenSelGroup.hide();
        }
        else {
            $hiddenSelGroup.show();
            if ($selVer.val() === "yes" && rhySeqIsValid()) {
                createFormDinamically();
                $hidden.show();
            }
        }
    }
    /*## NUMBER OF VERSES INPUT FIELD VALIDATION FUNCS ##*/
    function verNumIsValid() {
        var verNumVal = $verNum.val();
        if (typeof verNumVal === "string") {
            if ($verNum.val() == "") {
                resetToNeutral($verNum, "Min: 1, Max: 20");
                return true;
            }
            else if (0 < +verNumVal && +verNumVal < 21) {
                validInvalid($verNum, "Tiene buena pinta.", true);
                return true;
            }
            validInvalid($verNum, "Solo números. Min: 1, Max: 20", false);
            return false;
        }
        return false;
    }
    /*## LENGTH OF VERSES INPUT FIELD VALIDATION FUNCS ##*/
    function verLenIsValid() {
        var verLenVal = $verLen.val();
        if (typeof verLenVal === "string") {
            if ($verLen.val() == "") {
                resetToNeutral($verLen, "Min: 5, Max: 14");
            }
            else if (4 < +verLenVal && +verLenVal < 15) {
                validInvalid($verLen, "Tiene buena pinta.", true);
                return true;
            }
            validInvalid($verLen, "Solo números. Min: 5, Max: 14", false);
            return false;
        }
        return false;
    }
    function selVerIsValid() {
        if (String($selVer.val()) === "yes") {
            if ($rhySeq.hasClass("is-valid")) {
                if ($selVer.hasClass("is-invalid")) {
                    validInvalid($selVer, "", true);
                }
                createFormDinamically();
                $hidden.show();
            }
            else {
                var error_message = "La secuencia de rimas ha de ser válida.";
                validInvalid($selVer, error_message, false);
                $hiddenContainer.empty();
                $hidden.hide();
            }
        }
        else {
            $hiddenContainer.empty();
            $hidden.hide();
        }
    }
    /*## POPOVER ACTIVATION ##*/
    jquery_1.default(".popover").each(function () {
        var text = jquery_1.default(this)
            .parent()
            .prev()
            .children()
            .eq(0)
            .children()
            .eq(0)
            .text();
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
        jquery_1.default(this).attr("data-placement", where).attr("data-content", message);
    });
    jquery_1.default('[data-toggle="popover"]').popover({
        trigger: "focus",
    });
    /* ON READY VERIFICATION OF FIELDS */
    verNumIsValid();
    verLenIsValid();
    rhySeqOnLoad();
    selVerIsValid();
    /*## EVENT LISTENERS ##*/
    $verNum.on("change, blur", function () {
        var verNumVal = jquery_1.default(this).val();
        if (typeof verNumVal === "string") {
            if (verNumVal === "")
                resetToNeutral(jquery_1.default(this), "Min: 1, Max: 20");
            else if (0 < +verNumVal && +verNumVal < 21) {
                validInvalid(jquery_1.default(this), "Esto número tiene buena pinta.", true); /* Tiene buena pinta */
            }
            else
                validInvalid(jquery_1.default(this), "Sólo números. Min: 1, Max: 20", false);
            if ($rhySeq.val() !== "")
                rhySeqIsValid();
        }
    });
    $verLen.on("change, blur", function () {
        var verLenVal = jquery_1.default(this).val();
        if (typeof verLenVal === "string") {
            if (verLenVal === "") {
                resetToNeutral(jquery_1.default(this), "Min: 5, Max: 14");
            }
            else if (4 < +verLenVal && +verLenVal < 15) {
                var message = "Me gusta, no parece un número indigesto.";
                validInvalid(jquery_1.default(this), message, true);
            }
            else {
                var error_message = "Sólo números. Min: 5, Max: 14";
                validInvalid(jquery_1.default(this), error_message, false);
            }
        }
    });
    $rhySeq.keyup(function () {
        $hiddenSelGroup.show();
        if (jquery_1.default(this).val() === "") {
            resetToNeutral(jquery_1.default(this), "Ejemplo: ABBA ABBA");
            $hiddenContainer.empty;
            $hiddenSelGroup.hide();
            $hidden.hide();
        }
    });
    $rhySeq.on("change blur", function () {
        rhySeqIsValid();
    });
    $selVer.change(function () {
        selVerIsValid();
    });
    jquery_1.default("form").submit(function (event) {
        if (jquery_1.default(".is-invalid").length > 0) {
            alert("Todavía hay valores incorrectos");
            event.preventDefault();
        }
        else {
            /*<button class="btn btn-primary" type="button" disabled>
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
                </button>*/
            var $submit = jquery_1.default("#submit")
                .attr("disabled", "true")
                .text(" Generar Poema");
            var $loadingGif = jquery_1.default("<span>", {
                class: "spinner-border spinner-border-sm",
            });
            $submit.prepend($loadingGif);
            jquery_1.default(this).off().submit();
        }
    });
});
