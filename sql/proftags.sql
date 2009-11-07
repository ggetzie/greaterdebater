BEGIN;

ALTER TABLE profiles_profile ADD tags longtext NOT NULL;

COMMIT;
