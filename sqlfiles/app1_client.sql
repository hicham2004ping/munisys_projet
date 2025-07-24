-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mer. 23 juil. 2025 à 20:20
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
-- Structure de la table `app1_client`
--

CREATE TABLE `app1_client` (
  `id` bigint(20) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `telephone` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `app1_client`
--

INSERT INTO `app1_client` (`id`, `nom`, `email`, `telephone`) VALUES
(2, 'qacem', 'souleimani@gmail.com', '12238383'),
(3, 'testuser', 'test@gmail.com', '12238383'),
(4, 'lebonon', 'hassan@gmail.com', '12238383'),
(5, 'mynisys', 'munisys@gmail.com', '12238383'),
(6, 'gaza', 'gaza@gmail.com', '12238383'),
(7, 'sayed', 'beirut@gmail.com', '12238383'),
(8, 'ramadan', 'ramadan@gmail.com', '12238383'),
(9, 'hicham', 'hichamm@gmail.com', '12238383'),
(10, 'ismail', 'haniyah@gmail.com', '12238383');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `app1_client`
--
ALTER TABLE `app1_client`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `app1_client`
--
ALTER TABLE `app1_client`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
