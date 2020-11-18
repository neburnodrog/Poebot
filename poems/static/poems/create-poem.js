$(document).ready(function () {

  // HELPER FUNCS
  function uniqueChar(str1) {
     let str=str1;
     let uniql="";
     for (var x=0;x < str.length;x++) {
         if(uniql.indexOf(str.charAt(x))==-1) {
             uniql += str[x];
         }
     }
      return uniql;
  }


  function uniqueRhymes() {
      let rhySequence = $rhySeq.val()
      let rhyUniq = uniqueChar(rhySequence).split('').sort()
      let rhyList = rhyUniq.join('').trim().split('')
      return rhyList;
  };


  function isUpperCase(str) {
      return str === str.toUpperCase();
  };


  function createFormDinamically() {
      $hidden_field.empty();
      $hidden_field.append($( "<legend></legend>" ).text("Especifica las rimas:"));

      let seq_list = uniqueRhymes();

      for (i = 0; i < seq_list.length; i++) {
         let $div = $("<div></div>").addClass("form-group").appendTo($hidden_field)
         let seq_key = seq_list[i];

         if (isUpperCase(seq_key)) {
              $div.append($("<label>")
                           .attr("for", seq_list[i])
                           .text(`Rima consonante ${seq_list[i]}:`)
                           );
         } else {
              $div.append($("<label>")
                           .attr("for", seq_list[i])
                           .text(`Rima asonante ${seq_list[i]}:`)
                           );
         };

         $div.append($("<input type='text'>")
                      .attr("name", seq_list[i])
                      .attr("id", seq_list[i])
                      .attr("class", "form-control rhyme_validator")
                      .attr("required", "required")
                      );

         if (isUpperCase(seq_key)) {
              $div.append($("<small></small>")
                          .attr("class", "form-text text-muted")
                          .text("Aquí una rima consonante o una palabra. Ejemplo: '-oba' para rimar consonantemente con 'alcoba'. Si no la palabra directamente: 'amor'")
                          );
         } else {
              $div.append($("<small></small>")
                          .attr("class", "form-text text-muted")
                          .text("Aquí una rima asonante o una palabra. Ejemplo: '-aa' para rimar asonantemente con 'naranja'. Si no la palabra directamente: 'muerte'")
                          );
      };
    };

    let $rhyValid = $(".rhyme_validator");

    $rhyValid.change(function() {
        let $inp = $(this);
        let $smallTag = $inp.next();
        let $invalidFeed = $("<div></div>")
                            .attr("class", "invalid-feedback");
        let $validFeed = $("<div></div>")
                            .attr("class", "valid-feedback")
                            .text("Looks good!");

        $.ajax({
              url: "/validate/",
              data: `${$inp.serialize()}&${$rhySeq.serialize()}&${$verLen.serialize()}`,
              dataType: 'json',
              success: function(data) {

                  if (data.not_valid) {
                    $inp.addClass("is-invalid");
                    $inp.removeClass("is-valid")
                    $smallTag.hide();
                    $invalidFeed.text(data.error_message).insertAfter($smallTag);
                    $validFeed.insertAfter($invFeed).hide();

                  } else {
                    $inp.removeClass("is-invalid");
                    $inp.addClass("is-valid");
                    $smallTag.hide();
                    $validFeed.insertAfter($smallTag).show();
                    $invalidFeed.insertAfter($validFeed).hide();


                  };
              }
        });
    });
    $('#hidden').show();
  };


  function showSelect() {
    $selGroup
        .children()
        .eq(0)
          .show()
          .end()
        .eq(1)
          .show();
  };


  function hideSelect() {
    $selGroup
        .children()
        .eq(0)
          .hide()
          .end()
        .eq(1)
          .hide();
  };


  //VARIABLES
  const $rhySeq = $("#id_rhy_seq");
  const $selGroup = $("div.form-group").has("select");
  const $hidden_field = $("#hidden_fieldset");
  const $verLen = $("#id_verse_length");
  const $verNum = $("#id_ver_num");
  const $selVer = $( '#id_select_verses' )


  // CONTROL FLOW
  if ( $rhySeq.val() === "" ) {
      hideSelect();
  } else {
      showSelect();
  };

  if ( $selGroup.children().eq(1).val() === "yes" ) {
      createFormDinamically();
  };

  // EVENT TRIGGERS
  $rhySeq.keyup( function () {
    showSelect();

    let rhySeqVal = $rhySeq.val();
    let $small = $(this).next();
    let $feed = $small.next();

    if ( /^[a-zA-ZñÑ\s]+$/.test(rhySeqVal) === false ) {
        $(this).addClass("is-invalid");
        $small.hide();
        $feed.addClass("invalid-feedback")
             .text("La secuencia de rimas solo admite caracteres del abecedario y espacios en blanco")
             .show();
    };

    if ( $(this).val() === "" ) {
      $(this).removeClass("is-valid").removeClass("is-invalid");
      $small.show();
      $feed.removeClass("invalid-feedback")
           .text("")
           .hide();
    };

  });

  $rhySeq.change( function(){
    let verNumVal = Number($verNum.val());
    let rhySeqVal = $(this).val();

    if ( rhySeqVal.split(" ").join("").length === verNumVal ) {
        if ( /^[a-zA-ZñÑ\s]+$/.test($(this).val()) === false ) {
            $(this).removeClass("is-invalid").addClass("is-valid");
        };
    } else {
        $(this).removeClass("is-valid").addClass("is-invalid");

        let $small = $(this).next();
        $small.hide();

        let $feed = $small.next()
        $feed.addClass("invalid-feedback")
           .text("El número de caracteres en la secuencia de rimas ha de coincidir con el numero especificado de versos (sin contar espacios)")
    };
  });

  $selVer.change(function() {
       if ( $(this).val() === 'yes') {
            createFormDinamically();
      } else {
        $( "#hidden_fieldset" ).empty();
        $( '#hidden' ).hide();
      };
  });

  $verNum.change( function() {
    $(this).toggleClass("is-valid")
  });

  $verLen.change( function() {
    let verLenVal = $(this).val()
    if ( 4 < $(this).val() && $(this).val() < 20 ){
      $(this).removeClass("is-invalid").addClass("is-valid");
    } else {
      $(this).removeClass("is-valid").addClass("is-invalid");
    };
  });

});
