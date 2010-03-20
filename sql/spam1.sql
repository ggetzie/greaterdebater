BEGIN;

ALTER TABLE profiles_profile ADD `probation` bool NOT NULL default true;
ALTER TABLE comments_comment ADD `spam` bool NOT NULL default false;
ALTER TABLE items_topic ADD `spam` bool NOT NULL default false;

COMMIT;



    
    