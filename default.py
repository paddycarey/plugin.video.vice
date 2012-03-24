# import required modules
import urllib
import sys
import StorageServer
import xbmcaddon

from resources.lib import vice
from resources.lib import play
from resources.lib import utils

### get addon info
__addon__             = xbmcaddon.Addon()
__addonid__           = __addon__.getAddonInfo('id')
__addonidint__        = int(sys.argv[1])

# initialise cache object to speed up plugin operation
cache = StorageServer.StorageServer(__addonid__, 1)

class Main:

    def __init__(self):

        # parse script arguments
        params = utils.getParams()

        try:
            
            # Check if the show_link param exists
            show_link=urllib.unquote_plus(params["show_link"])
            utils.log('Show Found: %s' % show_link)
            
            # Get the current page number
            pageNum = int(params["page"])
            utils.log('Page Found: %s' % pageNum)
            
        except:

            try:
                
                # Check if the episode_name param exists
                episode_name=urllib.unquote_plus(params["episode_name"])
                utils.log('Episode Name Found: %s' % episode_name)
                
                # Check if the episode_link param exists
                episode_link=urllib.unquote_plus(params["episode_link"])
                utils.log('Episode Link Found: %s' % episode_link)
                
                # Check if the episode_thumb param exists
                episode_thumb=urllib.unquote_plus(params["episode_thumb"])
                utils.log('Episode Thumb Found: %s' % episode_thumb)
            
            except:
                
                # Browse all shows
                utils.log('Browsing all shows')
                for show in cache.cacheFunction(vice.get_episodes):
                    
                    # add show to directory listing
                    utils.addDir(show['title'], show['thumb'], show['link'], show['description'])

                # We're done with the directory listing
                utils.endDir()
                    
            else:
                
                # play episode
                utils.log('Playing episode: %s' % episode_link)
                play.play_episode(episode_link, episode_name, episode_thumb)
        
        else:
            
            # browse all episodes for show_link 
            utils.log('Browsing episodes for: %s' % show_link)
            for episode in cache.cacheFunction(vice.get_episodes, show_link, pageNum):
                    
                utils.addVideo(episode['title'], episode['link'], episode['thumb'], episode['description'])

            # add next page item
            utils.addNext(pageNum + 1, show_link)
            
            # We're done with the directory listing
            utils.endDir()
            

if __name__ == '__main__':
    
    # Main program
    Main()
        
