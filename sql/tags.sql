BEGIN;

CREATE TABLE `items_tags` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `topic_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `tags` longtext NOT NULL
)
;
ALTER TABLE `items_tags` ADD CONSTRAINT `user_id_refs_id_40bd0e46` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `items_tags` ADD CONSTRAINT `topic_id_refs_id_75be2838` FOREIGN KEY (`topic_id`) REFERENCES `items_topic` (`id`);

ALTER TABLE items_topic ADD tags longtext NOT NULL;
ALTER TABLE items_topic ADD display_tags longtext NOT NULL;

COMMIT;
