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
-- Structure de la table `app1_materiel`
--

CREATE TABLE `app1_materiel` (
  `id` bigint(20) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `refference` varchar(100) NOT NULL,
  `quantite_stock` int(11) NOT NULL,
  `categorie_id` bigint(20) NOT NULL,
  `min_quantite` int(11) NOT NULL,
  `prix` int(11) NOT NULL,
  `image` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `app1_materiel`
--

INSERT INTO `app1_materiel` (`id`, `nom`, `refference`, `quantite_stock`, `categorie_id`, `min_quantite`, `prix`, `image`) VALUES
(1, 'Lenovo ThinkPad', 'LTP123', 25, 1, 10, 200, 'materiels/istockphoto-458405389-612x612_8VWEwVV.jpg'),
(2, 'HP LaserJet 1020', 'HP1020', 0, 2, 10, 200, 'materiels/HP_LaserJet_1020_printer.jpg'),
(5, 'Clavier Logitech', 'LOG123', 13, 5, 10, 200, 'materiels/logitech-clavier-gaming-g213-prodigy-pcgamercasa-maroc.jpg'),
(6, 'Dell PowerEdge R740', 'DELL-R740', 18, 1, 2, 4000, 'materiels/image.jpg'),
(7, 'Lenovo ThinkCentre M920', 'LENO-M920', -2, 1, 5, 1000, 'materiels/thinkcenter.jpg'),
(8, 'Brother HL-L8360CDW', 'BRO-HL8360', 9, 2, 1, 600, 'materiels/hp.jpg'),
(9, 'Epson WorkForce WF-7840', 'EPS-WF7840', 20, 2, 2, 500, 'materiels/design-medium.jpg'),
(10, 'Rack 42U pour serveurs', 'RACK-42U', 18, 3, 4, 900, 'materiels/BAIE42U.jpg.jpg'),
(11, 'Armoire réseau murale 12U', 'RACK-12U', 1, 3, 3, 350, 'materiels/wk01200-01-thumbnail-540x540-70.jpg'),
(12, 'Cisco IP Phone 8845', 'CISCO-8845', 12, 4, 5, 250, 'materiels/ip_phone.jpg'),
(13, 'Grandstream GXP2170', 'GXP-2170', 6, 4, 3, 190, 'materiels/ip_sans_fil.jpg'),
(14, 'Clavier mécanique Logitech', 'LOG-MECH-KB', 15, 5, 10, 90, 'materiels/61PxD8xH9ML._AC_SL1024_.jpg'),
(15, 'Switch Netgear 24 ports', 'NET-SW24P', 9, 5, 4, 600, 'materiels/M4300-28G-PoE-plus-1000W-PSU_productcarousel_hero_image_tcm169-97107.jpg'),
(16, 'Routeur Cisco ISR 4331', 'CISCO-R4331', 4, 5, 1, 1500, 'materiels/cisco.jpg'),
(17, 'Onduleur APC Smart-UPS', 'APC-SMT1500', 20, 5, 3, 850, 'materiels/626044D396BDC9B385257C8A00521EE5_LEAN_9GNKMH_fr_h_hi_1500.jpg'),
(18, 'Caméra de surveillance PoE', 'CAM-POE01', 16, 5, 2, 3000, 'materiels/camera.jpg');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `app1_materiel`
--
ALTER TABLE `app1_materiel`
  ADD PRIMARY KEY (`id`),
  ADD KEY `app1_materiel_categorie_id_9921e0ae_fk_app1_categorie_id` (`categorie_id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `app1_materiel`
--
ALTER TABLE `app1_materiel`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `app1_materiel`
--
ALTER TABLE `app1_materiel`
  ADD CONSTRAINT `app1_materiel_categorie_id_9921e0ae_fk_app1_categorie_id` FOREIGN KEY (`categorie_id`) REFERENCES `app1_categorie` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
