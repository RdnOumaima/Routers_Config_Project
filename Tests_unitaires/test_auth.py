# test_auth.py
from flask import Flask, render_template
from app import app, db, User
from flask_testing import TestCase
import unittest

class TestAuthentication(TestCase):
    def create_app(self):
        # Changez la configuration de l'application pour utiliser la base de données de test
        #app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/huawei_db_app'
        return app

    def setUp(self):
        # Assurez-vous que la base de données est vide avant chaque test
        db.session.remove()
        db.drop_all()
        db.create_all()

        # Créez un utilisateur de test directement dans la base de données de test
        test_user = User(username='testuser', email='testuser@example.com', password='testpassword')
        db.session.add(test_user)
        db.session.commit()


    def test_registration(self):
        registration_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testPassword*2'
        }
        response = self.client.post('/inscription', data=registration_data, follow_redirects=False)  # Ne pas suivre la redirection ici

        # Assurez-vous que la réponse renvoie un code de statut 302 (redirection)
        self.assertEqual(response.status_code, 302)

       # Assurez-vous que la réponse redirige vers une URL quelconque (nous ne vérifions pas où elle redirige pour le moment)
        self.assertIsNotNone(response.location)


    def test_login(self):
        # Créez un utilisateur dans la base de données pour le test
        user = User(username='testuser1', email='testuser1@example.com', password='testpassword*22')
        db.session.add(user)
        db.session.commit()

        login_data = {
            'username': 'testuser1',
            'password': 'testpassword*22'
        }

        # Connectez-vous avec l'utilisateur
        response = self.client.post('/login', data=login_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Assurez-vous que l'utilisateur est connecté en vérifiant la session
        with self.client as c:
            response = c.get('/welcome')  # Accédez à une page protégée par la connexion
            self.assertIn(b'Welcome, testuser1!', response.data)  # Vérifiez si le message de bienvenue est présent dans la réponse
            self.assertEqual(user.username, 'testuser1')


        # Vous pouvez également vérifier d'autres informations de session si nécessaire
        with self.client.session_transaction() as sess:
            user_id = sess.get('user_id')
            self.assertIsNotNone(user_id)  # Assurez-vous que l'ID de l'utilisateur est défini dans la session

       
    def test_logout(self):
        # Créez un utilisateur dans la base de données pour le test
        user = User(username='testuser2', email='testuser2@example.com', password='testpassword*23')
        db.session.add(user)
        db.session.commit()

        # Connectez-vous avec l'utilisateur
        login_data = {
            'username': 'testuser2',
            'password': 'testpassword*23'
        }
        response = self.client.post('/login', data=login_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Déconnectez-vous
        with self.client as c:
            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Assurez-vous que l'utilisateur est redirigé vers la page de connexion
            self.assertIn(b'Login', response.data)

        # Vous pouvez également vérifier que la session de l'utilisateur est correctement nettoyée après la déconnexion
        with self.client.session_transaction() as sess:
            user_id = sess.get('user_id')
            self.assertIsNone(user_id)  # Assurez-vous que l'ID de l'utilisateur a été supprimé de la session

        # Assurez-vous que l'utilisateur ne peut plus accéder à des pages protégées après la déconnexion
        with self.client as c:
            response = c.get('/welcome')
            self.assertNotIn(b'Welcome', response.data)  # Assurez-vous que le message de bienvenue n'est pas présent dans la réponse



    def tearDown(self):
        # Supprimez toutes les données de la base de données après chaque test
        db.session.remove()
        db.drop_all()



if __name__ == '__main__':
    unittest.main()
