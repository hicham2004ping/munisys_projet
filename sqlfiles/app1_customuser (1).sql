-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mer. 23 juil. 2025 à 20:19
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `gestion_inventaire`
--

-- --------------------------------------------------------

--
-- Structure de la table `app1_customuser`
--

CREATE TABLE `app1_customuser` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `app1_customuser`
--

INSERT INTO `app1_customuser` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`) VALUES
(1, 'pbkdf2_sha256$600000$hwPSJ69JyeIoELAfLV0j3G$2AQWOA0SAb7f0mD9FMT2T10rvvdupW5ThRTl81pAMLA=', '2025-07-23 15:14:04.690156', 1, 'hicham', 'nascerallah', 'souleimani', 'ilyasmoulragouba@gmail.com', 1, 1, '2025-07-04 15:14:29.793600', ''),
(7, 'pbkdf2_sha256$600000$IUe2YFmP2lX0CULN4j9tfW$yq95LPyt4jUjo0IKuddMqsXffpNCtEB/Do6iuNOpRQ0=', '2025-07-05 17:29:38.334583', 0, 'testuser', 'ibrahim', 'akil', 'hicham@gmail.com', 0, 1, '2025-07-04 17:06:10.348899', ''),
(14, 'pbkdf2_sha256$600000$JmwIpteq6EIIjE5WbyZFdP$cXApub0PNhOovpzcO11jI0xtoJzeVx1Lg+7dJJEAJmw=', NULL, 0, 'Ragouba__lef9ih', 'ilyas', 'moul', 'ilyas.moulragouba@uir.ac.ma', 0, 1, '2025-07-05 17:15:26.103950', ''),
(19, 'pbkdf2_sha256$720000$ljADrwmQkIStsK9CRLU452$/ZnNkZ2EBRbdbldhMXEZ2G6Iv5kjSVUB/fRauA/awts=', '2025-07-23 18:02:04.347222', 0, 'nascerallah@gmail.com', 'nascerallah', 'hassan', 'nascerallah@gmail.com', 0, 1, '2025-07-07 21:54:02.146702', 'commercial'),
(20, 'pbkdf2_sha256$600000$0vplUFZuRlPfF2QuP0BWip$x4+eX1zPQbX0SjAGKfE+hofElrgDPB44wzYmZwwLyyE=', '2025-07-12 01:22:40.243126', 0, 'souleimani@gmail.com', 'qacem', 'souleimani', 'souleimani@gmail.com', 0, 1, '2025-07-07 22:16:03.653281', ''),
(21, 'pbkdf2_sha256$600000$tGrsj6lbrmRrWH2yDo9jBZ$G+OuxL4C3xjrGKq2WAbfO9VPVZy5564pqVVJFkL8boU=', '2025-07-08 21:46:43.120629', 0, 'test@gmail.com', 'testuser', 'test', 'test@gmail.com', 0, 1, '2025-07-08 21:46:30.640424', ''),
(22, 'pbkdf2_sha256$600000$0UuKd2Mld5Q04VEzSZUZYH$q/G6GjuO2NnD0WQ55eATvIT03A8jjB5aEwubj3EHYmU=', '2025-07-13 14:59:58.279787', 0, 'hassan@gmail.com', 'lebonon', 'on', 'hezbollah@gmail.com', 0, 1, '2025-07-09 00:39:57.673874', 'client'),
(25, 'pbkdf2_sha256$600000$L6miFfJBpHuoj9eFZfEqSZ$Sq3U6klI8kF4EVdt+LVAKikWCJfhRL05pswaP3RHF9I=', '2025-07-18 18:30:03.236549', 0, 'ali_karaki', 'ali', 'karaki', 'ali@gmail.com', 0, 1, '2025-07-11 22:58:46.723260', 'technicien'),
(26, 'pbkdf2_sha256$720000$CR98LhasWUzpmByZtqGyP9$O6Ry+uYO09j8t8En0LcWyJmnoA/Cbfrt5Xv1DIqGea4=', '2025-07-23 18:05:02.490541', 0, 'sayed_mohsiin', 'fouad', 'chokr', 'technicien@gmail.com', 0, 1, '2025-07-13 02:00:46.869100', 'technicien'),
(27, 'pbkdf2_sha256$600000$7fzzdFewk5ag8TtAWwuadr$WE1cIz1d02zTh3MZGN2XXLlD2Hi/nEwYYDhHv369/uU=', '2025-07-18 15:22:23.048556', 0, 'samedi', 'samedi', 'dimanche', 'samedi@gmail.com', 0, 1, '2025-07-13 02:09:04.982391', 'technicien'),
(28, 'pbkdf2_sha256$600000$MoXClLgj4Tno1xUg2zKKHt$9+W7PCVtKUdzy70spJNA/Z9Jqok4Q6ZJikmkrKdnzVo=', '2025-07-23 18:18:33.137459', 0, 'munisys@gmail.com', 'mynisys', 'societe', 'munisys@gmail.com', 0, 1, '2025-07-13 15:06:45.323549', 'client'),
(29, 'pbkdf2_sha256$600000$K6fzbdSF6tP9zALruHMzc2$USqEP5q+u71X7DMdg81Yvg0rJSipcvEiHhJ/ptKtHXM=', '2025-07-17 01:54:33.691976', 0, 'gaza@gmail.com', 'gaza', 'palestine', 'gaza@gmail.com', 0, 1, '2025-07-13 15:12:43.186604', 'client'),
(30, 'pbkdf2_sha256$600000$EDw5mAPAkYt4c1kXBTEX0M$mIKa0IpD8aktErb2gveMde69g+fwuj6djh7zCplZGeo=', '2025-07-13 20:19:13.251475', 0, 'beirut@gmail.com', 'sayed', '', 'beirut@gmail.com', 0, 1, '2025-07-13 20:19:07.028863', 'client'),
(31, 'pbkdf2_sha256$600000$XZrnbxO8dWVDXqEPVPf0If$TuE+SPOM7av658uakOD4HCSGnbiOQkRQfJ4E8HsGmJQ=', '2025-07-21 13:35:09.800360', 0, 'fedex', 'fed', 'ex', 'fedex@gmail.com', 0, 1, '2025-07-16 15:19:16.494007', 'coursier'),
(32, 'pbkdf2_sha256$600000$cNBJv8xOfUKz8LAa9uWU6O$r+7R/MC8tOzKN2YUuL42oxkYgW1+EtQmrdmWcnvldqw=', '2025-07-18 15:23:00.083394', 0, 'ramadan@gmail.com', 'ramadan', '', 'ramadan@gmail.com', 0, 1, '2025-07-18 15:12:17.345941', 'client'),
(34, 'pbkdf2_sha256$600000$D9VHwbAmp61DPOMptB5KhV$O9cXT4GnayetOltRMt7vamKm0cgtklvQ0zFpuuOGoU8=', '2025-07-18 15:56:13.435392', 0, 'hichamm@gmail.com', 'hicham', '', 'hichamm@gmail.com', 0, 1, '2025-07-18 15:56:06.100193', 'client'),
(35, 'pbkdf2_sha256$600000$9ltPHvifcdBgs6UE3dTw3M$XUQrNM543ZfgVtaE1ZyeHI3NSBTdFsSvmPc3KArVEUc=', '2025-07-18 18:35:56.802316', 0, 'haniyah@gmail.com', 'ismail', '', 'haniyah@gmail.com', 0, 1, '2025-07-18 18:35:51.335746', 'client');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `app1_customuser`
--
ALTER TABLE `app1_customuser`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `app1_customuser`
--
ALTER TABLE `app1_customuser`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
