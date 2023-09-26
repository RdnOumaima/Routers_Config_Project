# test_routes.py
from app import app
from flask import Flask, render_template
import unittest

class TestYourApp(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)

    def test_inscription_page(self):
        response = self.client.get('/inscription')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create an account', response.data)

    def test_signup_link(self):
        # Envoyez une requête GET à la page de connexion
        response = self.client.get('/')

        # Assurez-vous que le code d'état HTTP est égal à 200 (page de connexion accessible)
        self.assertEqual(response.status_code, 200)

        # Recherchez le lien "Sign up now" dans le contenu de la page
        signup_link = '<a href="/inscription">Sign up now</a>'
        self.assertIn(signup_link.encode(), response.data)

        # Suivez le lien "Sign up now" en cliquant dessus
        response = self.client.get('/inscription')

        # Assurez-vous que le code d'état HTTP est égal à 200 (page d'inscription accessible)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create an account', response.data)  # Assurez-vous que le texte 'Inscription' est présent sur la page

   # def test_signin_link(self):
   #     with self.client as c:
    #        response = c.get('/inscription')
     #       self.assertEqual(response.status_code, 200)
            # Assurez-vous que le lien de login est présent dans la page d'inscription
           # signin_link = '<a href="{{ url_for(\'index\') }}">Login here</a>'
      #      self.assertIn(b'Already have an account? <a href="{{ url_for(\'index\') }}">Login here</a>', response.data)
       #     response = self.client.get('/')
        #    self.assertEqual(response.status_code, 200)
         #   self.assertIn(b'Login', response.data)


    def test_logout(self):
    # Assurez-vous que l'utilisateur est connecté en définissant une session
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1  # Remplacez 1 par l'ID d'un utilisateur existant dans votre base de données

            # Accédez à la page /logout
            response = c.get('/logout', follow_redirects=True)  # Utilisez follow_redirects=True pour suivre la redirection après la déconnexion

            # Assurez-vous que l'utilisateur est redirigé après la déconnexion
            self.assertEqual(response.status_code, 200)  # 200 correspond à une réponse OK
            self.assertIn(b'You have been logged out.', response.data)  # Assurez-vous que le message de déconnexion est présent dans la réponse







if __name__ == '__main__':
    unittest.main()