function add_checked() {
    var checked_items = [];
    $('.message').each( function(i) {
	if ($(this).attr('checked')) {
	    checked_items.push($(this).attr('value'))}})
     if (checked_items.length == 0) {
	return false;
    } else {
	$("#id_id_list").attr('value', checked_items.toString());
	return true;
    }
}