

function submit_form(username, action) {
    url = '/blog/' + username  + '/' + action +'/'
    $.post(url, {title: $('#id_title').val(),
		 txt: $('#id_txt').val(),
		 tags: $('#id_title').val()},
	   function(xml) {
	       $('#postform').before($('message', xml).html());
	   });
} 