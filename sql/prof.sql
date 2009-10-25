BEGIN;

ALTER TABLE profiles_profile ADD newwin boolean NOT NULL;
ALTER TABLE profiles_profile ADD mailok boolean NOT NULL;

COMMIT;
