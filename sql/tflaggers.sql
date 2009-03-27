BEGIN;
CREATE TABLE `items_topic_tflaggers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `topic_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`topic_id`, `user_id`)
)
;
ALTER TABLE `items_topic_tflaggers` ADD CONSTRAINT `topic_id_refs_id_481f079` FOREIGN KEY (`topic_id`) REFERENCES `items_topic` (`id`);
ALTER TABLE `items_topic_tflaggers` ADD CONSTRAINT `user_id_refs_id_3a495b49` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE items_topic ADD needs_review bool NOT NULL;
COMMIT;