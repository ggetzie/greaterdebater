BEGIN;

CREATE TABLE `comments_topiccomment_followers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `topiccomment_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`topiccomment_id`, `user_id`)
)
;
ALTER TABLE `comments_topiccomment_followers` ADD CONSTRAINT `user_id_refs_id_328ff9ce` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

CREATE TABLE `items_topic_followers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `topic_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`topic_id`, `user_id`)
)
;
ALTER TABLE `items_topic_followers` ADD CONSTRAINT `user_id_refs_id_587a132b` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

ALTER TABLE profiles_profile ADD followtops BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE profiles_profile ADD followcoms BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT;
