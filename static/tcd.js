$(document).ready(function() {
    
//     $("ads").css("height", $("content").css("height"));

});
    
function displayFormComment(form_id) {

    $(form_id).parents("div.action_block").find("div.comment_action").
    not(form_id).each(function() {
	$(this).hide();
    });

    $(form_id).slideToggle();
}		

function vote(form_id){
    $.post("/vote/", {argument: $(form_id + ' #argument').val(),
		      voter: $(form_id + ' #voter').val(),
		      voted_for: $(form_id + ' #voted_for').val()},
	   function(xml) {
	       addVotes(xml);
	   });
};

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

function delete_comment(id) {
    form_id = '#delete' + id
    
    $.post("comments/delete", {comment_id: id},	   
	   function(xml) { 
	       comID = $("id",xml).text()
	       divID = '#comment_div' + comID
	       if($("status",xml).text() == "error") {
		   $('#confirm_delete' + comID).html($("message", xml).text())		       		   
	       } else {
		   $(divID).html($("comment",xml).text())
	       }

	   }
	  );	       
};

function flag_topic(topic_id, user_id) {
    form_id = 'tflag' + topic_id;

    $.post("/tflag/", {topic_id: topic_id,
		      user_id: user_id},
	   function(xml) {
	       msg = $("message",xml).text();
	       $("#topic_div" + topic_id).after(msg);
	   }
	  )
}

function collapse(div_id, mode) {
    var div = $(div_id);
    var margin = div.css("margin-left");
    
    while ( div.next().css("margin-left") > margin ) {
	
	if (mode == 0) {
	    div.next().css("display", "none");
	} else if (mode == 1) {
	    div.next().css("display", "");
	}

	div = div.next();
    }

    collapseID = div_id.replace(/comment_div/, "collapse");

    if (mode == 0) {
	$(collapseID).html("[+]");
	$(collapseID).attr("href","javascript:collapse('" + div_id + "', 1);");
    } else if (mode == 1) {
	$(collapseID).html("[-]");
	$(collapseID).attr("href","javascript:collapse('" + div_id + "', 0);");
    } else {
	alert("Invalid mode!");
    };
	
};

