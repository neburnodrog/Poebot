$(document).ready(function () {

  //## VARIABLES ##//
  const $rhySeq = $("#id_rhy_seq");
  const $hiddenForm = $("#hidden-form");
  const $verLen = $("#id_verse_length");
  const $verNum = $("#id_ver_num");
  const $selVer = $( '#id_select_verses' );
  const $inputs = $("input");
  const $isValid = $(".is_valid");
  const $submit = $("#create-poem");
  const help_messages_assonant = [
    "Aquí o rima asonante o palabra. Ejemplo: '-oa' para rimar asonantemente con 'española'. Si no la palabra directamente: 'muerte'",
    "Una rima asonante o una palabra. Ejemplo: '-aa' para rimar asonantemente con 'naranja'. Si no la palabra directamente: 'muerte'",
    "Elige entre una rima asonante o una palabra. Ejemplo: '-ae' para rimar asonantemente con 'encaje'. Si no la palabra directamente: 'muerte'",
    "Aquí una rima asonante o una palabra. Ejemplo: '-uo' para rimar asonantemente con 'estuco'. Si no la palabra directamente: 'muerte'",
    "Una rima asonante o una palabra. Ejemplo: '-oi' para rimar asonantemente con 'escoliósis'. Si no la palabra directamente: 'muerte'",
    "Elige entre una rima asonante o una palabra. Ejemplo: '-aueo' para rimar asonantemente con 'áureo'. Si no la palabra directamente: 'muerte'",
    "Aquí una rima asonante o una palabra. Ejemplo: '-aa' para rimar asonantemente con 'naranja'. Si no la palabra directamente: 'muerte'",
    "Una rima asonante o una palabra. '-aa' para rimar asonantemente con 'naranja'. Si no la palabra directamente: 'muerte'",
    "Aquí una rima asonante o una palabra. Ejemplo: '-aa' para rimar asonantemente con 'naranja'. Si no la palabra directamente: 'muerte'",

  ];
  const help_messages_consonant = [
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",
    "Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'",

  ];


  //## FUNCTIONS ##//
  function uniqueChar(listX) {
     let list=listX;
     let unique = [];
     for (var i = 0; i < list.length; i++) {
        if ( unique.includes(list[i]) ) {
        } else {
          unique.push(list[i]);
        };
     };
     return unique;
  };

  function uniqueRhymes() {
      let rhySequence = $rhySeq.val()
                               .split(' ')
                               .join('')
                               .split('');

      let rhyUniques = uniqueChar(rhySequence);
      return rhyUniques;
  };

  function isUpperCase(str) {
      return str === str.toUpperCase();
  };

  function createFormDinamically() {
      $hiddenForm.empty();
      // TODO https://getbootstrap.com/docs/4.1/components/collapse/#example

      let seqList = uniqueRhymes();

      for (i = 0; i < seqList.length; i++) {
         let $div = $( "<div></div>" ).addClass("col-6").appendTo($hiddenForm);
         let seqKey = seqList[i];

         if (isUpperCase(seqKey)) {
              $div.append($( "<label>" )
                            .attr("for", seqKey)
                            .text(`Rima consonante ${seqKey}:`));
         } else {
              $div.append($( "<label>" )
                            .attr("for", seqKey)
                            .text(`Rima asonante ${seqKey}:`));
         };

         $div.append( $( "<input type='text'>" )
                      .attr("name", seqKey)
                      .attr("id", seqKey)
                      .attr("class", "form-control rhyme_validator")
                      .attr("required", "required") );

         if (isUpperCase(seqKey)) {
              $div.append($( "<small></small>" )
                          .attr("class", "form-text text-muted")
                          .text("Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'"));
         } else {
              $div.append($( "<small></small>" )
                          .attr("class", "form-text text-muted")
                          .text("Aquí una rima asonante o una palabra. Ejemplo: '-aa' para rimar asonantemente con 'naranja'. Si no la palabra directamente: 'muerte'"));
         };
    };

    let $rhyValid = $(".rhyme_validator");
    $rhyValid.change(function() {
        let $inp = $(this);

        if ( $inp.val().length !== $inp.val().split(" ").join("").length ) {
          error_message = 'No se permiten espacios. O la palabra: "amor", o la rima: "-or"/"-o".';
          validInvalid( $inp, error_messsage );
        } else if ( /^[a-zA-ZñÑ-]+$/.test( $inp.val() ) === false ) {
          error_messsage = "Solo se permiten caracteres alfabéticos y el guión para especificar una rima."
          validInvalid( $inp, error_messsage );
        } else if ( /-/.test($inp.val()) == true && /^-/.test($inp.val()) === false ){
          error_messsage = "El guión solo se permite una vez y al comienzo de la casilla."
          validInvalid( $inp, error_messsage );
        } else {
          $.ajax({
                url: "/validate/",
                data: `${$inp.serialize()}&${$rhySeq.serialize()}&${$verLen.serialize()}`,
                dataType: 'json',
                success: function(data) {

                    if (data.not_valid) {
                      $inp.removeClass("is-valid").addClass("is-invalid");
                      validInvalid( $inp, data.error_message )

                    } else {
                      $inp.removeClass("is-invalid").addClass("is-valid");
                      validInvalid( $inp, "Tiene buena pinta" )

                    };
                }
          });
        };
    });

    $('#hidden').show();
  };

  function showSelect() {
    $selVer
      .show()
      .prev()
        .show();
    };

  function hideSelect() {
    $selVer
      .hide()
      .prev()
        .hide();
    };

  function validInvalid( inputElement, msg ) {
    if ( inputElement.next().length === 0 ) {
        inputElement.parent().append("<small></small>")
    };

    if ( inputElement.hasClass( "is-valid" ) ) {
        inputElement.next() //small>
                        .removeClass( "text-muted invalid-feedback" )
                        .addClass( "valid-feedback" )
                        .text( msg )
    } else if ( inputElement.hasClass( "is-invalid" ) ) {
      inputElement.next()
                      .removeClass( "text-muted valid-feedback" )
                      .addClass( "invalid-feedback" )
                      .text ( msg )
    };
  };

  var validateRhymesSequence = function (element) {
    let verNumVal = Number($verNum.val());

    if ( $( element ).val() === "" ) {
      $( element ).removeClass( "is-invalid" ).addClass( "is-valid" );
      validInvalid( $( element ), "Si dejas esta celda en blanco se generarán versos aleatorios" );

    //IF NOT ALL CHARACTERS MATCH THE REGEX -> ERROR
    } else if ( /^[a-zA-ZñÑ\s]+$/.test( $( element ).val() ) === false ) {
        $( element ).removeClass( "is-valid" ).addClass( "is-invalid" );
        let error_message = "La secuencia de rimas solo admite caracteres del abecedario y espacios en blanco";
        validInvalid( $( element ), error_message );

    } else if ( $( element ).val().split(" ").join("").length !== verNumVal ) {
        $( element ).removeClass( "is-valid" ).addClass( "is-invalid" );
        let error_message = "El número de caracteres en la secuencia de rimas ha de coincidir con el numero especificado de versos (sin contar espacios)"
        validInvalid( $( element ), error_message );

    } else {
        $( element ).removeClass("is-invalid").addClass("is-valid");
        validInvalid( $( element ), "Tiene buena pinta" );

    };
  };

  if ( $rhySeq.val() !== "" ) {
      showSelect();
  };

  if ( $selVer.val() === "yes" ) {
      createFormDinamically();
  };


  // EVENT TRIGGERS
  $rhySeq.keyup( function () {
    showSelect();
    if ( $( this ).val() === "" ) {
        hideSelect();
        $("#hidden").hide();
    };
  });

  $rhySeq.on("change blur focus", function() {
    let verNumVal = Number($verNum.val());

    if ( $( this ).val() === "" ) {
      $( this ).removeClass( "is-invalid" ).addClass( "is-valid" );
      validInvalid( $( this ), "Si dejas esta celda en blanco se generarán versos aleatorios" );

    //IF NOT ALL CHARACTERS MATCH THE REGEX -> ERROR
    } else if ( /^[a-zA-ZñÑ\s]+$/.test( $( this ).val() ) === false ) {
        $( this ).removeClass( "is-valid" ).addClass( "is-invalid" );
        let error_message = "La secuencia de rimas solo admite caracteres del abecedario y espacios en blanco";
        validInvalid( $( this ), error_message );

    } else if ( $( this ).val().split(" ").join("").length !== verNumVal ) {
        $( this ).removeClass( "is-valid" ).addClass( "is-invalid" );
        let error_message = "El número de caracteres en la secuencia de rimas ha de coincidir con el numero especificado de versos (sin contar espacios)"
        validInvalid( $( this ), error_message );

    } else {
        $(this).removeClass("is-invalid").addClass("is-valid");
        validInvalid( $( this ), "Tiene buena pinta" );
        if ( $selVer.val() == "yes" ) {
            $selVer.removeClass("is-invalid").addClass("is-valid");
            validInvalid($selVer, "Ahora sí que puedes elejir las rimas");
            createFormDinamically();
        };
    };
  });

  $selVer.change(function() {
       if ( $(this).val() === 'yes' ) {

             if ( $rhySeq.hasClass( "is-valid" ) ) {

                   if ( $( this ).hasClass("is-invalid") ) {
                         $( this ).removeClass("is-invalid").addClass("is-valid");
                         let message = "Ahora sí que tiene buena pinta, elije las rimas.";
                         validInvalid( $( this ), message);
                   };
                   createFormDinamically();

             } else {
                   $( this ).removeClass("is-valid").addClass("is-invalid");
                   let error_message = "La secuencia de rimas ha de ser válida para poder elegir las rimas";
                   validInvalid( $( this ), error_message );
             };
      } else {
        $( "#hidden" ).hide();
      };
  });

  $verNum.change( function() {
    let verNumVal = Number( $( this ).val() );

    if ( verNumVal > 0 ) {
      $( this ).removeClass("is-invalid").addClass("is-valid");
      validInvalid( $( this ), "Tiene buena pinta." );

    } else {
      $( this ).removeClass("is-valid").addClass("is-invalid");
      validInvalid( $( this ), "El valor ha de ser un número entero positivo" );
    };

    if ( $rhySeq.val() !== "" ){
      validateRhymesSequence($rhySeq);
    }
  });

  $verLen.change( function() {
    let verLenVal = $( this ).val();

    if ( verLenVal === "" ) {
      $( this ).removeClass( "is-invalid" ).addClass( "is-valid" );
      validInvalid( $( this ), "Si dejas este valor en blanco se generarán versos de tamaño variable y aleatorio" );

    } else if ( 3 < verLenVal && verLenVal < 21 ) {
      $( this ).removeClass( "is-invalid" ).addClass( "is-valid" );
      validInvalid( $( this ), "Tiene buena pinta." );

    } else {
      $(this).removeClass( "is-valid" ).addClass( "is-invalid" );
      validInvalid( $( this ), "El valor ha de ser un número entero positivo entre 4 y 20" );
    };
  });
});
