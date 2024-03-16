import json
import shutil
import pytest
from ..server import app


def load_json_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def load_clubs():
    return load_json_data('clubs.json')['clubs']


def load_competitions():
    return load_json_data('competitions.json')['competitions']


class BaseTestClass:

    def setup_method(self):
        # Sauvegardez les fichiers originaux avant chaque test
        shutil.copyfile('clubs.json', 'clubs_backup.json')
        shutil.copyfile('competitions.json', 'competitions_backup.json')

    def teardown_method(self):
        # Restaurez les fichiers originaux après chaque test
        shutil.move('clubs_backup.json', 'clubs.json')
        shutil.move('competitions_backup.json', 'competitions.json')


class TestEmailValidation(BaseTestClass):

    def test_show_summary_unknown_email(self, client):
        response = client.post('/showSummary', data={'email': 'unknown@example.com'}, follow_redirects=True)
        assert b'Sorry, that email was not found.' in response.data

    def test_show_summary_known_email(self, client):
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'}, follow_redirects=True)
        assert b'Welcome' in response.data


class TestPointLimits(BaseTestClass):

    def test_purchase_places_not_enough_points(self, client):
        data = {
            'club': 'Iron Temple',
            'competition': 'Spring Festival',
            'places': '5'
        }
        # Envoi de la demande de réservation
        response = client.post('/purchasePlaces', data=data, follow_redirects=True)
        assert b'You do not have enough points to complete this booking' in response.data

    def test_purchase_places_enough_points(self, client):
        data = {
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '3'
        }
        # Envoi de la demande de réservation
        response = client.post('/purchasePlaces', data=data, follow_redirects=True)
        assert b'Congratulations! Your booking is confirmed.' in response.data


class TestPurchaseNumberPlaces(BaseTestClass):

    def test_purchase_places_too_many_requested(self, client):
        data = {
            'club': 'Simply Lift2',
            'competition': 'Spring Festival2',
            'places': '13'
        }
        response = client.post('/purchasePlaces', data=data, follow_redirects=True)
        assert b'Cannot reserve more than 12 places per competition' in response.data

    def test_purchase_places_allowed_number(self, client):
        data = {
            'club': 'Simply Lift2',
            'competition': 'Spring Festival2',
            'places': '12'
        }
        response = client.post('/purchasePlaces', data=data, follow_redirects=True)
        assert b'Congratulations! Your booking is confirmed.' in response.data


class TestDateCompetitionBooking(BaseTestClass):

    def test_book_past_competition(self, client):
        # Test de la tentative de réservation pour une compétition passée
        response = client.get('/book/Fall Classic/Simply Lift', follow_redirects=True)
        assert b"This competition has already passed" in response.data

    def test_book_future_competition(self, client):
        # Test de la tentative de réservation pour une compétition future (Fall Classic)
        response = client.get('/book/Spring Festival/Simply Lift', follow_redirects=True)

        assert b"Spring Festival" in response.data


class TestSaveData(BaseTestClass):

    def test_purchase_places_updates_points_and_saves(self, client):
        # Préparez les données de test
        club_name = 'She Lifts'
        competition_name = 'Fall Classic2'
        initial_places = 5

        # Chargement initial des données depuis les fichiers
        clubs = load_clubs()
        initial_club = next(club for club in clubs if club['name'] == club_name)
        initial_club_points = int(initial_club['points'])

        competitions = load_competitions()
        initial_competition = next(comp for comp in competitions if comp['name'] == competition_name)
        initial_competition_places = int(initial_competition['numberOfPlaces'])

        # Effectuez la réservation
        response = client.post('/purchasePlaces', data={
            'club': club_name,
            'competition': competition_name,
            'places': str(initial_places)
        }, follow_redirects=True)

        # Rechargez les données après la réservation
        clubs_updated = load_clubs()
        updated_club = next(club for club in clubs_updated if club['name'] == club_name)
        updated_club_points = int(updated_club['points'])

        competitions_updated = load_competitions()
        updated_competition = next(comp for comp in competitions_updated if comp['name'] == competition_name)
        updated_competition_places = int(updated_competition['numberOfPlaces'])

        # Vérifiez que les points du club ont été correctement déduits et que le nombre de places pour la compétition
        # a été correctement réduit
        assert updated_club_points == initial_club_points - initial_places, "Club points not updated correctly."
        assert updated_competition_places == initial_competition_places - initial_places, ("Competition places not "
                                                                                           "updated correctly.")

        # Assurez-vous que le message de confirmation est affiché
        assert b"Congratulations! Your booking is confirmed." in response.data


class TestDisplayPointClubs(BaseTestClass):

    def test_points_table(self, client):
        # Faites une requête GET sur la route qui affiche le tableau des points.
        response = client.get('/')

        # Vérifiez que le statut de la réponse est 200 (OK).
        assert response.status_code == 200

        # Convertissez les données de la réponse de byte à string pour le parsing HTML.
        data = response.data.decode('utf-8')

        # Vérifiez que la réponse contient les noms des clubs et leurs points.

        assert 'Simply Lift' in data
        assert 'Iron Temple' in data
        assert 'She Lifts' in data
        assert '13' in data
        assert '4' in data
        assert '12' in data

        # Vérifiez que le tableau est présent
        assert '<table>' in data
        assert '</table>' in data