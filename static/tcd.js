$(document).ready(function() {

    $("div[@class=comment_action]").hide()
//     $("form[@class=Ballot]").submit(function(){
// 	$.post("/vote/", {argument: $(this).("input[@name=argument]").val(),
// 			  voter: $(this).("input[@name=voter]").val(),
// 			  voted_for: $(this).("input[@name=voted_for]").val()},
// 	       function(xml) {
// 		   addVotes(xml);
// 	       });
// 	return false;
//     });
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
    $("#vote").html("<p>You voted for " + $("voted_for",xml).text() +
		    "</p><p>Current Tally:<br />" + $("pvotes",xml).text() +  
		    " votes for " + $("plaintiff",xml).text() +
		    "<br />" + $("dvotes",xml).text() + " votes for " + 
		    $("defendant",xml).text() + "<br /></p>");
}