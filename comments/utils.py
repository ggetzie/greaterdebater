from django.http import HttpResponse
from django.template import loader, Context

from tcd.comments.models import TopicComment

def build_list(comments, p_id):
    """Takes a query set of comments and a parent id and
    returns a list of comments sorted in the appropriate parent-child
    order such that first comment = first toplevel comment, second commend = first
    child of first comment, third comment = first child of second comment or second 
    child of first comment and so on"""
    comment_list = []
    for comment in comments.filter(nparent_id=p_id):
        children = comments.filter(nparent_id=comment.id)
        if not children:
            comment_list.append(comment)
        else:
            comment_list.append(comment)
            comment_list.extend(build_list(comments, comment.id))
    return comment_list

