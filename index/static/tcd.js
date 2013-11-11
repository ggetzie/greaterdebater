$(document).ready(function() {
    
    $('#check_all').change(function () {
    	$('.message').attr('checked', $('#check_all').attr('checked'));
    });

    $('.jsddm > li').bind('mouseover', jsddm_open);
    $('.jsddm > li').bind('mouseout',  jsddm_timer)
    
});

document.onclick = jsddm_close;

// enable csrf protection for ajax POSTs
$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});
    
function displayFormComment(form_id) {

    $(form_id).parents("div.action_block").find("div.comment_action").
    not(form_id).each(function() {
	$(this).hide();
    });

    $(form_id).slideToggle();
}		


function check_messages() {
    $("#msgcount").html("Checking for messages...")
    var add = "/users/check_messages/"
    if (window.location.origin.indexOf("greaterdebater") != -1) {
	add = "https://greaterdebater.com/users/check_messages"
    }
    $.get(add,
	  function(xml) {
	      $("#user_msgs").append($("message", xml).html())
	  });
}

function mark_read(id) {
    $("#reply"+id).removeAttr("onmouseout");
    $.post("/users/mark_read/", {'id': id},
	   function(xml) {
	       if ($("status", xml).text() == "error") {
		   $("div.unread_msg").removeAttr("onmouseout");
		   alert($('message',xml).text());

	       } else {
		   $("#reply"+id).removeClass("unread_msg");
		   count = $('message', xml).next().text()
		   if (count == "0") {
		       $("#replycount").removeClass("unread_msg");
		   }
		   if (count == "1") {
		       suffix = "y"
		   } else {
		       suffix = "ies"
		   }
		   $("#replycount").html(count + " new repl" + suffix);
	       }
	       
	   })
}
	  		   

function follow(id, item) {
    var fol = $("#f"+item+id).parent()
    var folhtml = fol.html()
    fol.html("Loading...")
    
    $.post('/comments/follow/', {'item': item,
				 'id': id},
	   function(xml) {
	       message = $('message', xml).text()
	       if ($("status", xml).text() == "alert") {
		   alert($('message', xml).text());
	       } else if ($("status", xml).text() == "error") {
		   fol.html(folhtml)
		   $("#f"+item+id).after($('message', xml).html());
	       } else {
		   fol.html(folhtml)
		   if (message == "off") {
		       $("#f"+item+id).html("follow")
		   } else if (message == "on") {
		       $("#f"+item+id).html("unfollow")
		   }
	       }
	       
	   })
}		  

function vote(argument, voted_for){
    var votediv = $("#vote").html();
    $("#vote").html("Loading...");
    
    $.post("/argue/vote/", {argument: argument,
			    voted_for: voted_for},
	   function(xml) {
	       var pvotefor
	       var dvotefor

	       if ($("status",xml).text() == "alert"){
		   
		   $("vote").html(votediv);
		   alert($('message', xml).text());

	       } else {
		   window.location.reload();
	       }
	   });
};



function unvote(argument, voter) {
    var votediv =  $("#vote").html();
    $("#vote").html("Loading...");
    $.post("/argue/unvote/", {argument: argument,
			      voter:voter},
	   function(xml) {
	       if ($("error", xml).text() == "True") {		   
		   $("#vote").html(votediv);
		   $("#vote").after( $("message", xml).text() );
	       } else {
		   window.location.reload();
	       }});
}

function delete_comment(id) {
    var menuid = "#comment-menu" + id
    var menu = $(menuid).html();
    $(menuid).html("Loading...");
    $.post("/comments/delete/", {comment_id: id},	   
	   function(xml) { 
	       $(menuid).html(menu);
	       comID = $("message",xml).next().text()
	       divID = '#comment_div' + comID
	       if($("status",xml).text() == "error") {
		   msg=$("message",xml).html()
		   $('#comment_div' + comID).after(msg)
	       } else if ( $("status", xml).text() == "alert") {
		   alert($('message', xml).text());
	       } else {
		   $(divID).html($("message",xml).html())
	       }

	   }
	  );	       
};

function delete_topic(id) {
    var topic_menu = $("#delete_link" + id).parent();
    var tinside = topic_menu.html();
    topic_menu.html("Loading...");
    
    $.post("/topics/delete/", {topic_id: id},	   
	   function(xml) { 	 
	       topic_menu.html(tinside);
	       if ($("status", xml).text() == "alert") {
		   alert($("message",xml).text());
	       } else {
		   divID = '#topic_div' + id;	       
		   msg=$("message",xml).html()
		   $(divID).after(msg)
		   if ($("status",xml).text() == "ok") {
		       $(divID).remove()
		   }
	       }
	   }
	  );	       
};

function showalltags(topic_id, add) {
    ft = '#fulltags' + topic_id;
    mt = '#moretags' + topic_id;
    if ($(ft).css('display') == 'none') {
	$(mt).html("hide...");
    } else {
	if (add) {
	    $(mt).html("Add Tags...");
	} else {
	    $(mt).html("more...");
	}
    }
    $(ft).toggle();
}

function clicktag(topic_id, tag, main) {
    tag_text = "#tag_text" + topic_id
    ft = '#fulltags' + topic_id
    mt = '#moretags' + topic_id
    tagval = $(tag_text).val()
    if (main) {
	$(ft).show()
	$(mt).html("hide...")
    }

    if (tagval == '') {
	$(tag_text).val(tag)
    } else {
	$(tag_text).val(tagval + ", " + tag)
    }
}

function addtags(topic_id, source) {
    tagdiv = "#tags" + topic_id
    tags = $("#tag_text" + topic_id).val()
    var oldtags = $(tagdiv).html()
    $(tagdiv).html("Loading...")
    $.post("/topics/addtags/", {topic_id: topic_id,
				source: source,
				tags: tags},
	   function(xml) {
	       if ($("status", xml).text() == "error") {		   
		   $(tagdiv).html(oldtags);
		   $(tagdiv).before($("message", xml).html());
		
	       } else {
		   $(tagdiv).html($("message", xml).html());
	       }
	   });
}

function remove_tag(topic_id, user_id, tag) {
    $.post("/topics/removetag/", {topic_id: topic_id,
				  user_id: user_id,
				  tag: tag},
	   function(xml) {
	       if ($("status", xml).text() == "ok") {
		   $("li:contains(" + tag + ")").html($("message", xml).html());
		   
	       } else {
		   $("h3.prof-head").after($("message", xml).html())
	       }
	   });
}

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
	       if ($("status",xml).text() == 'alert') {
		   alert( $("message",xml).text());
	       } else {
		   msg = $("message",xml).html();
		   $("#comment_div" + comment_id).after(msg);
	       }
	   }
	  )
}

function respond_draw(arg_id, user_id, response) {
    var turn_actions = $("#turn_actions").html();
    $("#turn_actions").html("Loading...");
    
    $.post("/argue/draw/respond/", {arg_id: arg_id,
				    user_id: user_id,
				    response: response},
	   function(xml) {
	       // display the message
	       msg = $("message", xml).html();
	       $("#turn_actions").html(turn_actions);
	       $("#arg_actions").parent().append(msg);
	       arg_status = $("message", xml).slice(2).text();
	       if ( $("status", xml).text() == "ok") {
		   if ( arg_status == 'draw') {
		       // if the draw was accepted
		       // change the status and remove the options to reply
		       $("#arg_actions").remove();
		       $("#arg_status").html( arg_status );
		   } else {
		       // if the draw was declined, show the options to reply
		       $("#draw_query").remove();
		       turn_actions = $("message", xml).slice(1).html()
		       $("#arg_actions").replaceWith(turn_actions);
		   }
	       }

	   }
	  )
}

function respond_challenge(arg_id, user_id, response) {
    
    var arg_responses = $("#arg_responses").html();
    $("#arg_responses").html("Loading...");
    $.post("/argue/respond/", {arg_id: arg_id,
			       user_id: user_id,
			       response: response},
	   function(xml) {
	       // display the message
	       if ( $("status", xml).text() == "ok") {
		   msg = $("message", xml).html()
		   turn_actions = $('message', xml).slice(1).html()
		   arg_response = $('message', xml).slice(2).html()
		   arg_status = $('message', xml).slice(3).html()
		   if ( arg_response == "accept") {
		       // if the challenge was accepted
		       // change the status and add the options to reply
		       $("#arg_actions").replaceWith(turn_actions);
		   } else {
		       // if the challenge was declined, remove the arg_actions div
		       $("#arg_actions").remove();
		   }
		   $("#arg_comments").append(msg);
		   // In any case, update the status of the argument
		   $("#arg_status").html( arg_status);
	       } else if ($("status", xml).text() == "error") {
		   // Display the error message
		   $("#arg_responses").html(arg_responses);
		   msg = $("message", xml).text();
		   $("#arg_actions").append(msg);
	       } else {
		   alert("Invalid Status!");
	       }
	   }
	  )
	   
}

function concede_argument(arg_id, user_id) {
    var turn_actions = $("#turn_actions").html()
    $("#turn_actions").html("Loading...")
    $.post("/argue/concede/", {arg_id: arg_id,
			      user_id: user_id},
	   function(xml) {
	       
	       msg = $("message", xml).html();
	       if ( $("status", xml).text() == "error") {
		   $("#turn_actions").html(turn_actions);
		   $("#turn_actions").append(msg);
	       } else {
		   $("#arg_status").html( $("message", xml).next().html() );
		   $("#arg_actions").parent().append(msg);
		   $("#arg_actions").remove()
	       }
	   }
	  )
    $("#concede" + arg_id).hide();
}

function rebut_argument(arg_id, parent_id, draw) {    
    var comment_text
    if (draw == true) {
	url = "/argue/draw/"
	comment_text = $("#draw_text").val();
    } else {
	url = "/argue/rebut/"
	comment_text = $("#rebut_text").val();
    }

    var turn_actions = $("#turn_actions").html()
    $("#turn_actions").html("Loading...")

    $.post(url, {comment: comment_text,
		 parent_id: parent_id,
		 arg_id: arg_id},
	   function(xml) {
	       $("#turn_actions").html(turn_actions)
	       status = $("status", xml).text();
	       if (status == "error") {
		   // show the error message somewhere
		   $("#turn_actions").append(msg);
		   msg = $("message", xml).text();
	       } else {
		   // add the rebuttal comment at the end of the list of comments
		   msg = $("message", xml).html();
		   $("#arg_comments").append(msg);
		   // update the status field
		   astatus = $("message", xml).next().text()
		   $("#arg_status").html( astatus);
		   $("#arg_actions").remove()
	       }
	   })
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
    var cmd_row = $("#cmd_row").html();
    $("#cmd_row").html("Loading...");

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
    $("#cmd_row").html(cmd_row);
}

function delete_current_message(m_id){
    $("#delete").html("Loading...")
    $.post('/users/delete_current_message/', {message_id: m_id},
	   function(url) {
	       window.location.href=url
	   }
	       
	   )
}


// Javascript for dropdown menu adapted from
// http://javascript-array.com/scripts/jquery_simple_drop_down_menu/
var timeout    = 500;
var closetimer = 0;
var ddmenuitem = 0;

function jsddm_open()
{  jsddm_canceltimer();
   jsddm_close();
   ddmenuitem = $(this).find('ul').css('visibility', 'visible');}

function jsddm_close()
{  if(ddmenuitem) ddmenuitem.css('visibility', 'hidden');}

function jsddm_timer()
{  closetimer = window.setTimeout(jsddm_close, timeout);}

function jsddm_canceltimer()
{  if(closetimer)
   {  window.clearTimeout(closetimer);
      closetimer = null;}}
