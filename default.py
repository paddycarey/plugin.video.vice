import urllib
import sys
import StorageServer
import xbmcaddon

from resources.lib import vice
from resources.lib import utils

### get addon info
__addon__             = xbmcaddon.Addon()
__addonid__           = __addon__.getAddonInfo('id')
__addonidint__        = int(sys.argv[1])

# initialise cache object to speed up plugin operation
cache = StorageServer.StorageServer(__addonid__ + 'pages', 1)

class Main:

    def __init__(self):

        # parse script arguments
        params = utils.getParams()

        # Check if the url param exists
        try:
            
            show_link=urllib.unquote_plus(params["show_link"])
            utils.log('Show Found: %s' % show_link)
            
            # Get the current page number
            pageNum = int(params["page"])
            utils.log('Page Found: %s' % pageNum)
            
        except:

            try:
                
                episode_name=urllib.unquote_plus(params["episode_name"])
                utils.log('Episode Name Found: %s' % episode_name)
                
                episode_link=urllib.unquote_plus(params["episode_link"])
                utils.log('Episode Link Found: %s' % episode_link)
                
                episode_thumb=urllib.unquote_plus(params["episode_thumb"])
                utils.log('Episode Thumb Found: %s' % episode_thumb)
            
            except:
                
                utils.log('Browsing all shows')
                for show in cache.cacheFunction(vice.get_shows):
                    
                    utils.addDir(show['title'], show['thumb'], show['link'], show['description'])

                # We're done with the directory listing
                utils.endDir()
                    
            else:
                
                utils.log('Playing episode: %s' % episode_link)
                utils.playVideo(episode_link, episode_name, episode_thumb)
        
        else:
            
            utils.log('Browsing episodes for: %s' % show_link)
            #for episode in cache.cacheFunction(vice.get_episodes, show_link, pageNum):
            for episode in vice.get_episodes(show_link, pageNum):
                    
                utils.addVideo(episode['title'], episode['link'], episode['thumb'], episode['description'])

            utils.addNext(pageNum + 1, show_link)
            
            # We're done with the directory listing
            utils.endDir()
            

if __name__ == '__main__':
    
    # Main program
    Main()
        
