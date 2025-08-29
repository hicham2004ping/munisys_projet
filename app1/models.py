from time import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from django.db import models

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

class LigneCommande(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()

class Commande(models.Model):
    lignes = models.ManyToManyField(LigneCommande)

    @property
    def total_price(self):
        """Calcule le prix total de la commande"""
        total = 0
        for ligne in self.lignes.all():
            total += ligne.produit.prix * ligne.quantite
        return total
class Categorie(models.Model):
    nom=models.CharField(max_length=100)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('normal', 'Utilisateur normal'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Responsabilite(models.Model):
    utilisateur=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    categorie=models.ForeignKey(Categorie,on_delete=models.CASCADE)

class Materiel(models.Model):
    nom=models.CharField(max_length=100)
    refference=models.CharField(max_length=100)
    quantite_stock=models.IntegerField()
    categorie=models.ForeignKey(Categorie,on_delete=models.CASCADE)
    prix=models.IntegerField()
    min_quantite=models.IntegerField()
    image = models.ImageField(upload_to='materiels/', blank=True, null=True)

class Mouvement(models.Model):
    date=models.DateField()
    type=models.CharField(max_length=100)
    quantite=models.IntegerField()
    materiel=models.ForeignKey(Materiel,on_delete=models.CASCADE)
    effectuer_par=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=100, default='en attente')
    comerciale=models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class Installation(models.Model):
    technicien = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    commande= models.ForeignKey(Commande, null=True,blank=True,on_delete=models.CASCADE)
    date_installation = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=100, default='en attente')

class Notification(models.Model):
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    message = models.TextField()
    date_envoi = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)

class LigneDeCommande(models.Model):
    commande    = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Materiel, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.PositiveIntegerField()

class AffectationUtilisateur(models.Model):
    dernier_commercial = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dernier_commercial')
    dernier_technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dernier_technicien')
    dernier_coursier= models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dernier_coursier')

class PreparerCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    technicien=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    statut=models.CharField(max_length=100,blank=True,null=True)

class CoursierCommande(models.Model):
    coursier=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    Commande=models.ForeignKey(Commande,on_delete=models.CASCADE)
    statut=models.CharField(max_length=100,blank=True,null=True)

class ClienCommandeAvis(models.Model):
    commande=models.ForeignKey(Commande,on_delete=models.CASCADE)
    client=models.ForeignKey(Client,on_delete=models.CASCADE)
    avis=models.CharField(max_length=120)

class UserInterventino(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    fichier=models.FileField(upload_to="fiche_d'intervention/",blank=True,null=True)
    date_ajout = models.DateTimeField(default=timezone.now)

class fichier_upload(models.Model):
    numero=models.IntegerField()

