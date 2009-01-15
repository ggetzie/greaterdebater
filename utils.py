from tcd.comments.models import Comment
import random
import types

def build_list(comments, p_id):
    """Takes a query set of comments and a parent id and
    returns a list of comments sorted in the appropriate parent-child
    order such that first comment = first toplevel comment, second commend = first
    child of first comment, third comment = first child of second comment or second 
    child of first comment and so on"""
    comment_list = []
    for comment in comments.filter(parent_id=p_id):
        children = comments.filter(parent_id=comment.id)
        if not children:
            comment_list.append(comment)
        else:
            comment_list.append(comment)
            comment_list.extend(build_list(comments, comment.id))
    return comment_list


def random_string(length):
    """Returns an alphanumeric string of random characters with the given length"""
    alphanumeric = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(alphanumeric) for x in range(length)])

def calc_start(page, paginate_by, count):
    """Calculate the first number in a section of a list of objects to be displayed as a numbered list"""
    if page is not None:
        if page == 'last':
            return paginate_by * (count / paginate_by) + 1
        else:
            return paginate_by * (int(page) - 1) + 1                
    else:
        return 1








    
        
                            

