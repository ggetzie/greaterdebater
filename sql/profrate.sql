BEGIN;

ALTER TABLE profiles_profile ADD last_post datetime NOT NULL;
ALTER TABLE profiles_profile ADD rate smallint UNSIGNED NOT NULL;

COMMIT;
