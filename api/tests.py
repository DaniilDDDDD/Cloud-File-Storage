import tempfile

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import File

User = get_user_model()


class FileTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.client_auth = Client()
        self.user = User.objects.create_user(username="sarah",
                                             email="connor.s@skynet.com",
                                             password="qwerty1234")
        self.client_auth.force_login(self.user)

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

    def tearDown(self) -> None:
        self.client.logout()
        self.client_auth.logout()
        self.user.delete()
        self.file.delete()

    def test_file_list(self):
        response = self.client.get(reverse('files-list'))
        print(response.status_code)
