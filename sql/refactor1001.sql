BEGIN;

ALTER TABLE comments_comment DROP COLUMN is_removed;
ALTER TABLE comments_comment DROP COLUMN is_first;
ALTER TABLE comments_comment DROP COLUMN parent_id;
ALTER TABLE comments_comment DROP COLUMN nesting;
ALTER TABLE comments_comment DROP COLUMN arguments;
ALTER TABLE comments_comment DROP COLUMN arg_proper;

DROP TABLE items_argument;
DROP TABLE items_vote;
DROP TABLE comments_comment_arguments;

ALTER TABLE auth_group ENGINE = InnoDB;
ALTER TABLE auth_group_permissions ENGINE = InnoDB;
ALTER TABLE auth_message ENGINE = InnoDB;
ALTER TABLE auth_permission ENGINE = InnoDB;
ALTER TABLE auth_user ENGINE = InnoDB;
ALTER TABLE auth_user_groups ENGINE = InnoDB;
ALTER TABLE auth_user_user_permissions ENGINE = InnoDB;
ALTER TABLE comments_argcomment ENGINE = InnoDB;
ALTER TABLE comments_comment ENGINE = InnoDB;
ALTER TABLE comments_comment_cflaggers ENGINE = InnoDB;
ALTER TABLE comments_debate ENGINE = InnoDB;
ALTER TABLE comments_draw ENGINE = InnoDB;
ALTER TABLE comments_nvote ENGINE = InnoDB;
ALTER TABLE comments_tcdmessage ENGINE = InnoDB;
ALTER TABLE comments_topiccomment ENGINE = InnoDB;
ALTER TABLE django_admin_log ENGINE = InnoDB;
ALTER TABLE django_content_type ENGINE = InnoDB;
ALTER TABLE django_session ENGINE = InnoDB;
ALTER TABLE django_site ENGINE = InnoDB;
ALTER TABLE items_logitem ENGINE = InnoDB;
ALTER TABLE items_tags ENGINE = InnoDB;
ALTER TABLE items_topic ENGINE = InnoDB;
ALTER TABLE items_topic_tflaggers ENGINE = InnoDB;
ALTER TABLE profiles_forgotten ENGINE = InnoDB;
ALTER TABLE profiles_profile ENGINE = InnoDB;

COMMIT;
