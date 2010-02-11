BEGIN;

ALTER TABLE profiles_profile ADD `feedcoms` bool NOT NULL default false;
ALTER TABLE profiles_profile ADD `feedtops` bool NOT NULL default false;
ALTER TABLE profiles_profile ADD `feeddebs` bool NOT NULL default false;

COMMIT;



    
    