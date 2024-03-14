import pytest
import shutil
from ..server import app


class BaseTestClass:

    def setup_method(self):
        # Sauvegardez les fichiers originaux avant chaque test
        shutil.copyfile('clubs.json', 'clubs_backup.json')
        shutil.copyfile('competitions.json', 'competitions_backup.json')

    def teardown_method(self):
        # Restaurez les fichiers originaux après chaque test
        shutil.move('clubs_backup.json', 'clubs.json')
        shutil.move('competitions_backup.json', 'competitions.json')


class TestIntegrationFlow(BaseTestClass):

    def test_full_integration_flow(self, client):
        # Étape 1: Vérification du tableau de la page index
        response = client.get('/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert '<table>' in data
        assert 'Simply Lift' in data
        assert 'Iron Temple' in data
        assert 'She Lifts' in data
        assert '13' in data
        assert '4' in data
        assert '12' in data

        # Étape 2: Connexion avec un email enregistré
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'}, follow_redirects=True)
        assert response.status_code == 200
        assert 'Welcome, john@simplylift.co' in response.data.decode('utf-8')

        # Étape 3: Inscription à un tournoi
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '6'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Congratulations! Your booking is confirmed." in response.data.decode('utf-8')

        # Étape 4: Retour à la page welcome.html et vérification des points et places
        response = client.get('/showSummary?email=john@simplylift.co', follow_redirects=True)
        data = response.data.decode('utf-8')
        assert 'Welcome, john@simplylift.co' in data
        assert 'Points available: 7' in data
        assert 'Number of Places: 19' in data

        # Étape 5: Déconnexion
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert 'Welcome to the GUDLFT Registration Portal!' in response.data.decode('utf-8')

        # Étape 6: Nouvelle vérification du tableau dans la page index après déconnexion
        response = client.get('/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert '<table>' in data
        assert 'Simply Lift' in data
        assert 'Iron Temple' in data
        assert 'She Lifts' in data
        assert '7' in data
        assert '4' in data
        assert '12' in data
