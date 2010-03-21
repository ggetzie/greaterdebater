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

