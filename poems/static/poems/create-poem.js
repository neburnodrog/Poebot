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


  $(".rhyme_validator").change(function() {
      let inp = $(this);

      $.ajax({
            url: "/validate/",
            data: `${inp.serialize()}&${$rhySeq.serialize()}&${verLen.serialize()}`,
            dataType: 'json',
            success: function(data) {
                if (data.not_valid) {
                  inp.addClass("is-invalid");
                  let parent_div = inp.parent();
                  parent_div.children().last().remove();
                  $("<div></div>").appendTo(parent_div)
                      .addClass("invalid-feedback")
                      .text(data.error_message);

                }
            }
      });
  });
  $('#hidden').show();
};


function showLabel() {
  $selGroup
      .children()
      .eq(0)
        .show()
        .end()
      .eq(1)
        .show()
        .end();
};


function hideLabel() {
  $selGroup
      .children()
      .eq(0)
        .hide()
        .end()
      .eq(1)
        .hide()
        .end();
};


//VARIABLES
const $rhySeq = $("#id_rhy_seq")
const $selGroup = $("div.form-group").has("select")
const $hidden_field = $("#hidden_fieldset");
const verLen = $("#id_verse_length");


// CONTROL FLOW
if ( $rhySeq.val() === "" ) {
    hideLabel();
} else {
    showLabel();
};


if ( $(".invalid-feedback").length ) {
    $(".invalid-feedback")
          .parent()
          .children()
          .eq(1)
          .addClass("is-invalid");
};


if ( $selGroup.children().eq(1).val() === "yes" ) {
    createFormDinamically();
};

// EVENT TRIGGERS
$rhySeq.keypress( function () {
  showLabel();
  if ($(this).val() === "") {
      hideLabel();
  };
;})


$('#id_select_verses').on("change", function(){
     if ( $(this).val() === 'yes') {
          createFormDinamically();
    } else {
      $("#hidden_fieldset").empty();
      $('#hidden').hide();
    };
});
