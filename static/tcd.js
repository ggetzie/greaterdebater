$(document).ready(function() {


});

function vote(form_id){
    $.post("/vote/", {argument: $(form_id + ' #argument').val(),
		      voter: $(form_id + ' #voter').val(),
		      voted_for: $(form_id + ' #voted_for').val()},
	   function(xml) {
	       addVotes(xml);
	   });
};
    
		   
function displayFormComment(form_id) {

    $(form_id).parents("div.action_block").find("div.comment_action").
    not(form_id).each(function() {
	$(this).hide();
    });

    $(form_id).slideToggle();
}		


function addVotes(xml) {
    var pvotefor
    var dvotefor
    if ($("pvotes",xml).text() == "1") {
	pvotefor = " vote for "
    } else {
	pvotefor = " votes for "
    }

    if ($("dvotes",xml).text() == "1") {
	dvotefor = " vote for "
    } else {
	dvotefor = " votes for "
    }

    $("#vote").html("<p>You voted for " + $("voted_for",xml).text() +
		    "</p><p>Current Tally:<br />" + 
		    $("pvotes",xml).text() +  pvotefor + $("plaintiff",xml).text() + "<br />" + 
		    $("dvotes",xml).text() + dvotefor +  $("defendant",xml).text() + "</p>");
}