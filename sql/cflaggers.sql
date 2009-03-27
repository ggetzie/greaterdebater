
BEGIN;
CREATE TABLE `comments_comment_cflaggers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `comment_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`comment_id`, `user_id`)
)
;
ALTER TABLE `comments_comment_cflaggers` ADD CONSTRAINT `comment_id_refs_id_4e1c4df0` FOREIGN KEY (`comment_id`) REFERENCES `comments_comment` (`id`);
ALTER TABLE `comments_comment_cflaggers` ADD CONSTRAINT `user_id_refs_id_1ab795ab` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

ALTER TABLE comments_comment ADD needs_review bool NOT NULL;

COMMIT;
