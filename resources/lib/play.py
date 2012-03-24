# import required modules
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
cache = StorageServer.StorageServer(__addonid__, 1)

# initialise progress dialog
pDialog = xbmcgui.DialogProgress()

class XBMCPlayer(xbmc.Player):
    
    """Custom xbmc.Player class to perform custom action on finished playing"""
    
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
    
    """Resolve the provided url, detect if multipart and play video"""
    
    # check if video is multipart
    if re.search(r'-1$', episode_link):
        
        utils.log('Multipart video found: %s' % episode_link)
        
        # strip segment number from episode_link
        episode_link = episode_link.rstrip('123456789')
        
        # loop over ints starting at 1
        for i in range(1,100):

            # create progress dialog
            ret = pDialog.create('Vice.com', 'Checking for stream...')

            utils.log('Checking for stream: %s' % episode_link + str(i))

            # call get_video_details to resolve url for playback and get sub url
            videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))
    
            # check if was able to find video url
            if videoUrl == []:
                
                # workaround for situations where multipart videos do not all conform to the same pattern e.g. "The VICE Guide to Belfast"
                if episode_link.endswith('1-'):

                    # remove '1-' from end of link
                    episode_link = episode_link.replace('1-', '')
                    
                    utils.log('Checking for stream: %s' % episode_link + str(i))
                    
                    # call get_video_details to resolve url for playback
                    videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))

                elif episode_link.split('/')[2].startswith('the-'):
                    
                    # close dialog and exit if no more parts found
                    pDialog.close()
                    break

                else:
                    
                    # add '/the' to start of episode name
                    episode_link = '/' + episode_link.split('/')[1] + '/' + 'the-' + episode_link.split('/')[2]

                    utils.log('Checking for stream: %s' % episode_link + str(i))

                    # call get_video_details to resolve url for playback
                    videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))
            
            # log found video details
            utils.log('Video Details: %s' % str(videoUrl))
            
            # update progress dialog
            pDialog.update(50, 'Loading stream...')

            utils.log('Loading stream: %s' % episode_link + str(i))

            # play video
            if not play_video(videoUrl, episode_name, episode_thumb):
                
                # exit if user stops playing or no video present
                break

    else:
        
        # create progress dialog
        ret = pDialog.create('Vice.com', 'Loading stream...')
        
        utils.log('Loading stream: %s' % episode_link)
        
        # call get_video_details to resolve url for playback
        videoUrl = cache.cacheFunction(vice.get_video_details, episode_link)
        
        # play video
        play_video(videoUrl, episode_name, episode_thumb)
        


def play_video(videoUrl, episode_name, episode_thumb):
    
        """Play video with player"""
    
        # initialise player
        player = XBMCPlayer(xbmc.PLAYER_CORE_DVDPLAYER)
        
        # check if video url is present
        if not videoUrl == [] and videoUrl['vid_url']:
    
            # construct listitem to pass to player
            listitem = xbmcgui.ListItem(episode_name, iconImage = episode_thumb, thumbnailImage = episode_thumb)
            listitem.setInfo('video', {'Title': episode_name})
            
            # play video
            player.play(videoUrl['vid_url'], listitem)

            # wait until player begins playing
            while not player.isPlaying():
                player.sleep(100)
            
            try:
            
                # retrieve and enable captions
                player.setSubtitles(utils.convertSubs(videoUrl['sub_url']))
            
            except:
                
                utils.log('Unable to load subtitles')

            # wait for player to finish
            while player.active:
                player.sleep(100)
        
            # wait for player.result to be True
            while not player.result:
                player.sleep(100)
            
            # check if video was stopped or ended
            if player.result == 'stopped':
                
                # return false if stopped
                return False
                
            else:
                
                # return true if video ended normally
                return True
                
        else:
            
            # close dialog and return false
            pDialog.close()
            return False
