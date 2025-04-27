from django.core.management.base import BaseCommand
from music.api import fetch_jamendo_tracks
from music.models import Artist, Album, Song
import requests
from datetime import timedelta

class Command(BaseCommand):
    help = 'Fetch songs from Jamendo API'

    def handle(self, *args, **options):
        data = fetch_jamendo_tracks(genre='pop', limit=20)
        
        for track in data['results']:
            # Get or create artist
            artist, _ = Artist.objects.get_or_create(
                name=track['artist_name'],
                defaults={
                    'bio': '',
                    'country': track.get('artist_country', '')
                }
            )
            
            # Get or create album (if available)
            album = None
            if track.get('album_name'):
                album, _ = Album.objects.get_or_create(
                    title=track['album_name'],
                    artist=artist,
                    defaults={
                        'release_date': track.get('releasedate', '2020-01-01'),
                        'genre': track.get('musicinfo', {}).get('genre', 'Pop')
                    }
                )
            
            # Create song
            duration = timedelta(seconds=track['duration'])
            Song.objects.get_or_create(
                external_id=track['id'],
                source='jamendo',
                defaults={
                    'title': track['name'],
                    'artist': artist,
                    'album': album,
                    'duration': duration,
                    'audio_url': track['audio'],
                    'genre': track.get('musicinfo', {}).get('genre', 'Pop'),
                    'release_date': track.get('releasedate', '2020-01-01'),
                    'bpm': track.get('musicinfo', {}).get('bpm'),
                    'bitrate': track.get('audioinfo', {}).get('bitrate'),
                    'sample_rate': track.get('audioinfo', {}).get('samplerate')
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fetched {len(data["results"])} songs'))