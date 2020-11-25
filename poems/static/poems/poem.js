
$(document).ready(function () {

  function swap(a, b) {
      let a_mark = $("<span>").insertAfter(a);
      let b_mark = $("<span>").insertAfter(b);
      b.insertBefore(a_mark);
      a.insertBefore(b_mark);
      a_mark.remove();
      b_mark.remove();

  };

  $( '#reload' ).click( function() {
      location.reload();
  });

  $( ".verse" ).click( function() {
      $( this ).attr("contenteditable", true);
      $( this ).blur( function() {
          $( this ).attr("contenteditable", false);
      });
  });

  $( ".bi-arrow-down-short" ).click( function() {
    let verse = $(this).parent().next().children();
    let verse_index = verse.index($( ".verse" ));
    let verse_to_change_with = $( ".verse" ).eq(verse_index + 1);
    swap(verse, verse_to_change_with);

  });

  $( ".bi-arrow-up-short" ).click( function() {
    let verse = $(this).parent().next().children();
    let verse_index = verse.index($( ".verse" ));
    let verse_to_change_with = $( ".verse" ).eq(verse_index + -1);
    swap(verse, verse_to_change_with);

  })
  ;
});
