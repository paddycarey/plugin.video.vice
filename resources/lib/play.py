import re
import xbmc
import xbmcaddon
import xbmcgui
import StorageServer

from resources.lib import vice
from resources.lib import utils

### get addon info
__addon__             = xbmcaddon.Addon()
__addonid__           = __addon__.getAddonInfo('id')

# initialise cache object to speed up plugin operation
cache = StorageServer.StorageServer(__addonid__ + '-videodetails', 1)

pDialog = xbmcgui.DialogProgress()

class XBMCPlayer(xbmc.Player):
    def __init__( self, *args, **kwargs ):
        utils.log( "Player initialised")
        self.active = True
        self.result = False

    def onPlayBackPaused( self ):
        utils.log("Player paused")
        
    def onPlayBackResumed( self ):
        utils.log("Player resumed")
        
    def onPlayBackStarted( self ):
        utils.log( "Playback started")
        self.active = True
        pDialog.close()
        
    def onPlayBackEnded( self ):
        utils.log("Playback ended")
        self.active = False
        self.result = 'ended'
        
    def onPlayBackStopped( self ):
        utils.log("Playback stopped")
        self.active = False
        self.result = 'stopped'

    def sleep(self, s):
        xbmc.sleep(s)
        
def play_episode(episode_link, episode_name, episode_thumb):
    
    """Resolve the provided url and play video"""
        
    if re.search(r'-1$', episode_link):
        utils.log('Multipart video found: %s' % episode_link)
        episode_link = episode_link.rstrip('123456789')
        
        for i in range(1,100):

            player = XBMCPlayer(xbmc.PLAYER_CORE_DVDPLAYER)

            ret = pDialog.create('Vice.com', 'Checking for stream...')

            # call getVideoUrl to resolve url for playback
            videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))
    
            # set success to true if video found
            if videoUrl == []:
                
                if episode_link.startswith('/the-'):
                    
                    pDialog.close()
                    break

                else:
                    
                    episode_link = '/' + episode_link.split('/')[1] + '/' + 'the-' + episode_link.split('/')[2]
                
                    # call getVideoUrl to resolve url for playback
                    videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))
            
            utils.log('Video Details: %s' % str(videoUrl))
            
            pDialog.update(50, 'Loading stream...')
            
            if not play_video(videoUrl, episode_name, episode_thumb):
                break

    else:
        
        ret = pDialog.create('Vice.com', 'Loading stream...')
        
        videoUrl = cache.cacheFunction(vice.get_video_details, episode_link)
        
        play_video(videoUrl, episode_name, episode_thumb)
        


def play_video(videoUrl, episode_name, episode_thumb):
    
        player = XBMCPlayer(xbmc.PLAYER_CORE_DVDPLAYER)

        if not videoUrl == [] and videoUrl['vid_url']:
            
            listitem = xbmcgui.ListItem(episode_name, iconImage = episode_thumb, thumbnailImage = episode_thumb)
            listitem.setInfo('video', {'Title': episode_name})
            player.play(videoUrl['vid_url'], listitem)

            while not player.isPlaying():
                player.sleep(100)
            
            player.setSubtitles(utils.convertSubs(videoUrl['sub_url']))

            while player.active:
                player.sleep(100)
        
            while not player.result:
                player.sleep(100)
            
            if player.result == 'stopped':
                return False
            else:
                return True
                
        else:
            
            pDialog.close()
            return False
