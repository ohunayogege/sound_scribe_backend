from datetime import timedelta
from django.db import models
from pydub import AudioSegment
import librosa
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import uuid
import numpy as np
from cloudinary.models import CloudinaryField

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    last_login = models.DateTimeField(auto_now=True)
    
    # Remove username field and use email as username
    username = models.CharField(max_length=150, unique=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()  # <-- Required
    
    def save(self, *args, **kwargs):
        # Generate username from email if not provided
        if not self.username:
            self.username = self.email.split('@')[0]
        self.email = self.email.lower()
        self.username = self.username.lower()
        super().save(*args, **kwargs)

class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    image = CloudinaryField(default='', null=True, blank=True, folder='artist_art/')
    
    def __str__(self):
        return self.name

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    release_date = models.DateField()
    cover_image = CloudinaryField(default='', null=True, blank=True, folder='cover_art/')
    genre = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs', null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs', null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    audio_file = CloudinaryField(
        resource_type='video',  # Automatically detects audio/video
        folder='songs/',      # Stores files in 'songs/' directory on Cloudinary
        null=True,
        blank=True
    )
    audio_url = models.URLField(blank=True)  # For streaming from external source
    track_number = models.PositiveIntegerField(null=True, blank=True)
    art = CloudinaryField(resource_type='image', default='', null=True, blank=True, folder='song_art/')
    # art = models.ImageField(upload_to='songs_art/', blank=True, null=True, default='')
    genre = models.CharField(max_length=100, blank=True)
    release_date = models.DateField(null=True, blank=True)
    bpm = models.PositiveIntegerField(null=True, blank=True)
    downloadable_link=models.URLField(default='')
    external_id = models.CharField(max_length=100, blank=True)  # ID from external API
    source = models.CharField(max_length=50, blank=True)  # 'jamendo', 'deezer', etc.
    lyrics = models.TextField(blank=True)
    is_explicit = models.BooleanField(default=False)
    
    # Audio metadata
    bitrate = models.PositiveIntegerField(null=True, blank=True)
    sample_rate = models.PositiveIntegerField(null=True, blank=True)
    channels = models.PositiveSmallIntegerField(default=2)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} by {self.artist.name if self.artist else 'Unknown'}"
    
    def extract_metadata(self):
        if self.audio_file:
            try:
                audio = AudioSegment.from_file(self.audio_file.path)
                self.duration = timedelta(milliseconds=len(audio))
                # self.bitrate = audio.frame_rate
                # self.channels = audio.channels
                
                # Advanced features with librosa
                y, sr = librosa.load(self.audio_file.path)
                self.bpm = librosa.beat.tempo(y=y, sr=sr)[0]
                self.save()
                return True
            except Exception as e:
                print(f"Error processing audio: {e}")
                return False
        return False

class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True, blank=True)
    songs = models.ManyToManyField(Song)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
