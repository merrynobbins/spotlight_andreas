from spotilight.model.Model import Model
from spotilight.ui.Router import Router
import xbmc
import sys
import xbmcplugin
import xbmcgui
from spotilight.ui.Paths import Paths

class UiHelper:
    
    DEFAULT_FOLDER_IMG = 'DefaultFolder.png'
    RUN_PLUGIN_SCRIPT = 'XBMC.RunPlugin(%s)'
    UPDATE_CONTAINER_SCRIPT = 'XBMC.Container.Update(%s)' 
    CONTENT_SONGS = 'songs'
    CONTENT_ALBUMS = 'albums'

    def __init__(self, list_item_factory):
        self.addon_handle = int(sys.argv[1])
        self.list_item_factory = list_item_factory
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_SONGS)
    
    def keyboardText(self, heading = 'Enter phrase'):
        keyboard = xbmc.Keyboard('', heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            return keyboard.getText()     
        
        return None
    
    def create_folder_item(self, title, url, image = DEFAULT_FOLDER_IMG):
        item = xbmcgui.ListItem(title, iconImage = image)
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_ALBUMS)
        
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, 
                                    url = url, listitem = item, 
                                    isFolder = True)       
         
    def create_list_of_playlists(self, playlists):
        for playlist in playlists:
            url = Router.url_for(Paths.GET_PLAYLIST, Model(name = playlist.name))
            self.create_folder_item(playlist.name, url)
            
        xbmcplugin.endOfDirectory(self.addon_handle)
         
    def create_list_of_tracks(self, tracks):
        self.create_track_list_items(tracks)
        
        xbmcplugin.endOfDirectory(self.addon_handle)
        
    def create_list_of_albums(self, albums):
        for album in albums:
            url = Router.url_for(Paths.ALBUM_TRACKS, Model(album = album.uri))
            self.create_folder_item('%s [%s]' % (album.name, album.year), url, album.image)
        
        xbmcplugin.endOfDirectory(self.addon_handle)

    def create_track_list_items(self, tracks):
        for index, track in enumerate(tracks):
            path, item = self.list_item_factory.create_list_item(track, index + 1)
            self.add_context_menu(track, path, item)
            
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url = path, listitem=item)            

    def add_context_menu(self, track, play_url, li):
        browse_album_url = Router.url_for(Paths.ALBUM_TRACKS, Model(album = track.album_uri))
        browse_artist_url = Router.url_for(Paths.ARTIST_ALBUMS, Model(track = track.uri))
        
        li.addContextMenuItems([('Queue item', UiHelper.RUN_PLUGIN_SCRIPT % play_url), 
                                ('Browse album...', UiHelper.UPDATE_CONTAINER_SCRIPT % browse_album_url), 
                                ('Browse artist...', UiHelper.UPDATE_CONTAINER_SCRIPT % browse_artist_url)])       
