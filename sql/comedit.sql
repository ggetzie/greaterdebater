BEGIN;

ALTER TABLE comments_comment ADD last_edit datetime;

COMMIT;
