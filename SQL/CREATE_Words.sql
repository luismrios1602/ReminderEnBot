CREATE TABLE `words` (
  `id` int NOT NULL AUTO_INCREMENT,
  `word` varchar(200) NOT NULL,
  `meaning` varchar(200) NOT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `examples` varchar(1000) NOT NULL,
  `chat_id` bigint NOT NULL,
  `scheduled` datetime NOT NULL DEFAULT '1900-01-01 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci