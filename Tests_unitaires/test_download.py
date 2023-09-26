from flask import Flask, request
from flask_testing import TestCase
from app import app  # Importez votre application Flask
import unittest
import io

# Importez ce qui est nécessaire

class TestDownloadConfiguration(TestCase):
    def create_app(self):
        # Configurez votre application Flask pour utiliser la base de données de test (si nécessaire)
        #app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/huawei_db_app'
        return app

    def test_download_configuration(self):
        # Accédez à la page où se trouve le bouton "Download Configuration"
        response = self.client.get('/upload')  # Remplacez '/generated_config' par l'URL de votre page avec le bouton

        # Vérifiez que la page s'affiche correctement
        self.assertEqual(response.status_code, 200)  # Assurez-vous que la réponse est OK

        # Vérifiez que le bouton "Download Configuration" est présent dans la réponse
        self.assertIn(b'Download Configuration', response.data)

        # Simulez un clic sur le bouton "Download Configuration"
        response = self.client.get('/download')  # Remplacez '/download' par l'URL de téléchargement

        # Vérifiez la réponse après avoir cliqué sur le bouton
        self.assertEqual(response.status_code, 200)  # Assurez-vous que la réponse est OK

        # Assurez-vous que la réponse contient le fichier que vous attendez ou au moins un lien de téléchargement valide
        # Vous pouvez vérifier le contenu de la réponse pour le nom du fichier ou le lien de téléchargement

if __name__ == '__main__':
    unittest.main()

