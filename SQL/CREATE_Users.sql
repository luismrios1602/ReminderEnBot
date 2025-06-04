CREATE TABLE `reminden`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `chat_id` BIGINT NOT NULL,
  `name` VARCHAR(200) NULL,
  `lang` VARCHAR(3) NOT NULL,
  PRIMARY KEY (`id`));