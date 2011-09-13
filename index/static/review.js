function decide(id, item, decision) {
    url = '/decide/'+ item +'/'
    $.post(url, {'id': id,
		 'decision': decision},
	   function(xml) {
	       divid = '#' + item + '_div' + id
	       if ($("status", xml).text() == "alert") {
		   alert($('message', xml).text());
	       } else {
		   $(divid).parent().replaceWith($('message', xml).html())
	       } 
	   });
		   
}

function decide_checked(item, decision) {
    url = '/decide/' + item + '/'
    var checked_items = [];
    var cmd_row = $("#cmd_row").html();
    $("#cmd_row").html("Loading...");
    $('.message').each( function(i) {
	if ($(this).attr('checked')) {
	    checked_items.push($(this).attr('value'))}})

    if (checked_items.length == 0) {
	$('#sys_messages').html("No items selected"); 
    } else {    
	$.post(url, {'id_list': checked_items.toString(),
		     'decision': decision},
	       function(xml){
		   jQuery.each(checked_items, function() {
		       $('#message_row' + this).remove()
		   })
		   $('#sys_messages').html($("message",xml))
	       })
    }
    $("#cmd_row").html(cmd_row);
}