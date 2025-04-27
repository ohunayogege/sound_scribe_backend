from django.contrib import admin
from .models import Artist, Album, Song, Playlist, User

class SongInline(admin.TabularInline):
    model = Song
    extra = 1

# class UserAdmin(admin.TabularInline):
#     filter_horizontal = ('email','user_id',)

class AlbumAdmin(admin.ModelAdmin):
    inlines = [SongInline]

class PlaylistAdmin(admin.ModelAdmin):
    filter_horizontal = ('songs',)

admin.site.register(Artist)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(User)