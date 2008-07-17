function comment_action(div_id, action) {
    div = document.getElementById(div_id)
    if (action == "edit") {
	div.innerHTML = "{% include \"comment/edit_form.html\"%}" }
    else {
	div.innerHTML = ""}
}

function displayFormComment(form_id) {
    c=document.getElementById(form_id)
    if (c.style.display == "none") {
	c.style.display="block"
    } else {
	c.style.display = "none"
    }
}		

	