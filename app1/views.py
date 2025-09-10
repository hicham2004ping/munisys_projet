from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import connection
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib import messages
from app1.models import Categorie, Responsabilite, Materiel, Mouvement, Client, LigneDeCommande, Commande, Notification, \
    Installation, AffectationUtilisateur, PreparerCommande, CoursierCommande, ClienCommandeAvis,UserInterventino
from django.shortcuts import render, redirect, get_object_or_404
from app1.models import CustomUser
from random import choice
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import traceback
import pandas as pd
import mimetypes
import sqlalchemy
import os
from django.http import Http404

def welcomeview(request):
    return render(request, "app1/acceuille.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect("adminn")

            elif user.role == "commercial":
                return redirect("comercial-dashboard")

            elif user.role == "client":
                return redirect("consutler_materiel-client")

            elif user.role == "technicien":
                return redirect("technicien_dashboard")

            elif user.role == "coursier":
                return redirect('coursier_dashboard')
            else:
                return redirect("user_dashboard")
        else:
            return redirect("login")
    return render(request, "app1/login.html")

@login_required
def admin_dashboard(request):
    actifs = CustomUser.objects.filter(is_active=True)
    commande = Commande.objects.all()
    total = commande.count
    en_attente = Commande.objects.filter(statut="en_attente")
    en_attente = en_attente.count()
    nbr_actifs = actifs.count()
    today = timezone.now()
    debut_mois = today.replace(day=1)
    mats = Materiel.objects.all()
    somme = 0
    for mat in mats:
        somme = mat.quantite_stock + somme
    print(somme)
    nouveau_users_ce_mois = CustomUser.objects.filter(
        is_active=True,
        date_joined__gte=debut_mois,
        date_joined__lte=today
    )
    return render(request, "app1/admin_dashboard.html", {
        "nbr_actifs": nbr_actifs,
        "nouveau_users_ce_mois": nouveau_users_ce_mois,
        "somme": somme,
        "total": total,
        "en_attente": en_attente,
    })

@login_required
def ajouter_nouveau_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        is_staff = 'is_staff' in request.POST
        print(role)

        user = CustomUser.objects.create_user(
            username=username,
            is_staff=is_staff,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role
        )
        return HttpResponse("on avance bien ")

    return render(request, "app1/nouveau_user.html")

@login_required
def supprimer_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            print(user)
            user.delete()
            return HttpResponse("L'utilisateur a été supprimé avec succès.")
        except CustomUser.DoesNotExist:
            return HttpResponseNotFound("L'utilisateur est introuvable.")
    return render(request, "app1/supprimer_user.html")

@login_required
def lister_users(request):
    users = CustomUser.objects.all()
    return render(request, "app1/liste_des_users.html", {'users': users})

@login_required
def modifier_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    print(user)
    if request.method == "POST":
        user.email = request.POST.get('email')
        user.username=request.POST.get('username')
        print(user.username)
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.role = request.POST.get('role')
        user.is_staff = (user.role == 'admin')
        user.save()
        return redirect('lister_users')
    return render(request, "app1/modifier_user.html", {"user": user})

@login_required
def consulter_materielle(request):
    materiels = Materiel.objects.all()
    return render(request, "app1/consulter_materielle_user.html", {"materiels": materiels})

@login_required
def dashboard_user(request):
    return render(request, "app1/utilisateur_normale_dashboard.html")

@login_required
def ajouter_mouvement(request, id):
    materiel = get_object_or_404(Materiel, id=id)
    admin = CustomUser.objects.get(id=1)
    if request.method == "POST":
        quantite = int(request.POST.get('quantite'))
        type = request.POST.get('type')
        if quantite > materiel.quantite_stock and type == "sortie":
            return HttpResponse("le stock n'est pas suffisant")
        if (
                materiel.quantite_stock + quantite) > materiel.min_quantite and type == "entrée" and materiel.quantite_stock < materiel.min_quantite:
            notif = Notification.objects.create(
                destinataire=admin,
                titre="reapporevisionment",
                message=f"le stock du  {materiel.nom} a ete renouvler , le stock actuel c'est {materiel.quantite_stock + quantite}",
                lu=False
            )

        Mouvement.objects.create(
            effectuer_par=request.user,
            date=timezone.now(),
            type=type,
            quantite=quantite,
            materiel=materiel,
        )

        if type == "sortie":
            materiel.quantite_stock -= quantite
        else:
            materiel.quantite_stock += quantite
        materiel.save()

        return redirect('consulter_materielle')

    return render(request, "app1/ajouter_mouvement.html", {'materiel': materiel})

@login_required
def historqiue_mouvement(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT m.id, m.date, m.type, m.quantite, mat.nom AS materiel_nom, u.username AS utilisateur
                       FROM app1_mouvement m
                                JOIN app1_materiel mat ON m.materiel_id = mat.id
                                JOIN app1_customuser u ON m.effectuer_par_id = u.id
                       ORDER BY m.date DESC
                       """)
        mouvements = cursor.fetchall()
    colonnes = ['ID', 'Date', 'Type', 'Quantité', 'Matériel', 'Utilisateur']
    return render(request, "app1/historique.html", {"mouvements": mouvements, "colonnes": colonnes})

def a_propos_du_site(request):
    return render(request, "app1/a_propos_du_site.html")

def sign_up_client(request):
    if request.method == "POST":
        email = request.POST.get('email')
        nom = request.POST.get('nom')
        password = request.POST.get('password')
        telephone = request.POST.get('telephone')
        password1 = request.POST.get('password1')
        print(password, " ", password1)
        errors = {}
        if password != password1:
            errors['password'] = "les 2 mots de passe ne sont pas idetiques"
        elif len(password) < 2:
            errors["taille"] = "la taille du mot de passe est insuffisant"
        try:
            validate_email(email)
            if Client.objects.filter(email=email).exists() or CustomUser.objects.filter(email=email).exists():
                errors['email'] = "Cet email est déjà utilisé."
        except ValidationError:
            errors['email'] = "Email invalide."
        if not errors:
            try:
                CustomUser.objects.create_user(
                    email=email,
                    first_name=nom,
                    password=password,
                    username=email,
                    is_active=True,
                    role='client'
                )

                Client.objects.create(
                    email=email,
                    nom=nom,
                    telephone=telephone,
                )

                print("on va se log in ")
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Erreur lors de la création du compte: {str(e)}")
        context = {
            'email': email,
            'nom': nom,
            'errors': errors
        }
        return render(request, "app1/creer_compte_client.html", context)

    return render(request, "app1/creer_compte_client.html")

@login_required
def consulter_materiel(request):
    materiels = Materiel.objects.filter(quantite_stock__gt=0)
    return render(request, "app1/test_photo.html", {"materiels": materiels})


@login_required
def ajouter_au_panier(request, id):
    if request.method == "POST":
        quantite = int(request.POST.get("quantite"))
        panier = request.session.get("panier", {})
        if str(id) in panier:
            panier[str(id)] += quantite
        else:
            panier[str(id)] = quantite
        request.session["panier"] = panier
    return redirect('consutler_materiel-client')


@login_required
def afficher_panier(request):
    panier = request.session.get("panier", {})
    produits = []
    total = 0
    print(panier.items())
    for id, qte in panier.items():
        produit = Materiel.objects.get(id=id)
        total += produit.prix * qte
        produits.append({"produit": produit, "quantite": qte})
    return render(request, "app1/panier.html", {"produits": produits, "total": total})


@login_required
def commander(request, id):
    produit = Materiel.objects.get(id=id)
    prix = produit.prix
    client = Client.objects.get(email=request.user.username)

    if request.method == "POST":
        qte = int(request.POST.get('qte'))
        produit.quantite_stock -= qte
        produit.save()
        commerciaux = CustomUser.objects.filter(role='commercial')
        commercial_assigne = choice(list(commerciaux)) if commerciaux else None
        print(qte, " ", produit)

        commande = Commande.objects.create(
            client=client,
            statut='en attente',
            comerciale=commercial_assigne
        )

        LigneDeCommande.objects.create(
            quantite=qte,
            commande=commande,
            produit=produit,
            prix_unitaire=prix
        )
        Notification.objects.create(
            destinataire=commercial_assigne,
            titre="Commande",
            message=f"Nouvelle commande du client {client.email}, le numero de telphone est {client.telephone}",
            lu=False
        )

        return redirect('consutler_materiel-client')
    return render(request, "app1/commande.html", {"produit": produit})


@login_required
def comercial_dashboard(request):
    return render(request, "app1/comerciale_dashboard.html")


@login_required
def notification_comerciale(request):
    notif_id = request.GET.get("lire")
    if notif_id:
        notif = get_object_or_404(Notification, id=notif_id)
        notif.lu = True
        notif.save()
        return redirect("notifications_comerciale")
    notifs = Notification.objects.filter(lu=False, destinataire=request.user)
    return render(request, "app1/notication_comerciale.html", {"notifs": notifs})


@login_required
def liste_commande_assinger(request):
    if "refuser" in request.GET:
        commande_id = request.GET.get("refuser")
        commande = get_object_or_404(Commande, id=commande_id)
        commande.statut = "annuler"
        user = CustomUser.objects.filter(username=commande.client.email).first()
        commande.save()

        Notification.objects.create(
            destinataire=user,
            titre="refus",
            message=f"votre commande d'id {commande.id} que vous avez effectuer le {commande.date_commande},a ete refuser",
        )
        return redirect("liste_commande_assinger")


    elif "approuver" in request.GET:
        commande_idd = request.GET.get("approuver")
        commande = get_object_or_404(Commande, id=commande_idd)
        commande.statut = "valider"
        commande.save()
        user = CustomUser.objects.filter(username=commande.client.email).first()

        technicien = get_suivant("technicien")

        Notification.objects.create(
            destinataire=user,
            titre="acceptation",
            message=f"votre commande d'id {commande.id} que vous avez effectuer le {commande.date_commande}, a ete approuver",
            lu=False
        )

        Notification.objects.create(
            destinataire=technicien,
            titre="Nouvelle commande à préparer",
            message=f"La commande d'id {commande_idd} du client {commande.client.nom} vous a été assignée pour préparation",
            lu=False
        )

        PreparerCommande.objects.create(
            commande=commande,
            technicien=technicien,
            statut="en_cours",
        )

        return redirect("liste_commande_assinger")

    # Récupérer les commandes en attente (pas "accepter")
    liste_commande = Commande.objects.select_related("client").filter(
        statut="accepter",
        comerciale_id=request.user.id,
    )
    return render(request, "app1/liste_commande_assigner.html",
                  {"liste_commande": liste_commande})

@login_required
def historique_commande_passe(request):
    commandes = Commande.objects.select_related("client").filter(
        comerciale_id=request.user.id,
        statut__in=["valider","livrer","expediter","installer","preparation_terminer"],
    )
    return render(request, "app1/historique_commande_comerciale.html", {"commandes": commandes})
@login_required
def dashboard_client(request):
    return render(request, "app1/dashboard_client.html")


@login_required
def consulter_notification_client(request):
    id_notif = request.GET.get("lire")
    if id_notif:
        notif = get_object_or_404(Notification, id=id_notif)
        notif.lu = True
        notif.save()
        return redirect('notifications_client')
    notifs = Notification.objects.filter(lu=False, destinataire=request.user)
    return render(request, "app1/client_notification.html", {"notifs": notifs})


@login_required
def historique_commande_passer_client(request):
    client = Client.objects.filter(email=request.user.username).first()
    if "annuler" in request.GET:
        id = request.GET.get("annuler")
        commande = get_object_or_404(Commande, id=id)
        commande.statut = "annuler"
        commande.save()
        lignes = LigneDeCommande.objects.filter(commande=commande)

        for ligne in lignes:
            materiel = Materiel.objects.get(id=ligne.produit.id)
            a = materiel.quantite_stock = materiel.quantite_stock + ligne.quantite
            materiel.save()

        Notification.objects.create(
            titre='annulation',
            message=f"votre commande d'id {commande.id} dans le {commande.date_commande} est annuler",
            destinataire=request.user,
        )

        a = Notification.objects.create(
            titre="annulation",
            message=f"la commade du client {commande.client.nom} d'id {commande.id} pour le {commande.date_commande} est annuler",
            destinataire=commande.comerciale,
        )
        return redirect('historique_commande_passer_client')
    elif "porsuivre" in request.GET:
        id = request.GET.get("porsuivre")
        commande = Commande.objects.get(id=id)
        commande.statut = "accepter"
        print("labayka ya nascerallah")
        commande.save()
        return redirect('historique_commande_passer_client')

    elif request.method == "POST":
        commande_id = request.POST.get("commande_id")
        feedback = request.POST.get("feedback")
        print("le feedback c'est", feedback)
        commande = Commande.objects.get(id=commande_id)
        existant = ClienCommandeAvis.objects.filter(commande=commande, client=client).exists()
        if not existant:
            print("on est dans la fonction ")
            k = ClienCommandeAvis.objects.create(
                commande=commande,
                client=client,
                avis=feedback,
            )
            return redirect('historique_commande_passer_client')
        else:
            k = ClienCommandeAvis.objects.create(
                commande=commande,
                client=client,
                avis=feedback,
            )
            print(k)
            return redirect('historique_commande_passer_client')
    else:
        client = Client.objects.filter(email=request.user.email).first()
        commandes = Commande.objects.filter(
            client=client,
        )
        return render(request, "app1/historique_commandes_client.html", {"commandes": commandes})


@login_required
def supprimer_du_panier(request, id):
    panier = request.session.get("panier", {})
    if str(id) in panier:
        del panier[str(id)]
    request.session["panier"] = panier
    return redirect("afficher_panier")


@login_required
def passer_commande(request):
    panier = request.session.get("panier", {})
    if not panier:
        return redirect("afficher_panier")
    if request.method == "POST":
        try:
            client = Client.objects.get(email=request.user.username)
            commercial_assigne = get_suivant("commercial")
            print(commercial_assigne)
            commande = Commande.objects.create(
                client=client,
                statut='en_attente',
                comerciale=commercial_assigne,
            )
            somme = 0
            for id, qte in panier.items():
                produit = Materiel.objects.get(id=id)
                prix = produit.prix
                qte = int(qte)
                somme += (prix * qte)

                produit.quantite_stock -= qte
                produit.save()

                LigneDeCommande.objects.create(
                    quantite=qte,
                    commande=commande,
                    produit=produit,
                    prix_unitaire=prix
                )

            for id, qte in panier.items():
                mat = Materiel.objects.get(id=id)
                if mat.quantite_stock < mat.min_quantite:
                    alerte_au_admin(id)

            if commercial_assigne:
                Notification.objects.create(
                    destinataire=commercial_assigne,
                    titre="Commande",
                    message=f"Nouvelle commande du client {client.email}, numéro: {client.telephone}, le prix total de la commande est {somme}",
                    lu=False
                )
                Notification.objects.create(
                    destinataire=request.user,
                    titre="Commande",
                    message=f"Votre commande d'id {commande.id} est en cours de traitement",
                    lu=False
                )

            request.session["panier"] = {}
            return redirect("consutler_materiel-client")
        except Exception as e:
            print(f"Erreur lors de la commande: {e}")
            return redirect("afficher_panier")
    return redirect("afficher_panier")


@login_required
def telecharger_recue(request, id):
    commande = Commande.objects.prefetch_related('lignes').get(id=id)
    lignes = commande.lignes.all()
    total = sum(ligne.quantite * ligne.prix_unitaire for ligne in lignes)

    # Création du PDF
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Paramètres de style
    primary_color = (0.129, 0.588, 0.953)  # Bleu Munisys
    secondary_color = (0.2, 0.2, 0.2)  # Gris foncé

    # ===== EN-TÊTE =====
    y_position = height - 50  # Commence en haut de la page

    # Logo et en-tête
    c.setFillColorRGB(*primary_color)
    c.rect(0, y_position, width, 50, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)  # Blanc
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y_position + 15, "MUNISYS MAROC")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y_position + 35, "DEVIS DE COMMANDE")
    y_position -= 60

    # ===== INFOS COMMANDE =====
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, f"COMMANDE N°: {commande.id}")
    c.setFont("Helvetica", 10)
    c.drawString(300, y_position, f"Date: {commande.date_commande.strftime('%d/%m/%Y %H:%M')}")
    y_position -= 20
    c.drawString(50, y_position, f"Commercial: {commande.comerciale.get_full_name()}")
    y_position -= 40

    # ===== TABLEAU DES ARTICLES =====
    # Ligne de séparation
    c.line(50, y_position, width - 50, y_position)
    y_position -= 20

    # En-têtes colonnes
    col_design = 50
    col_qte = width - 250
    col_pu = width - 180
    col_total = width - 100

    c.setFont("Helvetica-Bold", 10)
    c.drawString(col_design, y_position, "DÉSIGNATION")
    c.drawRightString(col_qte + 30, y_position, "QTÉ")
    c.drawRightString(col_pu + 30, y_position, "PRIX UNIT.")
    c.drawRightString(col_total + 30, y_position, "TOTAL")
    y_position -= 20

    # Contenu du tableau
    c.setFont("Helvetica", 9)
    for ligne in lignes:
        if y_position < 100:  # Gestion de saut de page si nécessaire
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 9)

        nom_produit = (ligne.produit.nom[:35] + '...') if len(ligne.produit.nom) > 35 else ligne.produit.nom
        c.drawString(col_design, y_position, nom_produit)
        c.drawRightString(col_qte + 30, y_position, str(ligne.quantite))
        c.drawRightString(col_pu + 30, y_position, f"{ligne.prix_unitaire:.2f} MAD")
        ligne_total = ligne.quantite * ligne.prix_unitaire
        c.drawRightString(col_total + 30, y_position, f"{ligne_total:.2f} MAD")
        y_position -= 15

    # ===== TOTAL =====
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 50, y_position, f"TOTAL GÉNÉRAL: {total:.2f} MAD")
    y_position -= 30

    # ===== PIED DE PAGE =====
    c.setFillColorRGB(*secondary_color)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 30, "Munisys Maroc - 10000 21 Av. Tadla, Rabat 10000")
    c.drawCentredString(width / 2, 20, "Tél: +XX XX XX XX XX - Email: contact@munisys.ma - Site: https://munisys.com/")

    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=f"commande_{commande.id}.pdf")

@login_required
def ajouter_materiel(request):
    categorie = Categorie.objects.all()
    if request.method == "POST":
        nom = request.POST.get("nom")
        stock = int(request.POST.get("stock"))
        ref = request.POST.get('ref')
        min = (request.POST.get('min'))
        prix = int(request.POST.get('prix'))
        categorie = request.POST.get("categorie")
        image = request.FILES.get('image')
        categorie = Categorie.objects.get(id=categorie)
        print(categorie, " ", image)
        Materiel.objects.create(
            nom=nom,
            quantite_stock=stock,
            refference=ref,
            min_quantite=min,
            prix=prix,
            image=image,
            categorie=categorie
        )
        return redirect('adminn')

    return render(request, "app1/ajouter_materielle.html", {"categorie": categorie})

@login_required
def lister_materiel(request):
    materiels = Materiel.objects.all()
    return render(request, "app1/lister_materielle.html", {"materiels": materiels})

@login_required
def modifier_materiel(request, id):
    materiel = Materiel.objects.get(id=id)
    if request.method == "POST":
        prix = int(request.POST.get("prix"))
        min = int(request.POST.get("min"))
        ref = request.POST.get("refference")
        stock = request.POST.get("quantite_stock")
        image = request.FILES.get('image')

        print(image, " ", prix)
        materiel.prix = prix
        materiel.min_quantite = min
        materiel.refference = ref
        materiel.quantite_stock = stock
        materiel.image = image
        materiel.save()
        return redirect('adminn')
    return render(request, "app1/modifier_materiel.html", {"materiel": materiel})

@login_required
def supprimer_materiel(request):
    if request.method == "POST":
        print(request.POST.get("nom"))
        materiel = Materiel.objects.filter(nom=request.POST.get("nom"))
        if materiel:
            materiel.delete()
            return redirect('adminn')
        else:
            return HttpResponse("ce nom ne correspand a aucun materiel ou produit ")
    return render(request, "app1/supprimer_materiele.html")


def alerte_au_admin(id):
    mat = Materiel.objects.get(id=id)
    Notification.objects.create(
        destinataire_id=1,
        titre="alerte",
        message=f"le prdouit {mat.nom} a surpase le sueil min ",
        lu=False
    )


def log_out(request):
    logout(request)
    return redirect('login')


@login_required
def notification_admin(request):
    id = request.GET.get("lire")
    if id:
        notification = Notification.objects.get(id=id)
        notification.lu = True
        notification.save()
        return redirect('notification_admin')
    notifs = Notification.objects.filter(destinataire_id=request.user, lu=False)
    return render(request, "app1/notififcation_admin.html", {"notifs": notifs})


@login_required
def technicien_dashboard(request):
    return render(request, "app1/technicien dashboard.html")


@login_required
def notifications_technicien(request):
    id = request.GET.get("lire")
    if id:
        notf = Notification.objects.get(id=id)
        notf.lu = True
        notf.save()
        return redirect('notifications_technicien')
    notifs = Notification.objects.filter(destinataire_id=request.user, lu=False)
    return render(request, "app1/notifications_technicien.html", {"notifs": notifs})


@login_required
def technicien_commande_concerner(request):
    idd = request.GET.get("approuver")
    if idd:
        installation = Installation.objects.get(id=idd)
        installation.statut = "confirmer"
        installation.save()
        return redirect('technicien_commande_concerner')
    installations = Installation.objects.filter(statut='en cours', technicien=request.user)
    return render(request, "app1/technicien_concerner.html", {"installations": installations})

@login_required
def historique_commande_concerner_technicien(request):
    installations = Installation.objects.filter(technicien=request.user, statut='confirmer')
    return render(request, "app1/historique_commande_installer.html", {"installations": installations})

@login_required
def technicien_hstoriqeu_mouvements(request):
    mvmts = Mouvement.objects.filter(effectuer_par=request.user)
    print(mvmts)
    return render(request, "app1/technicien_historique_mouvements.html", {"mvmts": mvmts})

@login_required
def liste_des_produits_depasser_seuil_min(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                       select *
                       from app1_materiel
                       where quantite_stock < min_quantite
                         and quantite_stock > 0
                       """)
        produits = cursor.fetchall()
        print(produits)
    return render(request, "app1/liste_prdouit_depasser_seuille_min.html", {"produits": produits})

def get_suivant(role):
    users = list(CustomUser.objects.filter(role=role).order_by('id'))
    if not users:
        return None

    suivi, _ = AffectationUtilisateur.objects.get_or_create(id=1)

    dernier_utilisateur = getattr(suivi, f'dernier_{role}', None)

    if not dernier_utilisateur or dernier_utilisateur not in users:
        suivant = users[0]
    else:
        index = users.index(dernier_utilisateur)
        suivant = users[(index + 1) % len(users)]

    setattr(suivi, f'dernier_{role}', suivant)
    suivi.save()
    return suivant

@login_required
def liste_commande_a_traiter(request):
    if "accepter" in request.GET:
        commande_id = request.GET.get("accepter")
        commande = get_object_or_404(Commande, id=commande_id)
        commande.statut = "accepter"  # Passe à "accepter" pour que le commercial puisse la traiter
        commande.save()

        # Notifier le commercial
        Notification.objects.create(
            destinataire=commande.comerciale,
            titre="Commande acceptée",
            message=f"La commande #{commande.id} a été acceptée par l'administration et nécessite votre traitement",
            lu=False
        )

        return redirect("a_traiter")

    elif "refuser" in request.GET:
        commande_id = request.GET.get("refuser")
        commande = get_object_or_404(Commande, id=commande_id)
        commande.statut = "annuler"
        commande.save()

        # Remettre le stock
        lignes = LigneDeCommande.objects.filter(commande=commande)
        for ligne in lignes:
            materiel = Materiel.objects.get(id=ligne.produit.id)
            materiel.quantite_stock += ligne.quantite
            materiel.save()

        # Notifier le client
        client_user = CustomUser.objects.filter(email=commande.client.email).first()
        if client_user:
            Notification.objects.create(
                destinataire=client_user,
                titre="Commande refusée",
                message=f"Votre commande #{commande.id} a été refusée par l'administration",
                lu=False
            )

        return redirect("a_traiter")

    commandes = Commande.objects.filter(statut="en_attente").select_related("client", "comerciale")
    return render(request, "app1/liste_commande_a_traiter.html", {"commandes": commandes})

@login_required
def historique_commande_finaliser(request):
    commandes = Commande.objects.filter(statut="finaliser")
    commandes_data = []
    for commande in commandes:
        lignes = LigneDeCommande.objects.filter(commande=commande)
        total = sum(ligne.produit.prix * ligne.quantite for ligne in lignes)

        try:
            installation = Installation.objects.get(commande=commande)
            technicien_nom = installation.technicien.first_name
        except Installation.DoesNotExist:
            technicien_nom = "Aucun"

        commandes_data.append({
            'commande': commande,
            'total': total,
            'technicien': technicien_nom,
            'lignes': lignes,
        })
    return render(request, "app1/historique_commande.html", {"commandes_data": commandes_data})

@login_required
def searched(request):
    if request.method == "POST":
        chercher = request.POST.get("chercher")
        produit = Materiel.objects.filter(nom__icontains=chercher)
        return render(request, "app1/search.html", {"produit": produit})
    else:
        return render(request, "app1/search.html")

@login_required
def produit_en_rupture_de_stocke(request):
    produits = Materiel.objects.filter(quantite_stock=0)
    return render(request, "app1/rupture_de_stock.html", {"produits": produits})

@login_required
def preparer_commande_technicien(request):
    if "preparer" in request.GET:
        id = request.GET.get("preparer")
        commande = Commande.objects.get(id=id)
        technicien = CustomUser.objects.get(id=request.user.id)

        if commande.statut == "annuler":
            messages.error(request, "Cette commande a été annulée par le client.")
            return redirect("commande_preparer")

        commande.statut = "preparation_terminer"
        commande.save()
        print("barca")
        hassan = PreparerCommande.objects.get(commande=commande)
        hassan.statut = "preparation_terminer"
        hassan.save()

        coursier_assigner = get_suivant("coursier")

        CoursierCommande.objects.create(
            Commande=commande,
            coursier=coursier_assigner,
            statut="en_expedition"
        )

        # Créer les mouvements de stock
        lignes = commande.lignes.all()
        for ligne in lignes:
            Mouvement.objects.create(
                type="sortie",
                quantite=ligne.quantite,
                effectuer_par=request.user,
                materiel=ligne.produit,
                date=timezone.now(),
            )
            ligne.produit.quantite_stock -= ligne.quantite
            ligne.produit.save()

        # Notifier le coursier
        Notification.objects.create(
            destinataire=coursier_assigner,
            titre="Nouvelle livraison",
            message=f"La commande #{commande.id} est prête pour livraison",
            lu=False
        )

        return redirect("commande_preparer")

    else:
        technicien = CustomUser.objects.get(id=request.user.id)
        commandes_assignées = PreparerCommande.objects.filter(
            technicien=technicien,
            statut="en_cours",  # Changé pour être cohérent
            commande__statut="valider"
        ).select_related("commande__client").prefetch_related("commande__lignes__produit")

        commandes_infos = []
        now = timezone.now()

        for assignation in commandes_assignées:
            commande = assignation.commande
            date_commande = commande.date_commande

            commandes_infos.append({
                "assignation": assignation,
                "commande": commande,
            })

        return render(request, "app1/liste_commande_a_preparer_technicien.html", {
            "commandes_infos": commandes_infos
        })

@login_required
def dashbaord_coursier(request):
    return render(request, "app1/dashboard_coursier_moderne.html")

@login_required
def liste_commande_assinger_coursier(request):
    if "expediter" in request.GET:
        id = request.GET.get("expediter")
        commande = Commande.objects.get(id=id)
        if commande.statut == "annuler":
            messages.error(request, "Cette commande a été annulée par le client.")
            return redirect('commande_coursier')
        commande.statut = 'expediter'
        commande.save()
        coursier_commande = CoursierCommande.objects.get(Commande=commande)
        coursier_commande.statut = "fin_expedition"
        coursier_commande.save()
        print(coursier_commande.statut)
        return redirect('commande_coursier')

    elif "livrer" in request.GET:
        id = request.GET.get("livrer")
        commande = Commande.objects.get(id=id)
        commande.statut = 'livrer'
        technicien_commande=PreparerCommande.objects.get(commande=commande)
        technicien=technicien_commande.technicien
        coursier_commande = CoursierCommande.objects.get(Commande=commande)
        coursier_commande.statut = "fin_livraison"
        coursier_commande.save()

        print(technicien)
        c = Installation.objects.create(
            statut="en_attente",
            technicien=technicien,
            commande=commande
        )
        commande.save()
        a = Notification.objects.create(
            titre="livraison d'une commande",
            message=f"la commande d'id {commande.id} a ete livrer le {timezone.now()} par le coursier {request.user.username} ",
            destinataire=commande.comerciale
        )

        b = Notification.objects.create(
            titre="affectation d'une installation",
            message=f"vous etes charger par l'installation de la commande d'id {commande.id}",
            destinataire=technicien,
        )
        print(b)
        return redirect('commande_coursier')
    else:
        commandes = CoursierCommande.objects.filter(coursier=request.user)
        return render(request, "app1/liste_commande_assigner_coursier.html", {"commandes": commandes})

@login_required
def liste_commandes_finsaliser_commerciale(request):
    if "finaliser" in request.GET:
        print("on est dans la fonction ")
        id = request.GET.get("finaliser")
        cmd = Commande.objects.get(id=id)
        user = CustomUser.objects.get(username=cmd.client.email)
        print(user)
        cmd.statut = 'finaliser'
        print("le statut de la commande est ", cmd.statut)
        cmd.save()
        a = Notification.objects.create(
            titre="finisaliser d'une commande",
            message=f"votre commande d'id {cmd.id} est maitenant declarer finsaliser et vous pouvez telecharger le recu de la commande",
            destinataire=user
        )
        print(a)
        return redirect('commande_finsaliser')
    else:
        commandes = Commande.objects.filter(statut="installer", comerciale=request.user)
        print(commandes)
        return render(request, "app1/liste_commande_finaliser_commerciale.html", {"commandes": commandes})

@login_required
def commande_a_installer_technicien(request):
    if "installer" in request.GET:
        id = request.GET.get("installer")
        cmd = Commande.objects.get(id=id)
        print(cmd)
        installation = Installation.objects.get(commande=cmd)
        print(installation)
        installation.statut = "terminer"
        installation.save()
        cmd.statut = 'installer'
        cmd.save()
        print("terminer")
        return redirect('commande_installer')
    else:
        commandes = Commande.objects.filter(
            statut="livrer",
            installation__technicien=request.user
        )
        return render(request, "app1/commande_a_installer_technicien.html", {"commandes": commandes})

@login_required
def telecharger_recue2(request, id):
    commande = Commande.objects.prefetch_related('lignes').get(id=id)
    lignes = commande.lignes.all()
    total = sum(ligne.quantite * ligne.prix_unitaire for ligne in lignes)

    # Création du PDF
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Paramètres de style
    primary_color = (0.129, 0.588, 0.953)  # Bleu Munisys
    secondary_color = (0.2, 0.2, 0.2)  # Gris foncé

    # ===== EN-TÊTE =====
    y_position = height - 50  # Commence en haut de la page

    # Logo et en-tête
    c.setFillColorRGB(*primary_color)
    c.rect(0, y_position, width, 50, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)  # Blanc
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y_position + 15, "MUNISYS MAROC")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y_position + 35, "RECUE DE COMMANDE")
    y_position -= 60

    # ===== INFOS COMMANDE =====
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, f"COMMANDE N°: {commande.id}")
    c.setFont("Helvetica", 10)
    c.drawString(300, y_position, f"Date: {commande.date_commande.strftime('%d/%m/%Y %H:%M')}")
    y_position -= 20
    c.drawString(50, y_position, f"Commercial: {commande.comerciale.get_full_name()}")
    y_position -= 40

    # ===== TABLEAU DES ARTICLES =====
    # Ligne de séparation
    c.line(50, y_position, width - 50, y_position)
    y_position -= 20

    # En-têtes colonnes
    col_design = 50
    col_qte = width - 250
    col_pu = width - 180
    col_total = width - 100

    c.setFont("Helvetica-Bold", 10)
    c.drawString(col_design, y_position, "DÉSIGNATION")
    c.drawRightString(col_qte + 30, y_position, "QTÉ")
    c.drawRightString(col_pu + 30, y_position, "PRIX UNIT.")
    c.drawRightString(col_total + 30, y_position, "TOTAL")
    y_position -= 20

    # Contenu du tableau
    c.setFont("Helvetica", 9)
    for ligne in lignes:
        if y_position < 100:  # Gestion de saut de page si nécessaire
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 9)

        nom_produit = (ligne.produit.nom[:35] + '...') if len(ligne.produit.nom) > 35 else ligne.produit.nom
        c.drawString(col_design, y_position, nom_produit)
        c.drawRightString(col_qte + 30, y_position, str(ligne.quantite))
        c.drawRightString(col_pu + 30, y_position, f"{ligne.prix_unitaire:.2f} MAD")
        ligne_total = ligne.quantite * ligne.prix_unitaire
        c.drawRightString(col_total + 30, y_position, f"{ligne_total:.2f} MAD")
        y_position -= 15

    # ===== TOTAL =====
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 50, y_position, f"TOTAL GÉNÉRAL: {total:.2f} MAD")
    y_position -= 30

    # ===== PIED DE PAGE =====
    c.setFillColorRGB(*secondary_color)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 30, "Munisys Maroc - 10000 21 Av. Tadla, Rabat 10000")
    c.drawCentredString(width / 2, 20, "Tél: +XX XX XX XX XX - Email: contact@munisys.ma - Site: https://munisys.com/")

    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=f"commande_{commande.id}.pdf")

@login_required
def avis_client_sur_commande(request):
    avis = ClienCommandeAvis.objects.filter(commande__comerciale=request.user)
    return render(request, "app1/avis_client_commande.html", {"avis": avis})

@login_required
def fichier_intervention(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Couleurs
    primary_color = (0.129, 0.588, 0.953)  # Bleu Munisys
    secondary_color = (0.2, 0.2, 0.2)  # Gris foncé

    # ===== EN-TÊTE =====
    y = height - 50
    c.setFillColorRGB(*primary_color)
    c.rect(0, y, width, 50, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y + 15, "MUNISYS MAROC")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y + 35, "FICHE D'INTERVENTION")
    y -= 70

    # ===== CHAMPS À REMPLIR =====
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)
    champs = [
        "Intervenant (Technicien / Coursier)",
        "Objet de l'intervention",
        "Date de début",
        "Date de fin",
        "Lieu de l'intervention",
        "Référence de commande (si applicable)",
        "Observations"
    ]

    for champ in champs:
        c.drawString(50, y, f"{champ} :")
        y -= 20
        c.line(50, y, width - 50, y)
        y -= 20
        if champ == "Observations":
            for _ in range(3):  # Plus de lignes pour les observations
                c.line(50, y, width - 50, y)
                y -= 20

    # ===== SIGNATURE =====
    c.drawString(50, y, "Signature de l'intervenant :")
    c.line(220, y, width - 50, y)
    y -= 30
    c.drawString(50, y, "Cachet de l'entreprise :")
    c.line(220, y, width - 50, y)

    # ===== PIED DE PAGE =====
    c.setFillColorRGB(*secondary_color)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 30, "Munisys Maroc - 21 Av. Tadla, Rabat 10000")
    c.drawCentredString(width / 2, 20, "Tél: +XX XX XX XX XX - Email: contact@munisys.ma - Site: https://munisys.com/")

    # Finaliser le PDF
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename="fiche_intervention.pdf")


@login_required
def uploader_fiche_intervention(request):
    if request.method == "POST":
        utilisateur = CustomUser.objects.get(id=request.user.id)
        fichier = request.FILES.get("fichier")
        type_mime, encoding = mimetypes.guess_type(fichier.name)
        types_acceptes = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
        max_taille = 5 * 1024 * 1024
        if type_mime in types_acceptes and fichier.size <= max_taille:
            k=UserInterventino.objects.create(
                fichier=fichier,
                user=utilisateur)
            if utilisateur.role == "technicien":
                return redirect('technicien_dashboard')
            elif utilisateur.role == "commercial":
                return redirect('comercial-dashboard')
            elif utilisateur.role == "coursier":
                return redirect('coursier_dashboard')
            elif request.user.is_superuser:
                return redirect('adminn')
        else:
            return HttpResponse("ce fichier ne respecte pas les normes ")
    return render(request, "app1/uploader-fiche_intervention.html")


@login_required
def historique_intervention(request):
    if 'telecharger' in request.GET:
        idd = request.GET.get('telecharger')
        intervention = UserInterventino.objects.get(id=idd)
        fichier_path = os.path.join("media", f"{intervention.fichier}")
        if not os.path.exists(fichier_path):
            raise Http404("Fichier introuvable.")
        return FileResponse(open(fichier_path, 'rb'), as_attachment=True, filename=f"{intervention.fichier}")
    interventions = UserInterventino.objects.all()
    return render(request, "app1/admin_visualier_intervention.html", {"interventions": interventions})

@login_required
def nombre_intervention_par_user(request):
    # Placeholder pour le nombre d'interventions par utilisateur
    return render(request, "app1/nombe_fiche_intervention_par_user.html", {"result": []})


@login_required
def temps_ecoule_avant_date_limiter(request):
    coursier = CustomUser.objects.get(id=request.user.id)
    commandes_assignées = CoursierCommande.objects.filter(coursier=coursier).filter(
        ~Q(Commande__statut="annuler") & ~Q(Commande__statut="finaliser"))
    commandes_infos = []
    now = timezone.now()

    for assignation in commandes_assignées:
        commande = assignation.Commande
        date_commande = commande.date_commande
        date_limite = getattr(commande, 'date_limite', None)

        if date_commande and date_limite and date_limite > date_commande:
            temps_total = (date_limite - date_commande).total_seconds()
            temps_ecoule = (now - date_commande).total_seconds()
            pourcentage_utilise = min(max((temps_ecoule / temps_total) * 100, 0), 100)  # clamp entre 0 et 100
        else:
            pourcentage_utilise = None
        commandes_infos.append({
            "assignation": assignation,
            "commande": commande,
            "temps_utilise_pourcent": round(pourcentage_utilise, 1) if pourcentage_utilise is not None else "N/A"
        })
    return render(request, "app1/templates/app1/temps_ecouler_coursier.html", {"commandes_infos": commandes_infos})


@login_required
def temps_ecoule_avant_date_limiter_commercial(request):
    commerciale = CustomUser.objects.get(id=request.user.id)
    commandes_assignées = Commande.objects.filter(comerciale=commerciale).filter(
        ~Q(statut="finaliser") & ~Q(statut="annuler"))
    commandes_infos = []
    now = timezone.now()

    for assignation in commandes_assignées:
        date_commande = assignation.date_commande
        print(date_commande)
        date_limite = getattr(assignation, 'date_limite', None)
        print(date_limite)
        if date_commande and date_limite and date_limite > date_commande:
            temps_total = (date_limite - date_commande).total_seconds()
            temps_ecoule = (now - date_commande).total_seconds()
            pourcentage_utilise = min(max((temps_ecoule / temps_total) * 100, 0), 100)  # clamp entre 0 et 100
        else:
            pourcentage_utilise = None
        commandes_infos.append({
            "assignation": assignation,
            "commande": assignation,
            "temps_utilise_pourcent": round(pourcentage_utilise, 1) if pourcentage_utilise is not None else "N/A"
        })
    return render(request, "app1/templates/app1/temps_ecouler_commerciale.html", {"commandes_infos": commandes_infos})


@login_required
def temps_ecoule_avant_date_limiter_technicien(request):
    technicien = CustomUser.objects.get(id=request.user.id)
    print(technicien.username)
    commandes_assignées = PreparerCommande.objects.filter(technicien=technicien).filter(
        ~Q(commande__statut="finaliser") & ~Q(commande__statut="annuler"))
    print(commandes_assignées)
    commandes_infos = []
    now = timezone.now()

    for assignation in commandes_assignées:
        commande = assignation.commande
        print("l'id de la commande est ", commande.id)
        date_commande = commande.date_commande
        date_limite = getattr(commande, 'date_limite', None)

        if date_commande and date_limite and date_limite > date_commande:
            temps_total = (date_limite - date_commande).total_seconds()
            temps_ecoule = (now - date_commande).total_seconds()
            pourcentage_utilise = min(max((temps_ecoule / temps_total) * 100, 0), 100)
            print(temps_ecoule, " le temps total est ", temps_total)
        else:
            pourcentage_utilise = None
        commandes_infos.append({
            "assignation": assignation,
            "commande": commande,
            "temps_utilise_pourcent": round(pourcentage_utilise, 1) if pourcentage_utilise is not None else "N/A"

        })
    return render(request, "app1/templates/app1/temps_ecouler_technicien.html", {"commandes_infos": commandes_infos})

@login_required
def import_users(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        if fichier:
            type_mime, encoding = mimetypes.guess_type(fichier.name)
            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]
            if type_mime in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    df.to_sql(name='app1_customuser', index=False, if_exists='append', con=conn)
                    return redirect('adminn')
                except Exception as e:
                    print(traceback.format_exc())
                    return HttpResponse("une erreur s'est produit")
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/uploader_csv_users.html')

@login_required
def import_clients(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        if fichier:
            type_mime, encoding = mimetypes.guess_type(fichier.name)
            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]
            if type_mime in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    df.to_sql(name='app1_client', index=False, if_exists='append', con=conn)
                    return redirect('adminn')
                except Exception as e:
                    return render(request, 'app1/uploader_csv_client.html',
                                  {'error': f"erreur lors de l'import {str(e)}"})
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/uploader_csv_client.html')

@login_required
def import_commandes(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        fichier1 = request.FILES.get('fichier1')
        if fichier and fichier1:
            type_mime, encoding = mimetypes.guess_type(fichier.name)
            type_mime1, encoding1 = mimetypes.guess_type(fichier1.name)
            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]

            if type_mime in types_acceptes and type_mime1 in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    df1 = pd.read_csv(fichier1)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    with conn.begin() as connection:
                        df.to_sql(name='app1_commande', index=False, if_exists='append', con=connection)
                        df1.to_sql(name='app1_lignedecommande', index=False, if_exists='append', con=connection)
                    print(traceback.format_exc())

                    return redirect('adminn')
                except Exception as e:
                    return render(request, 'app1/importer_csv_commandes.html',
                                  {'error': f"erreur lors de l'import {str(e)}"})
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/importer_csv_commandes.html')


@login_required
def import_couriser_commandes(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        if fichier:
            type_mime, encoding = mimetypes.guess_type(fichier.name)

            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]
            if type_mime in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    df.to_sql(name='app1_coursiercommande', index=False, if_exists='append', con=conn)
                    return redirect('adminn')
                except Exception as e:
                    return render(request, 'app1/upload_coursier_commande_csv.html',
                                  {'error': f"erreur lors de l'import {str(e)}"})
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/upload_coursier_commande_csv.html')


@login_required
def import_installations_techncien(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        if fichier:
            type_mime, encoding = mimetypes.guess_type(fichier.name)
            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]
            if type_mime in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    df.to_sql(name='app1_installation', index=False, if_exists='append', con=conn)
                    return redirect('adminn')
                except Exception as e:
                    return render(request, 'app1/upload_installations_csv.html',
                                  {'error': f"erreur lors de l'import {str(e)}"})
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/upload_installations_csv.html')

@login_required
def import_preparer_technicien(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        if fichier:
            type_mime, encoding = mimetypes.guess_type(fichier.name)
            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]
            if type_mime in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    df.to_sql(name='app1_preparercommande', index=False, if_exists='append', con=conn)
                    return redirect('adminn')
                except Exception as e:
                    return render(request, 'app1/upload_preparation_csv.html',
                                  {'error': f"erreur lors de l'import {str(e)}"})
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/upload_preparation_csv.html')

@login_required
def import_mouvements(request):
    if request.method == "POST":
        fichier = request.FILES.get('fichier')
        if fichier:
            print(fichier)
            type_mime, encoding = mimetypes.guess_type(fichier.name)
            types_acceptes = ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]
            if type_mime in types_acceptes:
                try:
                    df = pd.read_csv(fichier)
                    conn = sqlalchemy.create_engine(
                        'mysql+mysqlconnector://root:@localhost:3306/gestion_inventaire'
                    )
                    print(df.dtypes)
                    df.to_sql(name='app1_mouvement', index=False, if_exists='append', con=conn)
                    return redirect('adminn')
                except Exception as e:
                    print(traceback.format_exc())
                    return render(request, 'app1/importer_mouvements.html',
                                  {'error': f"erreur lors de l'import {str(e)}"})
            else:
                return HttpResponse('le format du fichier nest pas valide')
        else:
            return HttpResponse('aucun fichier na ete choisis')
    return render(request, 'app1/importer_mouvements.html')

@login_required
def liste_demandes_devis(request):
    # Récupérer les commandes en attente de devis
    commandes = Commande.objects.filter(statut="en_attente", comerciale=request.user).select_related(
        'client').prefetch_related('lignes__produit')

    # Calculer la valeur totale
    total_value = 0
    for commande in commandes:
        for ligne in commande.lignes.all():
            total_value += ligne.produit.prix * ligne.quantite

    context = {
        'commandes': commandes,
        'total_value': total_value
    }

    return render(request, "app1/liste_demandes_devis.html", context)

@login_required
def negocier_devis(request, id):
    commande = get_object_or_404(Commande, id=id)
    if request.method == "POST":
        commentaire = request.POST.get('commentaire')
        remise = request.POST.get('remise', 0)

        # Mettre à jour la commande avec les informations de négociation
        commande.commentaire_commercial = commentaire
        commande.remise_globale = float(remise) if remise else 0
        commande.statut = "devis_envoye"
        commande.date_devis = timezone.now()
        commande.save()

        # Notifier le client
        client_user = CustomUser.objects.filter(email=commande.client.email).first()
        if client_user:
            Notification.objects.create(
                destinataire=client_user,
                titre="Devis reçu",
                message=f"Vous avez reçu un devis pour votre commande #{commande.id}",
                lu=False
            )

        return redirect('demandes_devis')

    return render(request, "app1/negocier_devis.html", {"commande": commande})

@login_required
def envoyer_devis(request, id):
    commande = get_object_or_404(Commande, id=id)
    if request.method == "POST":
        # Confirmer l'envoi du devis
        commande.statut = "devis_envoye"
        commande.date_devis = timezone.now()
        commande.save()

        # Notifier le client
        client_user = CustomUser.objects.filter(email=commande.client.email).first()
        if client_user:
            Notification.objects.create(
                destinataire=client_user,
                titre="Devis confirmé",
                message=f"Le devis pour votre commande #{commande.id} a été envoyé",
                lu=False
            )

        return redirect('demandes_devis')

    return render(request, "app1/confirmer_envoi_devis.html", {"commande": commande})

@login_required
def devis_client(request):
    # Récupérer les devis reçus par le client
    client = Client.objects.filter(email=request.user.email).first()
    if client:
        commandes = Commande.objects.filter(client=client, statut="devis_envoye")
    else:
        commandes = []
    return render(request, "app1/devis_client.html", {"commandes": commandes})

@login_required
def repondre_devis(request, id):
    commande = get_object_or_404(Commande, id=id)
    if request.method == "POST":
        reponse = request.POST.get('reponse')

        if reponse == "accepter":
            commande.statut = "accepter"
            message = f"Le client a accepté le devis pour la commande #{commande.id}"
        else:
            commande.statut = "devis_refuse"
            message = f"Le client a refusé le devis pour la commande #{commande.id}"

        commande.save()

        # Notifier le commercial
        Notification.objects.create(
            destinataire=commande.comerciale,
            titre="Réponse au devis",
            message=message,
            lu=False
        )

        return redirect('devis_client')

    return render(request, "app1/repondre_devis.html", {"commande": commande})
