BEGIN;
ALTER TABLE `ratestreets_booleanrating` ADD COLUMN `image_date` date;
ALTER TABLE `ratestreets_categoryrating` ADD COLUMN `image_date` date;
ALTER TABLE `ratestreets_countrating` ADD COLUMN `image_date` date;
ALTER TABLE `ratestreets_freeformrating` ADD COLUMN `image_date` date;
COMMIT;