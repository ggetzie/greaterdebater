README COMMENTS
-----------------------------------
Last revision : Tue Sep 25 14:05:51 CEST 2007
Author : Benoit Chesneau <bchesneau at gmail dot com>


*) About
------------------------------------

Comments is a django application used on Friendsnippets (http://www.friendsnippets.com) to let members to add their comments to snippets. 

It works with current django-trunk (revision 6423 and above) and use Newsforms.

Current Features :
 - Let users post a comment when they are authenticated
 - markdown support
 - code embeded in comments is also supported : 
   http://friendsnippets.com/help/comments/

It's inspired by django freecomments :
http://code.djangoproject.com/browser/django/trunk/django/contrib/comments


*) License :
------------------------------------

Copyright (c) 2007 Benoit Chesneau <benoitc at metavers dot net>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.



*) Requirements :
------------------------------------
- Pygments : You need to install pygments in PYTHON_PATH. Pygmets will allow insertion of code in comments. To download pygments go on their website :
http://pygments.org/

- Markdown : http://www.freewisdom.org/projects/python-markdown/


*) Installation :
------------------------------------
- Download comments
svn checkout http://friendsnippets.googlecode.com/svn/trunk/django/comments 

- put comments in your django application and add it to INSTALLED_APPS.


*) How to add comments to my applications ?
------------------------------------

In 0.1 it's easy to add comments to an application :

load comments_tags :
{% load comments_tags %}

Netx add this tags to add posting form. For now only authenticated users can post :

{% if user.is_authenticated %}
{% comment_form for app.Model model.id redirect_to path %}
{% include "comments/form.html" %}
{% else %}
{% trans "In order to post a comment, you should have a friendsnippet account. Please" %} <a href="/signin">{% trans "sign-in" %}</a>.
{% endif %}

To view comments for an item :
{% show_comments for app.Model model.id %}
{% include "comments/comments.html" %}


Replace app.Mode by the name of app and model you want. model.id could be a context template variable or a value.

Replace path by path of the page you want to redirect users after posting a comment

In settings.py you could set 2 vars :


try:
COMMENT_REDIRECT_TO :  to set default redirect url . 

COMMENTS_SIGNIN_VIEW : to set signin view. It will be used to redirect non authenticated users.




TODO :
- Add support for unauthenticated users.

