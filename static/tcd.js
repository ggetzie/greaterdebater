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
    
    $.post("/comments/delete/", {comment_id: id},	   
	   function(xml) { 
	       comID = $("id",xml).text()
	       divID = '#comment_div' + comID
	       if($("status",xml).text() == "error") {
		   msg=$("message",xml).text()
		   $('#comment_div' + comID).after(msg)
	       } else {
		   $(divID).html($("comment",xml).text())
	       }

	   }
	  );	       
};

function delete_topic(id) {
        
    $.post("/topics/delete/", {topic_id: id},	   
	   function(xml) { 	       
	       divID = '#topic_div' + id;	       
	       msg=$("message",xml).text()
	       $(divID).after(msg)
	       if ($("status",xml).text() == "success") {		   
		   $(divID).remove()
	       }
	   }
	  );	       
};

function flag_topic(topic_id, user_id) {    

    $.post("/tflag/", {object_id: topic_id},		      
	   function(xml) {
	       msg = $("message",xml).text();
	       $("#topic_div" + topic_id).after(msg);
	   }
	  )
}

function flag_comment(comment_id, user_id) {
    $.post("/comments/flag/", {object_id: comment_id},
	   function(xml){
	       msg = $("message",xml).text();
	       $("#comment_div" + comment_id).after(msg);
	   }
	  )
}

function swap(thing1, thing2){
    var temp = $(thing1).html()
    $(thing1).html( $(thing2).html());
    $(thing2).html(temp);
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

