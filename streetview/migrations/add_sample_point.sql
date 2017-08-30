BEGIN;
CREATE TABLE `ratestreets_samplepoint` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `study_id` integer NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `row_id` integer NOT NULL,
    `lat` double precision,
    `lng` double precision,
    `street_address` varchar(256)
)
;
ALTER TABLE `ratestreets_samplepoint` ADD CONSTRAINT `study_id_refs_id_3395776c` FOREIGN KEY (`study_id`) REFERENCES `ratestreets_study` (`id`);
ALTER TABLE `ratestreets_segment` ADD COLUMN `sample_point_id` integer; 
ALTER TABLE `ratestreets_segment` ADD CONSTRAINT `sample_point_id_refs_id_8af512dc` FOREIGN KEY (`sample_point_id`) REFERENCES `ratestreets_samplepoint` (`id`);
COMMIT;
