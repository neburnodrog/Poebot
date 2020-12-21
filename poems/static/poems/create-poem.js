

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


    // jQuery SELECTOR variables
    const $rhySeq = $("#id_rhy_seq");
    const $hiddenForm = $("#hidden-form");
    const $verLen = $("#id_verse_length");
    const $verNum = $("#id_ver_num");
    const $selVer = $( '#id_select_verses' );
    const $submit = $( "#submit" );


    /*## FUNCTIONS ##*/
    function choose_message( rhyme_type ) {
        if (rhyme_type === "consonante") {
            word = conson_words[Math.floor(Math.random() * conson_words.length)];
        } else {
            word = asson_words[Math.floor(Math.random() * asson_words.length)];
        }
        return `O la palabra: '${word[0]}', o la rima: '${word[1]}'`
    }


    function uniqueChar( rhymeSequence ) {
        let uniqueValuesArray = [];
        for (var i = 0; i < rhymeSequence.length; i++) {
            if ( uniqueValuesArray.includes(rhymeSequence[i]) ) {
            } else {
                uniqueValuesArray.push(rhymeSequence[i]);
            }
        }
        return uniqueValuesArray;
    }


    function uniqueRhymes( rhymeSequenceString ) {
        /* return it as array without the whitespaces */
        let rhySequenceArray = rhymeSequenceString
            .split(' ')
            .join('')
            .split('');
        return uniqueChar(rhySequenceArray);
    }


    function createInput( rhymeKey, rhymeType ) {
        let input = $(
            "<input>",
            {
                type:"text",
                class:"form-control rhyme_validator",
                name: rhymeKey,
                id: rhymeKey,
                required: true,
            }
        );

        input.change(
            function() {
                if ( /^-?[a-zA-ZñÑÓóÁáÉéíÍúÚü]+$/.test( input.val() ) ) {
                    $.ajax({
                        url: "/validate/",
                        data: `${input.serialize()}&${$rhySeq.serialize()}&${$verLen.serialize()}`,
                        dataType: 'json',
                        success: function(data) {
                            if (data.not_valid) {
                                validInvalid( input, data.error_message, valid=false )
                            } else {
                                validInvalid( input, "Tiene buena pinta", valid=true )
                            }
                        }
                    });
                } else {
                    error_message = "Solo se permiten caracteres alfabéticos y el guión en caso de especificar la rima."
                    validInvalid( input, error_message, valid=false );
                }
            }
        );

        input.keyup(
            function() {
                if (input.val() === "") {
                    input.removeClass( "is-valid is-invalid" );
                    small = input.next();
                    small.removeClass( "valid-feedback invalid-feedback" );
                    small.addClass( "text-muted" ).text( choose_message(rhymeType) );
                }
            }
        );

        return input;
    }


  function createRhymeField ( rhymeKey, $hiddenForm ) {
      let $rhymeDivRow = $( "<div>", {class: 'row justify-content-center'})
      let $rhymeDivCol = $( "<div>", {class: 'col-auto col-sm-8 mb-2'} );

      let rhymeType;
      if ( rhymeKey === rhymeKey.toUpperCase() ) {
          rhymeType = "consonante";
      } else { rhymeType = "asonante"; }

      let $label = $( "<label>" ).attr("for", rhymeKey).text(`Rima ${rhymeType} ${rhymeKey}:`);
      let $input = createInput( rhymeKey, rhymeType );
      let $small = $( "<small>", {class:'form-text text-muted'} )
            .text(choose_message(rhymeType));

      $hiddenForm.append( $rhymeDivRow );
      $rhymeDivRow.append( $rhymeDivCol );
      $rhymeDivCol.append( $label, $input, $small );
  }


  function createFormDinamically( hiddenForm, rhymeSequence, verseLength ) {
    hiddenForm.empty();

    let sequenceSet = uniqueRhymes(rhymeSequence.val());
    for (i = 0; i < sequenceSet.length; i++) {
      createRhymeField( sequenceSet[i], hiddenForm );
    }
    $('#hidden').show();
  }


  function showSelect( select ) {
    select
      .show()
      .prev()
        .show();
  }


  function hideSelect( select ) {
    select
      .hide()
      .prev()
        .hide();
  }


    function validInvalid( inputElem, msg, valid ) {
        if (valid) {
            inputElem.removeClass("is-invalid").addClass("is-valid");
        } else {
            inputElem.removeClass("is-valid").addClass("is-invalid");
        }

        if ( inputElem.next().length === 0 ) {
            inputElem.parent().append("<small></small>");
        }

        small = inputElem.next().removeClass("text-muted");

        if ( inputElem.hasClass( "is-valid" ) ) {
            small.removeClass( "invalid-feedback" )
                .addClass( "valid-feedback" );
        } else if ( inputElem.hasClass( "is-invalid" ) ) {
            small.removeClass( "valid-feedback" )
               .addClass( "invalid-feedback" );
        }

        small.text(msg);
    }


    function validateRhymesSequence( rhymeInput, verNumVal ) {
        if ( $( rhymeInput ).val() === "" ) {
            let error_message = "Mayúsculas: rima consonante. Minúsculas: asonante. Espacio(s) en blanco: verso en blanco. Ejemplo: ABBA ABBA. Si dejas esta celda en blanco se generarán versos aleatorios"
            validInvalid( $( rhymeInput ), error_message, true );

        //IF NOT ALL CHARACTERS MATCH THE REGEX -> ERROR
        } else if ( /^[a-zA-ZñÑ\s]+$/.test( $( rhymeInput ).val() ) === false ) {
            let error_message = "La secuencia de rimas solo admite caracteres del abecedario y espacios en blanco";
            validInvalid( $( rhymeInput ), error_message, false);

        } else if ( $( rhymeInput ).val().split(" ").join("").length !== verNumVal ) {
            let error_message = "El número de caracteres en la secuencia de rimas ha de coincidir con el numero especificado de versos (sin contar espacios)"
            validInvalid( $( rhymeInput ), error_message, false );

        } else {
            validInvalid( $( rhymeInput ), "Tiene buena pinta", true );
        }
    }

$(document).ready(function () {
// LOGIC AND LISTENERS
    $(".popover").each(function () {
        let text = $(this).parent().prev()
                    .children().eq(0).children()
                    .eq(0).text();
        if (text === "Número de versos:") {
            var message = "Este campo requiere de un número entero positivo menor o igual a 20 para germinar.";
            var where = "top";
        } else if (text === "Longitud de los versos:") {
            var message = "Medidos en número de sílabas (mínimo 5 y máximo 14).";
            var where = "top";
        } else {
            var message = "Ejemplo: ABBA ABBA.\nMayúsculas: rima consonante.\n Minúsculas: rima asonante.\n Espacio en blanco: verso en blanco.";
            var where = "bottom";
        }

        $(this).attr("data-placement", where).attr("data-content", message);
    })

    $('[data-toggle="popover"]').popover()

    if ( $rhySeq.val() !== "" ) {
        showSelect($selVer);
    };

    if ( $selVer.val() === "yes" ) {
        createFormDinamically( $hiddenForm, $rhySeq, $verLen );
        var $rhyValid = $(".form-control.rhyme_validator");
    };

    //EVENT LISTENERS
    $verNum.on(
        "change, blur", function() {
            let verNumVal = Number( $( this ).val() );

            if ( 0 < verNumVal && verNumVal < 21 ) {
                validInvalid( $( this ), "Esto tiene buena pinta.", valid=true );/* Tiene buena pinta */
            } else if ( verNumVal === "" ) {
                message = "Se generan un número aleatorio de versos."
                validInvalid( $( this ), message, valid=true );
            } else {
                error_message = "Sólo números. Min: 1, Max: 20"
                validInvalid( $( this ), error_message, valid=false );
            }

            if ( $rhySeq.val() !== "" ){
                validateRhymesSequence($rhySeq, verNumVal);
            }
        }
    );


    $verLen.on(
        "change, blur", function() {
            let verLenVal = Number ( $( this ).val() );

            if ( verLenVal === "") {
                message = "Se generarán versos de tamaño aleatorio"
                validInvalid( $( this ), message, valid=true );

            } else if ( 4 < verLenVal && verLenVal < 20 ) {
                message = "Me gusta, no parece un número indigesto."
                validInvalid( $( this ), message, valid=true ); /* Tiene buena pinta */

            } else {
                error_message = "Sólo números. Min: 5, Max: 14"
                validInvalid( $( this ), error_message, valid=false );
            };
        }
    );


    $rhySeq.keyup(
        function () {
            showSelect($selVer);
            if ( $( this ).val() === "" ) {
                hideSelect($selVer);
                $("#hidden").hide();
            }
        }
    );


    $rhySeq.on(
        "change blur", function() {
            let verNumVal = Number($verNum.val());

            if ( $( this ).val() === "" ) {
                validInvalid( $( this ), "Si dejas esta celda en blanco se generarán versos sin rima", valid=true );

            //IF NOT ALL CHARACTERS MATCH THE REGEX -> ERROR
            } else if ( /^[a-zA-ZñÑ\s]+$/.test( $( this ).val() ) === false ) {
                let error_message = "La secuencia de rimas solo admite caracteres del abecedario y espacios en blanco";
                validInvalid( $( this ), error_message, valid=false );

            } else if ( $( this ).val().split(" ").join("").length !== verNumVal ) {
                let error_message = "El número de caracteres en la secuencia de rimas ha de coincidir con el numero especificado de versos (sin contar espacios)"
                validInvalid( $( this ), error_message, valid=false );

            } else {
                validInvalid( $( this ), "Tiene buena pinta", valid=true );
                if ( $selVer.val() == "yes" ) {
                    $selVer.removeClass("is-invalid").addClass("is-valid");
                    validInvalid($selVer, "Ahora sí que puedes elejir las rimas", valid=true );
                    createFormDinamically($hiddenForm, $rhySeq, $verLen);
                }
            }
        }
    );


  $selVer.change(function() {
       if ( $(this).val() === 'yes' ) {

             if ( $rhySeq.hasClass( "is-valid" ) ) {

                   if ( $( this ).hasClass("is-invalid") ) {
                         let message = "Ahora sí que tiene buena pinta, elije las rimas.";
                         validInvalid( $( this ), message, valid=true);
                   }
                   createFormDinamically($hiddenForm, $rhySeq, $verLen);

             } else {
                   let error_message = "La secuencia de rimas ha de ser válida para poder elegir las rimas";
                   validInvalid( $( this ), error_message, valid=false );
             };
      } else {
        $( "#hidden" ).hide();
      };
  });

  $submit.click(
      function(event) {
          if ( $(".is-invalid").length === 0 ) {
          } else {
              event.preventDefault;
          }
      }
  );

});
