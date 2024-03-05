import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/showSummary', methods=['GET', 'POST'])
def showSummary():
    if request.method == 'POST':
        club = [club for club in clubs if club['email'] == request.form['email']]
    else:  # GET
        email = request.args.get('email')
        club = [club for club in clubs if club['email'] == email]

    if not club:
        flash("Sorry, that email was not found.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club[0], competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    # Convertir la date de la compétition en objet datetime pour la comparaison
    competition_date = datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    # Vérifier si la compétition est déjà passée
    if competition_date < datetime.now():
        flash("This competition has already passed")
        return redirect(url_for('showSummary', email=foundClub['email']))
    if foundClub and foundCompetition:
        return render_template(
            "booking.html", club=foundClub, competition=foundCompetition
        )
    else:
        flash("Something went wrong - please try again")
        return redirect(url_for('showSummary', email=foundClub['email']))



@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][0]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])

    # Vérifier si le club a suffisamment de points pour la réservation demandée
    if int(club["points"]) < placesRequired:
        flash("You do not have enough points to complete this booking")
        return render_template("welcome.html", club=club, competitions=competitions)

    # Vérifier que le nombre de places demandées ne dépasse pas 12
    if placesRequired > 12:
        flash("Cannot reserve more than 12 places per competition")
        return render_template("welcome.html", club=club, competitions=competitions)

    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired
    flash("Congratulations! Your booking is confirmed.")
    return render_template("welcome.html", club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
