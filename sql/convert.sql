BEGIN;



ALTER TABLE auth_group CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE auth_group_permissions CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  auth_message CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  auth_permission CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  auth_user CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  auth_user_groups CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  auth_user_user_permissions CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  blog_blog CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  blog_post CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  blog_postcomment CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_argcomment CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_comment CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_comment_cflaggers CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_debate CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_draw CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_fcommessage CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_nvote CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_tcdmessage CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_topiccomment CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  comments_topiccomment_followers CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  django_admin_log CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  django_content_type CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  django_session CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  django_site CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  items_logitem CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  items_tags CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  items_topic CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  items_topic_followers CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  items_topic_tflaggers CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  profiles_forgotten CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE  profiles_profile CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;

COMMIT;