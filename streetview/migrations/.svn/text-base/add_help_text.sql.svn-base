DROP TABLE `ratestreets_itemhelptext`;
CREATE TABLE `ratestreets_itemhelptext` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `item_id` integer NOT NULL,
    `text` varchar(4096) NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL
)
;
ALTER TABLE `ratestreets_itemhelptext` ADD CONSTRAINT `item_id_refs_id_fce540a9` FOREIGN KEY (`item_id`) REFERENCES `ratestreets_item` (`id`);
CREATE INDEX `ratestreets_itemhelptext_67b70d25` ON `ratestreets_itemhelptext` (`item_id`);
