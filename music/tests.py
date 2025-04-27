from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Artist, Album, Song, Playlist
import datetime

class MusicAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.token = self.client.post(
            reverse('api_token_auth'), 
            {'username': 'testuser', 'password': 'testpass123'}
        ).data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        
        # Create test data
        self.artist = Artist.objects.create(
            name='Test Artist',
            bio='Test bio',
            country='US'
        )
        
        self.album = Album.objects.create(
            title='Test Album',
            artist=self.artist,
            release_date='2020-01-01',
            genre='Rock'
        )
        
        self.song = Song.objects.create(
            title='Test Song',
            album=self.album,
            duration=datetime.timedelta(minutes=3, seconds=30),
            track_number=1
        )
        
        self.playlist = Playlist.objects.create(
            name='Test Playlist',
            user=self.user
        )
        self.playlist.songs.add(self.song)

    def test_artist_list(self):
        url = reverse('artist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_artist(self):
        url = reverse('artist-list')
        data = {
            'name': 'New Artist',
            'bio': 'New bio',
            'country': 'UK'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artist.objects.count(), 2)

    def test_album_detail(self):
        url = reverse('album-detail', args=[self.album.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Album')

    def test_song_update(self):
        url = reverse('song-detail', args=[self.song.id])
        data = {'title': 'Updated Song Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.song.refresh_from_db()
        self.assertEqual(self.song.title, 'Updated Song Title')

    def test_playlist_creation(self):
        url = reverse('playlist-list')
        data = {
            'name': 'My Playlist',
            'song_ids': [self.song.id],
            'is_public': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Playlist.objects.count(), 2)

    def test_add_song_to_playlist(self):
        url = reverse('playlist-add-song', args=[self.playlist.id])
        new_song = Song.objects.create(
            title='Another Song',
            album=self.album,
            duration=datetime.timedelta(minutes=4),
            track_number=2
        )
        data = {'song_id': new_song.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.playlist.songs.count(), 2)

    def test_unauthorized_access(self):
        self.client.credentials()  # Remove authentication
        url = reverse('artist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        url = reverse('playlist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)