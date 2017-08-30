BEGIN;
CREATE TABLE `ratestreets_kappastat` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `kappa` double precision,
    `timestamp` datetime NOT NULL,
    `study_id` integer NOT NULL,
    `item_id` integer NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL
)
;
ALTER TABLE `ratestreets_kappastat` ADD CONSTRAINT `study_id_refs_id_e637cd5f` FOREIGN KEY (`study_id`) REFERENCES `ratestreets_study` (`id`);
ALTER TABLE `ratestreets_kappastat` ADD CONSTRAINT `item_id_refs_id_67365eba` FOREIGN KEY (`item_id`) REFERENCES `ratestreets_item` (`id`);
CREATE INDEX `ratestreets_kappastat_da5fc7d6` ON `ratestreets_kappastat` (`study_id`);
CREATE INDEX `ratestreets_kappastat_67b70d25` ON `ratestreets_kappastat` (`item_id`);COMMIT;
