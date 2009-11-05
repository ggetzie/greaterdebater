BEGIN;

ALTER TABLE profiles_profile ADD usertags longtext NOT NULL;

COMMIT;
