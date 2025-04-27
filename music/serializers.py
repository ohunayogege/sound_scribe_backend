from rest_framework import serializers
from .models import Artist, Album, Song, Playlist
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User
import uuid


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        errors = []
        
        # Password match validation
        if data['password'] != data['confirm_password']:
            errors.append("Passwords don't match")
        
        # Email validation
        try:
            validate_email(data['email'])
        except ValidationError:
            errors.append("Enter a valid email address")
        
        if errors:
            raise serializers.ValidationError({"errors": errors})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email_or_username = data.get('login')
        password = data.get('password')
        errors = []
        
        if not email_or_username or not password:
            errors.append("Must include 'login' and 'password'")
            raise serializers.ValidationError({"errors": errors})
        
        # Try to authenticate with email
        user = authenticate(email=email_or_username, password=password)
        
        # If that fails, try with username
        if user is None:
            user = authenticate(username=email_or_username, password=password)
        
        if user:
            if not user.is_active:
                errors.append("User account is disabled")
                raise serializers.ValidationError({"errors": errors})
            data['user'] = user
        else:
            errors.append("Unable to login with provided credentials")
            raise serializers.ValidationError({"errors": errors})
        # user.last_login = ""
        # user.save()
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    cover_image_url = serializers.SerializerMethodField(read_only=True)
    songs = serializers.SerializerMethodField()  # For songs not in albums or all songs
    
    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ('id',)
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None
    
    def get_songs(self, obj):
        # Get all songs by this artist (through albums)
        songs = Song.objects.filter(album=obj)
        serializer = SongSerializer(songs, many=True, context=self.context)
        return serializer.data


class ArtistSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)
    songs = serializers.SerializerMethodField()  # For songs not in albums or all songs
    class Meta:
        model = Artist
        fields = '__all__'
        read_only_fields = ('id',)
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_songs(self, obj):
        # Get all songs by this artist (through albums)
        songs = Song.objects.filter(album__artist=obj)
        serializer = SongSerializer(songs, many=True, context=self.context)
        return serializer.data


class SongSerializer(serializers.ModelSerializer):
    album_title = serializers.CharField(source='album.title', read_only=True)
    artist_name = serializers.CharField(source='album.artist.name', read_only=True)
    art = serializers.SerializerMethodField()
    art = serializers.ImageField(required=False, allow_null=True)
    art_url = serializers.SerializerMethodField(read_only=True)
    audio_file = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(),
        required=False,
        allow_null=True
    )
    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Song
        fields = '__all__'
        read_only_fields = [
            'id', 'sample_rate',
            'channels', 'date_added', 'bpm'
        ]
    
    # def get_art(self, obj):
    #     if obj.art:
    #         return obj.art.url
    #     return None
    
    def get_art_url(self, obj):
        if obj.art:
            return obj.art.url
        return None
    
    def get_audio_file(self, obj):
        if obj.audio_file:
            return obj.audio_file.url  # Cloudinary URL
        return obj.audio_url  # Fallback external URL


class PlaylistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    
    class Meta:
        model = Playlist
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'user')
    
    def create(self, validated_data):
        # Get the current user from the request context
        user = self.context['request'].user
        songs_data = validated_data.pop('songs', [])
        
        playlist = Playlist.objects.create(user=user, **validated_data)
        playlist.songs.set(songs_data)
        return playlist