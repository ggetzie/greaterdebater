function submit_form(username, action) {
    url = '/blog/' + username  + '/' + action +'/'
    pdata = {title: $('#id_title').val(),
	     txt: $('#id_txt').val(),
	     tags: $('#id_tags').val()}

    if ($('#id_id').val() != 'None') {
	pdata.id = $('#id_id').val();
    }

    $.post(url, pdata,
	   function(xml) {
	       if (action == 'save' || $('status', xml) == 'error') {
		   $('#postform').after($('message', xml).html());
	       } else {
		   window.location = '/blog/' + username + '/post/' + pdata.id.toString();
	       }
	   });
};

function swap(thing1, thing2){
    var temp = $(thing1).html()
    $(thing1).html( $(thing2).html());
    $(thing2).html(temp);
};

function delete_post(username, id) {
    url = '/blog/' + username + '/delete/'
    $.post(url, {id: id},
	   function(xml) {
	       status = $('status', xml).text()
	       if (status == 'error') {
		   $('#postform').after($('message', xml).html());
	       } else {
		   alert( $('message', xml).text());
		   window.location = '/blog/' + username + '/drafts/';
	       }
	   });

};