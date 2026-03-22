CREATE TABLE `mati_go_2_menetrend` (
  `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `used_id` smallint NULL,
  `datum` date NOT NULL,
  `idopont` time NOT NULL,
  `jarat` varchar(10) NOT NULL,
  `irany` varchar(100) NOT NULL,
  `megallo` varchar(100) NOT NULL
);




The server docker image is created by  docker-compose
