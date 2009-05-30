$(document).ready(function() {
    
    $('#check_all').change(function () {
    	$('.message').attr('checked', $('#check_all').attr('checked'));
    });

});
    
function displayFormComment(form_id) {

    $(form_id).parents("div.action_block").find("div.comment_action").
    not(form_id).each(function() {
	$(this).hide();
    });

    $(form_id).slideToggle();
}		

function vote(argument, voter, voted_for){
    $.post("/vote/", {argument: argument,
		      voter: voter,
		      voted_for: voted_for},
	   function(xml) {
	       addVotes(xml);
	   });
};

function addVotes(xml) {
    var pvotefor
    var dvotefor

    if ($("error",xml).text() == "True"){

	$("#sys_messages").html( $("message",xml).text());

    } else {

	$("#vote").html( $("message",xml).text());
    }
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

function concede_argument(arg_id, user_id) {
    $.post("/argue/concede/", {arg_id: arg_id,
			      user_id: user_id},
	   function(xml) {
	       msg = $("message", xml).text();
	       $("#turn_actions").append(msg);
	   }
	  )
    $("#concede" + arg_id).hide();
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

function delete_checked_messages() {
    var checked_messages = [];
    
    $('.message').each( function(i) {
	if ($(this).attr('checked')) {
	    checked_messages.push($(this).attr('value'))}})
    
    if (checked_messages.length == 0) {
	$('#sys_messages').html("No messages selected"); 
    } else {    
	$.post('/users/delete_messages/', {message_list: checked_messages.toString()},
	       function(xml){
		   jQuery.each(checked_messages, function() {
		       $('#message_row' + this).remove()
		   })
		   $('#sys_messages').html($("message",xml))
	       })
    }
}
