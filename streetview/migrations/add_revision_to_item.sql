BEGIN;
ALTER TABLE `ratestreets_item` ADD COLUMN `revision` varchar(32);
UPDATE `ratestreets_item` SET revision="test";
COMMIT;
