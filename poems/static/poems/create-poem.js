function unique_char(str1) {
   var str=str1;
   var uniql="";
   for (var x=0;x < str.length;x++) {
       if(uniql.indexOf(str.charAt(x))==-1) {
           uniql += str[x];
       }
   }
    return uniql;
}


$('#id_select_verses').on("change", function(){
     if ( $(this).val() === 'yes'){
        var hidden_field = $("#hidden_fieldset")

        hidden_field.empty()

        hidden_field.append($( "<legend></legend>" ).text("Especifica las rimas:"))

        rhy_seq = $("#id_rhy_seq").val()
        rhy_uniq = unique_char(rhy_seq).split('').sort()
        rhy_list = rhy_uniq.join('').trim().split('')

        for (i = 0; i < rhy_list.length; i++) {
           hidden_field.append($("<label>").attr("for", rhy_list[i]).text(`Rima ${rhy_list[i]}:`));
           hidden_field.append($("<br>"));
           hidden_field.append($("<input type='text'>").attr("name", rhy_list[i])
                                                       .attr("id", rhy_list[i])
                                                       .attr("required", "required")
                                                       .attr("validation-url", "{% url 'poems:validate-rhymes' %}"));
           hidden_field.append($("<br>"));
        };

        $('#hidden').show();

    } else {

      hidden_field.empty()
      $('#hidden').hide();
    }
});
