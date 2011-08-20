BEGIN;

ALTER TABLE profiles_profile ADD `shadowban` bool NOT NULL default false;

COMMIT;



    
    