from django.urls import re_path as path
from .views import (
    ArtistAPIView, ArtistDetailAPIView,
    AlbumAPIView, AlbumDetailAPIView,
    SongAPIView, SongDetailAPIView,
    PlaylistAPIView, PlaylistDetailAPIView, UnifiedSearch,
    DiscoverSongsAPIView, UserLoginAPIView, UserProfile, UserRegistrationAPIView, FetchSongTag
)

urlpatterns = [

    path(r'^register/$', UserRegistrationAPIView.as_view(), name='register'),
    path(r'^login/$', UserLoginAPIView.as_view(), name='login'),
    path(r'^profile/$', UserProfile.as_view(), name='login'),
    
    # Artists
    path(r'^artists/$', ArtistAPIView.as_view(), name='artist-list'),
    path(r'^artists/(?P<pk>[\w-]+)/$', ArtistDetailAPIView.as_view(), name='artist-detail'),
    
    # Albums
    path(r'^albums/$', AlbumAPIView.as_view(), name='album-list'),
    path(r'^albums/(?P<pk>[\w-]+)/$', AlbumDetailAPIView.as_view(), name='album-detail'),
    
    # Songs
    path(r'^fetch-song-tag/$', FetchSongTag.as_view(), name='song-tag'),
    path(r'^songs/$', SongAPIView.as_view(), name='song-list'),
    path(r'^songs/(?P<pk>[\w-]+)/$', SongDetailAPIView.as_view(), name='song-detail'),
    
    # Playlists
    path(r'^playlists/$', PlaylistAPIView.as_view(), name='playlist-list'),
    path(r'^playlists/(?P<pk>[\w-]+)/$', PlaylistDetailAPIView.as_view(), name='playlist-detail'),
    path(r'^playlists/(?P<pk>[\w-]+)/add_song/$', PlaylistDetailAPIView.as_view(), name='playlist-add-song'),
    path(r'^playlists/(?P<pk>[\w-]+)/remove_song/', PlaylistDetailAPIView.as_view(), name='playlist-remove-song'),
    
    # Discovery
    path(r'^discover/$', DiscoverSongsAPIView.as_view(), name='discover-songs'),
    path(r'^search/$', UnifiedSearch.as_view(), name='search-all'),
]