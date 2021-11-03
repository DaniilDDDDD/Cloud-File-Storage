import tempfile
import os
import shutil
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, CoreAPIClient

from bebranie.settings import MEDIA_ROOT
from .models import File

User = get_user_model()


class FileTests(APITestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.client_auth = CoreAPIClient()
        self.data = {
            "email": "vpupkin@yandex.ru",
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "qwerty1234"
        }
        self.user = User.objects.create(
            email=self.data['email'],
            username=self.data['username'],
            first_name=self.data['first_name'],
            last_name=self.data['last_name']
        )
        self.user.set_password(self.data['password'])
        self.user.save()

        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            f.write(b'Inside test file!')
            f.seek(0)
            some_file = f.read()
            uploaded = SimpleUploadedFile(
                'Test_file.txt', some_file,
                content_type='text/plain'
            )
            self.file = File.objects.create(
                author=self.user,
                file=uploaded
            )

        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            f.write(b'Inside test file1!')
            f.seek(0)
            some_file = f.read()
            uploaded = SimpleUploadedFile(
                'Test_file1.txt', some_file,
                content_type='text/plain'
            )
            self.file1 = File.objects.create(
                access='public',
                author=self.user,
                file=uploaded,
                download_count=10
            )

    def client_login(self, requests_client: CoreAPIClient(), data) -> CoreAPIClient():
        response = self.client.post(reverse('login'), data={
            'email': data['email'],
            'password': data['password']
        })
        token = response.data['auth_token']

        requests_client.session.headers.update({
            'Authorization': f'Token {token}'
        })
        return requests_client

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()
        os.remove(MEDIA_ROOT + '/' + str(self.file.file))
        self.file.delete()
        os.remove(MEDIA_ROOT + '/' + str(self.file1.file))
        shutil.rmtree(MEDIA_ROOT + '/files/1', ignore_errors=True)
        self.file1.delete()

    def test_register_login_logout(self):
        data = {
            'username': "sarah.connor",
            'email': "connor.s@skynet.com",
            'first_name': 'sarah',
            'last_name': 'connor',
            'password': "qwerty1234"
        }
        response = self.client.post(reverse('users-list'), data=data)

        self.assertEqual(response.status_code, 201)

        user = User.objects.filter(pk=response.data['id']).first()
        self.assertIsNotNone(user)

        data = {
            'username': "sarah.connor",
            'email': "connor.s@skynet.com",
            'first_name': 'sarah',
            'last_name': 'connor'
        }
        response = self.client.post(reverse('users-list'), data=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'email': user.email,
            'password': "qwerty1234"
        }
        response = self.client.post(reverse('login'), data=data)
        self.assertEqual(response.status_code, 200)
        token = response.data['auth_token']
        self.assertIsInstance(token, str)

        data = {
            'email': user.email
        }
        response = self.client.post(reverse('login'), data=data)
        self.assertEqual(response.status_code, 400)

        response = self.client_auth.session.post(f"http://testserver{reverse('logout')}", headers={
            'Authorization': f'Token {token}'
        })
        self.assertEqual(response.status_code, 204)

        user.delete()

    def test_file_list_link(self):
        response = self.client.get(reverse('files-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['access'], 'public')
        self.assertEqual(response.data[0]['id'], self.file1.id)

        file_id = response.data[0]['id']
        _response = self.client_auth.get(
            f"http://testserver{reverse('files-link', args={file_id})}"
        )
        self.assertIn('view_link', _response)
        self.assertIn('download_link', _response)

        self.client_auth = self.client_login(self.client_auth, self.data)
        response = self.client_auth.get(f"http://testserver{reverse('files-list')}", format='json')
        self.assertEqual(len(response), 2)

        for item in response:
            file_id = item['id']
            _response = self.client_auth.get(
                f"http://testserver{reverse('files-link', args={file_id})}"
            )
            self.assertIn('view_link', _response)
            self.assertIn('download_link', _response)

            if item['access'] == 'only_author':
                _response = self.client.get(
                    f"http://testserver{reverse('files-link', args={file_id})}"
                )
                self.assertEqual(_response.status_code, 401)

    def test_change_access(self):
        self.client_auth = self.client_login(self.client_auth, self.data)
        response = self.client_auth.get(f"http://testserver{reverse('files-list')}", format='json')
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0]['access'], 'public')

        _response = self.client_auth.session.patch(
            f"http://testserver{reverse('files-list')}{response[0]['id']}/",
            data={
                'access': 'only_author'
            }
        )
        self.assertEqual(_response.status_code, 200)
        self.assertEqual(File.objects.filter(pk=response[0]['id']).first().access, 'only_author')

    def test_download_view_file(self):
        self.client_auth = self.client_login(self.client_auth, self.data)
        response = self.client_auth.get(f"http://testserver{reverse('files-list')}", format='json')

        _response = self.client_auth.get(
            f"http://testserver{reverse('files-link', args={response[0]['id']})}"
        )
        download_link = _response['download_link']

        self.assertEqual(File.objects.filter(id=self.file1.id).first().download_count, 10)

        response = self.client_auth.get(download_link)
        with open(response.name) as f:
            text = f.read()
            self.assertEqual(text, 'Inside test file1!')

        self.assertEqual(File.objects.filter(id=self.file1.id).first().download_count, 11)

        view_link = _response['view_link']
        response = self.client_auth.get(view_link)
        self.assertEqual(response, 'Inside test file1!')

