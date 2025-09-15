CREATE TABLE `words` (
  `id` int NOT NULL AUTO_INCREMENT,
  `word` varchar(200) NOT NULL,
  `lang_word` char(2) DEFAULT NULL,
  `meaning` varchar(200) NOT NULL,
  `lang_meaning` char(2) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `examples` varchar(1000) DEFAULT NULL,
  `chat_id` bigint NOT NULL,
  `days_schedule` int NOT NULL DEFAULT '7' COMMENT 'Cantidad de dias para reprogramar una palabra',
  `scheduled` datetime NOT NULL DEFAULT '1900-01-01 00:00:00',
  `remind` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci