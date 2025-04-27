from datetime import timedelta
from io import BytesIO
import io
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .api import fetch_jamendo_tracks
from .response import create_response
from .models import Artist, Album, Song, Playlist
from .serializers import ArtistSerializer, AlbumSerializer, SongSerializer, PlaylistSerializer, UserLoginSerializer, UserRegistrationSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
import cloudinary.uploader

def upload_external_file_to_cloudinary(file_url, folder, resource_type):
    print(file_url)
    try:
        # 1. Download the file
        response = requests.get(file_url)
        if response.status_code != 200:
            print(f"Failed to download {file_url}")
            return None

        # 2. Upload to Cloudinary
        result = cloudinary.uploader.upload(
            BytesIO(response.content),  # Pass file bytes
            folder=f"{folder}/",
            resource_type=resource_type
        )
        return result['public_id']
    except Exception as e:
        print(f"Failed to upload {file_url}: {e}")
        return None

class UserRegistrationAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
            
            return create_response(
                success=True,
                message="User registered successfully",
                data=response_data,
                status_code=201
            )
        
        return create_response(
            success=False,
            message="Registration failed",
            errors=serializer.errors.get('errors', []),
            status_code=400
        )

class UserLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'user_id': user.id,
                'email': user.email,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
            
            return create_response(
                success=True,
                message="Login successful",
                data=response_data
            )
        
        return create_response(
            success=False,
            message="Login failed",
            errors=serializer.errors.get('errors', []),
            status_code=400
        )

class UserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user=request.user
        serializer = UserSerializer(user)
        return create_response(
            success=True,
            message="User Profile",
            data=serializer.data
        )

class ArtistAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        artists = Artist.objects.filter(user=request.user)
        serializer = ArtistSerializer(artists, many=True, context={'request': request})
        return create_response(
            success=True,
            message="Artists retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = ArtistSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return create_response(
                success=True,
                message="Artist created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return create_response(
            success=False,
            message="Artist creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ArtistDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, pk, user):
        return get_object_or_404(Artist, pk=pk, user=user)

    def get(self, request, pk):
        artist = self.get_object(pk, request.user)
        serializer = ArtistSerializer(artist, context={'request': request})
        return create_response(
            success=True,
            message="Artist retrieved successfully",
            data=serializer.data
        )

    def patch(self, request, pk):
        artist = self.get_object(pk, request.user)
        serializer = ArtistSerializer(artist, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return create_response(
                success=True,
                message="Artist updated successfully",
                data=serializer.data
            )
        return create_response(
            success=False,
            message="Artist update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        artist = self.get_object(pk, request.user)
        artist.delete()
        return create_response(
            success=True,
            message="Artist deleted successfully",
            status_code=status.HTTP_200_OK
        )

class AlbumAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        albums = Album.objects.filter(user=request.user)
        serializer = AlbumSerializer(albums, many=True, context={'request': request})
        return create_response(
            success=True,
            message="Albums retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = AlbumSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return create_response(
                success=True,
                message="Album created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return create_response(
            success=False,
            message="Album creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class AlbumDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, pk, user):
        return get_object_or_404(Album, pk=pk, user=user)

    def get(self, request, pk):
        album = self.get_object(pk, request.user)
        serializer = AlbumSerializer(album, context={'request': request})
        return create_response(
            success=True,
            message="Album retrieved successfully",
            data=serializer.data
        )

    def patch(self, request, pk):
        album = self.get_object(pk, request.user)
        serializer = AlbumSerializer(album, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return create_response(
                success=True,
                message="Album updated successfully",
                data=serializer.data
            )
        return create_response(
            success=False,
            message="Album update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        album = self.get_object(pk, request.user)
        album.delete()
        return create_response(
            success=True,
            message="Album deleted successfully",
            status_code=status.HTTP_200_OK
        )

from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
# from django.core.files.uploadedfile import InMemoryUploadedFile

class FetchSongTag(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {"success": False, "error": "No audio file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        audio_file = request.FILES['file']
        metadata = {}

        try:
            # Handle both in-memory and temporary file uploads
            if hasattr(audio_file, 'temporary_file_path'):
                # File is on disk (Django temporary upload)
                audio = File(audio_file.temporary_file_path(), easy=True)
            else:
                # File is in memory - read into BytesIO
                file_bytes = audio_file.read()
                file_io = io.BytesIO(file_bytes)
                audio_file.seek(0)  # Reset file pointer for future use
                audio = File(file_io, easy=True)

            if not audio:
                return Response(
                    {"success": False, "error": "Unsupported audio format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get accurate duration in seconds (float)
            duration = audio.info.length  # This returns float (seconds)

            # Extract common metadata
            result = {
                'duration': round(duration, 2),  # Rounded to 2 decimal places
                'bitrate': getattr(audio.info, 'bitrate', None),
                'sample_rate': getattr(audio.info, 'sample_rate', None),
                'channels': getattr(audio.info, 'channels', 2),
            }

            # Extract ID3 tags if available
            if hasattr(audio, 'tags'):
                tags = audio.tags
                result.update({
                    'title': tags.get('title', [''])[0] if tags.get('title') else None,
                    'artist': tags.get('artist', [''])[0] if tags.get('artist') else None,
                    'album': tags.get('album', [''])[0] if tags.get('album') else None,
                    'genre': tags.get('genre', [''])[0] if tags.get('genre') else None,
                    'track_number': tags.get('tracknumber', [''])[0] if tags.get('tracknumber') else None,
                    'bpm': tags.get('bpm', [''])[0] if tags.get('bpm') else None,
                    'year': tags.get('date', [''])[0] if tags.get('date') else None,
                })

            return Response(
                {"success": True, "metadata": result},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SongAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        songs = Song.objects.filter(user=request.user)
        serializer = SongSerializer(songs, many=True, context={'request': request})
        return create_response(
            success=True,
            message="Songs retrieved successfully",
            data=serializer.data
        )
    
    def post(self, request, format=None):
        user = request.user
        if not user.is_authenticated:
            return create_response(
                success=False,
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Handle both manual fields and auto-extracted metadata
        data = request.data
        audio_file = request.FILES.get('audio_file')
        art_file = request.FILES.get('art')

        if not data.get('title'):
            return create_response(
                success=False,
                message="Title is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 🔍 Check file size (15MB max)
        if audio_file.size > 15 * 1024 * 1024:  # 15MB in bytes
            return create_response(success=False, message="Audio file must be less than 15MB", status_code=status.HTTP_400_BAD_REQUEST)

        
        # Create song instance with provided data
        song_data = {
            'user': user.id,
            'title': data.get('title', 'Untitled'),
            'genre': data.get('genre'),
            'release_date': data.get('release_date'),
            'is_explicit': data.get('is_explicit', False),
            'lyrics': data.get('lyrics', ''),
            'track_number': data.get('track_number'),
            'audio_file': audio_file,
            'art': art_file
        }

        # Handle album foreign key
        album_id = data.get('album')
        if album_id:
            try:
                album = Album.objects.get(id=album_id)
                song_data['album'] = album.id
            except Album.DoesNotExist:
                return create_response(
                    success=False,
                    message=f"Album with ID {album_id} does not exist",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Handle artist foreign key
        artist_id = data.get('artist')
        if artist_id:
            try:
                artist = Artist.objects.get(id=artist_id)
                song_data['artist'] = artist.id
            except Artist.DoesNotExist:
                return create_response(
                    success=False,
                    message=f"Artist with ID {artist_id} does not exist",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = SongSerializer(data=song_data, context={'request': request})
        if not serializer.is_valid():
            return create_response(
                success=False,
                message="Invalid song data",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            album = Album.objects.get(id=data.get('album'))
            song_data['album'] = album.id
        except Album.DoesNotExist:
            return create_response(success=False, message="Album not found", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            artist = Artist.objects.get(id=data.get('artist'))
            song_data['artist'] = artist.id
        except Artist.DoesNotExist:
            return create_response(success=False, message="Artist not found", status_code=status.HTTP_400_BAD_REQUEST)

        # 🚀 Upload to Cloudinary
        try:
            cloudinary_response = cloudinary.uploader.upload_large(
                audio_file,
                resource_type="video",  # Cloudinary treats audio as video
                folder="songs/",
                use_filename=True,
                unique_filename=False
            )

            song_data['audio_url'] = cloudinary_response.get('secure_url')
            song_data['duration'] = cloudinary_response.get('duration')  # if available
            song_data['bitrate'] = cloudinary_response['audio']['bit_rate']  # Optional, you can skip extracting locally
            song_data['audio_file'] = cloudinary_response.get('playback_url')  # Optional, you can skip extracting locally
            song_data['downloadable_link'] = cloudinary_response.get('secure_url')  # Optional, you can skip extracting locally
            song_data['title'] = cloudinary_response.get('original_filename')  # Optional, you can skip extracting locally

        except Exception as e:
            return create_response(success=False, message="Cloudinary upload failed", errors={"audio_file": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

        
        serializer = SongSerializer(data=song_data, context={'request': request})
        print(song_data)
        if serializer.is_valid():
            song = serializer.save()
            return create_response(success=True, message="Song uploaded successfully", data=SongSerializer(song).data, status_code=status.HTTP_201_CREATED)
        else:
            return create_response(success=False, message="Invalid song data", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        # Process audio file if provided
        

    # def post(self, request):
    #     serializer = SongSerializer(data=request.data, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return create_response(
    #             success=True,
    #             message="Song created successfully",
    #             data=serializer.data,
    #             status_code=status.HTTP_201_CREATED
    #         )
    #     return create_response(
    #         success=False,
    #         message="Song creation failed",
    #         errors=serializer.errors,
    #         status_code=status.HTTP_400_BAD_REQUEST
    #     )

class SongDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, pk, user):
        return get_object_or_404(Song, pk=pk, user=user)

    def get(self, request, pk):
        song = self.get_object(pk, request.user)
        serializer = SongSerializer(song, context={'request': request})
        return create_response(
            success=True,
            message="Song retrieved successfully",
            data=serializer.data
        )

    def patch(self, request, pk):
        song = self.get_object(pk, request.user)
        serializer = SongSerializer(song, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return create_response(
                success=True,
                message="Song updated successfully",
                data=serializer.data
            )
        return create_response(
            success=False,
            message="Song update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        # song = self.get_object(pk)
        song = Song.objects.get(id=pk)
        song.delete()
        return create_response(
            success=True,
            message="Song deleted successfully",
            status_code=status.HTTP_200_OK
        )

class PlaylistAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        playlists = Playlist.objects.filter(user=request.user)
        serializer = PlaylistSerializer(playlists, many=True, context={'request': request})
        return create_response(
            success=True,
            message="Playlists retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = PlaylistSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            playlist = serializer.save()
            
            # Handle song additions if provided
            song_ids = request.data.get('song_ids', [])
            for song_id in song_ids:
                try:
                    song = Song.objects.get(id=song_id, user=request.user)
                    playlist.songs.add(song)
                except Song.DoesNotExist:
                    pass
            
            return create_response(
                success=True,
                message="Playlist created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return create_response(
            success=False,
            message="Playlist creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class PlaylistDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, pk, user):
        return get_object_or_404(Playlist, pk=pk, user=user)

    def get(self, request, pk):
        playlist = self.get_object(pk, request.user)
        serializer = PlaylistSerializer(playlist, context={'request': request})
        return create_response(
            success=True,
            message="Playlist retrieved successfully",
            data=serializer.data
        )

    def patch(self, request, pk):
        playlist = self.get_object(pk, request.user)
        serializer = PlaylistSerializer(playlist, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return create_response(
                success=True,
                message="Playlist updated successfully",
                data=serializer.data
            )
        return create_response(
            success=False,
            message="Playlist update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        playlist = self.get_object(pk, request.user)
        playlist.delete()
        return create_response(
            success=True,
            message="Playlist deleted successfully",
            status_code=status.HTTP_200_OK
        )

    def post(self, request, pk):
        """Handle both adding and removing songs based on action parameter"""
        playlist = self.get_object(pk, request.user)
        song_id = request.data.get('song_id')
        action = request.data.get('action', 'add')  # Default to 'add' if not specified
        
        if not song_id:
            return create_response(
                success=False,
                message="Operation failed",
                errors={"song_id": ["This field is required"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            song = Song.objects.get(id=song_id, user=request.user)
            
            if action == 'add':
                if playlist.songs.filter(id=song_id).exists():
                    return create_response(
                        success=False,
                        message="Song addition failed",
                        errors={"song_id": ["Song already exists in playlist"]},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                playlist.songs.add(song)
                message = "Song added to playlist successfully"
                
            elif action == 'remove':
                if not playlist.songs.filter(id=song_id).exists():
                    return create_response(
                        success=False,
                        message="Song removal failed",
                        errors={"song_id": ["Song not in playlist"]},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                playlist.songs.remove(song)
                message = "Song removed from playlist successfully"
                
            else:
                return create_response(
                    success=False,
                    message="Operation failed",
                    errors={"action": ["Invalid action. Use 'add' or 'remove'"]},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            return create_response(
                success=True,
                message=message,
                data=PlaylistSerializer(playlist, context={'request': request}).data
            )
            
        except Song.DoesNotExist:
            return create_response(
                success=False,
                message="Operation failed",
                errors={"song_id": ["Song not found or doesn't belong to user"]},
                status_code=status.HTTP_404_NOT_FOUND
            )


class UnifiedSearch(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    Unified Search across Artists, Albums, Songs, and Playlists.
    """
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        result_type = request.query_params.get('type', '').strip().lower()

        if not query:
            return Response({'error': 'Query parameter "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        if result_type == 'artist' or result_type == '':
            artists = Artist.objects.filter(Q(name__icontains=query) | Q(country__icontains=query)).distinct()
            results += [{
                'type': 'artist',
                'data': ArtistSerializer(artist).data
            } for artist in artists]

        if result_type == 'album' or result_type == '':
            albums = Album.objects.filter(Q(title__icontains=query) | Q(genre__icontains=query)).distinct()
            results += [{
                'type': 'album',
                'data': AlbumSerializer(album).data
            } for album in albums]

        if result_type == 'song' or result_type == '':
            songs = Song.objects.filter(Q(title__icontains=query) | Q(genre__icontains=query) | Q(lyrics__icontains=query)).distinct()
            results += [{
                'type': 'song',
                'data': SongSerializer(song).data
            } for song in songs]

        if result_type == 'playlist' or result_type == '':
            playlists = Playlist.objects.filter(Q(name__icontains=query)).distinct()
            results += [{
                'type': 'playlist',
                'data': PlaylistSerializer(playlist).data
            } for playlist in playlists]

        
        print(results)
        return create_response(
            success=True,
            message='Search Results',
            data=results,
        )


class DiscoverSongsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            genre = request.query_params.get('genre', 'pop').lower()
            limit = min(int(request.query_params.get('limit', 20)), 100)  # Add max limit
            
            # First try to get from our database
            songs = Song.objects.filter(
                genre__iexact=genre, 
                user=request.user
            ).select_related('artist', 'album')[:limit]
            
            if songs.count() < limit:
                # If not enough, fetch from external API
                try:
                    data = fetch_jamendo_tracks(genre=genre, limit=limit)
                    if not data or not data.get('results'):
                        raise ValueError("No results from external API")
                    
                    new_songs = []
                    for track in data.get('results', []):
                        # Process artist
                        artist, _ = Artist.objects.get_or_create(
                            name=track['artist_name'],
                            user=request.user,
                            image=upload_external_file_to_cloudinary(track['image'], 'artist_art', 'image'),
                            defaults={
                                'country': track.get('artist_country', '')
                            }
                        )
                        
                        # Process album
                        album = None
                        if track.get('album_name'):
                            album, _ = Album.objects.get_or_create(
                                title=track['album_name'],
                                artist=artist,
                                user=request.user,
                                cover_image=upload_external_file_to_cloudinary(track['album_image'], 'cover_art', 'image'),
                                defaults={
                                    'release_date': track.get('releasedate', '2020-01-01'),
                                    'genre': track.get('musicinfo', {}).get('tags', {}).get('genres', ['Pop'])[0] if isinstance(track.get('musicinfo', {}).get('tags', {}), dict) else 'Pop'
                                }
                            )
                        
                        # Process song
                        song, created = Song.objects.get_or_create(
                            external_id=track['id'],
                            user=request.user,
                            source='jamendo',
                            defaults={
                                'title': track['name'],
                                'artist': artist,
                                'album': album,
                                'downloadable_link': track['audiodownload'] or track['audio'] or None,
                                'duration': timedelta(seconds=track['duration']),
                                'audio_url': track['audio'],
                                'audio_file': upload_external_file_to_cloudinary(track['audiodownload'], 'songs', 'auto') or upload_external_file_to_cloudinary(track['audio'], 'songs', 'auto') or None,
                                'art': upload_external_file_to_cloudinary(track['image'], 'song_art', 'image'),
                                'genre': track.get('musicinfo', {}).get('tags', {}).get('genres', ['Pop'])[0] if isinstance(track.get('musicinfo', {}).get('tags', {}), dict) else 'Pop',
                                'release_date': track.get('releasedate', '2020-01-01')
                            }
                        )
                        if created:
                            new_songs.append(song)
                    
                    # Get the updated queryset with prefetching
                    songs = Song.objects.filter(
                        user=request.user
                    ).select_related('artist', 'album').order_by("-date_added")[:limit]
                    
                except Exception as api_error:
                    # Log the error but continue with existing songs
                    import logging
                    logging.error(f"Failed to fetch from external API: {str(api_error)}")
            
            # Serialize with request context for absolute URLs
            serializer = SongSerializer(
                songs, 
                many=True,
                context={'request': request}  # Important for absolute URLs
            )
            
            return create_response(
                success=True,
                message="Songs discovered successfully",
                data=serializer.data
            )
            
        except Exception as e:
            return create_response(
                success=False,
                message=f"Error discovering songs: {str(e)}",
                data=[],
                status=400
            )