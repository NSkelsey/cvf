function reorder(total){
  $("li.rvote").each(function (i) {
    $(this).find(':input').each(function() {
      var name = $(this).attr('name').replace(/-\d*-/,'-' + i + '-');
      var id = 'id_' + name;
      $(this).attr({'name': name, 'id': id, });
      if ($(this).attr('name') == "form-" + i + "-position"){
        $(this).attr({'value': i});
      }

    });
    $(this).find('label').each(function() {
      var newFor = $(this).attr('for').replace(/-\d*-/,'-' + i + '-');
      $(this).attr('for', newFor);
    });
  });
}



$(function() {
        $( "#sortable" ).sortable({stop: function( event, ui ){
          reorder();
        }});
    });
