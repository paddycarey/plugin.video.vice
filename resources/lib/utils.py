#!/usr/bin/env python

import os
import re
import sys
import urllib
import urllib2

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from BeautifulSoup import BeautifulSoup

import StorageServer
from resources.lib import vice

### get addon info
__addon__             = xbmcaddon.Addon()
__addonid__           = __addon__.getAddonInfo('id')
__addonidint__        = int(sys.argv[1])
__addondir__          = xbmc.translatePath(__addon__.getAddonInfo('path'))
__cachedir__          = os.path.join(xbmc.translatePath(__addon__.getAddonInfo('profile')), 'subs')

# initialise cache object to speed up plugin operation
cache = StorageServer.StorageServer(__addonid__ + '-videodetails', 1)

class XBMCPlayer(xbmc.Player):
    def __init__( self, *args, **kwargs ):
        log( "#XBMCPlayer#")
        self.active = True
        self.result = False

    def onPlayBackPaused( self ):
        log("#Im paused#")
        
    def onPlayBackResumed( self ):
        log("#Im Resumed #")
        
    def onPlayBackStarted( self ):
        log( "#Playback Started#")
        self.active = True
        
    def onPlayBackEnded( self ):
        log("#Playback Ended#")
        self.active = False
        self.result = 'ended'
        
    def onPlayBackStopped( self ):
        log("## Playback Stopped ##")
        self.active = False
        self.result = 'stopped'

    def sleep(self, s):
        xbmc.sleep(s)

def getParams():
    
    """Parse and return the arguments passed to the addon in a usable form
    
    Returns:    param -- A dictionary containing the parameters which have been passed to the addon"""
    
    # initialise empty list to store params
    param=[]
    
    # store params as string
    paramstring=sys.argv[2]
    
    # check if params were provided
    if len(paramstring)>=2:
        
        # store params as string
        params=sys.argv[2]
        
        # remove ? from param string
        cleanedparams=params.replace('?','')
        
        # check if last argument is /
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        
        # split param string into individual params
        pairsofparams=cleanedparams.split('&')
        
        # initialise empty dict to store params
        param={}
        
        # loop through all params
        for i in range(len(pairsofparams)):
            
            # initialise empty dict to store split params
            splitparams={}
            
            # get name and value of param
            splitparams=pairsofparams[i].split('=')
            
            # check if param has value
            if (len(splitparams))==2:
                
                # add value to param dict
                param[splitparams[0]]=splitparams[1]
    
    # return dict of params
    return param


def convertSubs(sub_url):
    
    if not xbmcvfs.exists(__cachedir__):
        xbmcvfs.mkdir(os.path.split(__cachedir__)[0])
        xbmcvfs.mkdir(__cachedir__)
    
    sub_path = os.path.join(__cachedir__, sub_url.rsplit('/', 1)[1])
    sub_path_srt = sub_path + '.srt'
    
    if xbmcvfs.exists(sub_path):
        xbmcvfs.delete(sub_path)
    
    if not xbmcvfs.exists(sub_path_srt):
        sub_file = open(sub_path, "wb")
        response = urllib2.urlopen(sub_url)
        sub_file.write(response.read())
        sub_file.close()
        response.close()
    else:
        return sub_path_srt
    
    subs = open(sub_path, 'r').read()
    
    finalSubs = ""
    soup = BeautifulSoup(subs, convertEntities=BeautifulSoup.HTML_ENTITIES)
    engSub = soup.find('div', attrs={'xml:lang': 'en'})
    if engSub:
        engSubs = engSub.findAll('p')
        if engSubs:
            for i, line in enumerate(engSubs):
                tempSubArray = [0] * 4
                begin = line['begin'].replace(':', ' ').replace('.', ' ').split()
                dratn = line['dur'].replace(':', ' ').replace('.', ' ').split()
                begin.reverse()
                dratn.reverse()
                
                text = str(line.renderContents()).replace("<br />", "\\n").replace('\n', '').replace('\r', '')
                text = re.sub(' +',' ', text).replace('\\n ', '\\n')
                for n, cell in enumerate(begin):
                    calcTime = int(begin[n]) + int(dratn[n])
                    if n == 0 and calcTime > 1000:
                        calcTime -= 1000
                        tempSubArray[n+1] += 1
                    if (n == 1 or n == 2) and calcTime > 60:
                        calcTime -= 60
                        tempSubArray[n+1] += 1
                    tempSubArray[n] += calcTime
                    
                begin.reverse()
                tempSubArray.reverse()
                if tempSubArray[0] < 10:
                    tempSubArray[0] = "0" + str(tempSubArray[0])
                if tempSubArray[1] < 10:
                    tempSubArray[1] = "0" + str(tempSubArray[1])
                if tempSubArray[2] < 10:
                    tempSubArray[2] = "0" + str(tempSubArray[2])
                if tempSubArray[3] < 10:
                    tempSubArray[3] = "00" + str(tempSubArray[3])
                elif tempSubArray[3] < 100:
                    tempSubArray[3] = "0" + str(tempSubArray[3])
                curSubLine = str(i+1) + "\n" + str(begin[0]) + ":" + str(begin[1]) + ":" + str(begin[2]) + "," + str(begin[3]) + " --> "
                curSubLine += str(tempSubArray[0]) + ":" + str(tempSubArray[1]) + ":" + str(tempSubArray[2]) + "," + str(tempSubArray[3]) + "\n" + text + "\n\n"
                finalSubs += curSubLine
    
        sub_file = open(sub_path_srt, "wb")
        sub_file.write(finalSubs)
        sub_file.close()
            
    return sub_path_srt


def log(txt, severity=xbmc.LOGDEBUG):
    
    """Log txt to xbmc.log at specified severity
    
    Arguments:  txt -- A string containing the text to be logged
                severity -- Logging level to log text at (Default to LOGDEBUG)"""

    # generate log message from addon name and txt
    message = ('%s: %s' % (__addonid__, txt))
    
    # write message to xbmc.log
    xbmc.log(msg=message, level=severity)


def addVideo(linkName = '', episode_link = '', thumbPath = '', plot = ''):
    
    """Add a video to an XBMC directory listing
    
    Arguments:  linkName -- A string containg the name of the video
                episode_link -- A string containing the relative url to the video page (will be resolved later)
                thumbPath -- A string containg the url/path of the video's thumbnail image
                date -- a dataetime object containg the date of the video"""
    
    url = sys.argv[0] + "?episode_link=%s&episode_name=%s&episode_thumb=%s" % (episode_link, urllib.quote(linkName), urllib.quote(thumbPath))
    
    # initialise a listitem object to store video details
    li = xbmcgui.ListItem(linkName, iconImage = thumbPath, thumbnailImage = thumbPath)
    
    # set the video to playable
    li.setProperty("IsPlayable", 'false')
    
    # set the infolabels for the video
    li.setInfo( type="Video", infoLabels={ "title": linkName, "Plot": plot} )
    
    # set fanart image for video
    li.setProperty( "Fanart_Image", os.path.join(__addondir__, 'fanart.jpg'))
    
    # add listitem object to list
    xbmcplugin.addDirectoryItem(handle = __addonidint__, url = url, listitem = li, isFolder = False)


def addNext(page, show_link):
    
    """Add a 'Next Page' button to a directory listing
    
    Arguments:  page -- An Integer containing the number of the page to load on clicking the next page button"""
    
    # construct url of next page
    u = sys.argv[0] + "?page=%s&show_link=%s" % (str(page), show_link)
    
    # initialise listitem object
    li = xbmcgui.ListItem('Next Page', iconImage = "DefaultFolder.png", thumbnailImage = "DefaultFolder.png")
    
    # set title of list item
    li.setInfo( type = "Video", infoLabels = { "Title" : 'Next Page' })
    
    # set fanart image for video
    li.setProperty( "Fanart_Image", os.path.join(__addondir__, 'fanart.jpg'))
    
    # add listitem object to list
    xbmcplugin.addDirectoryItem(handle = __addonidint__, url = u, listitem = li, isFolder = True)


def addDir(title, thumbnail, url, description):
    
    """Add a 'Next Page' button to a directory listing
    
    Arguments:  page -- An Integer containing the number of the page to load on clicking the next page button"""

    # construct url of next page
    u = sys.argv[0] + "?page=1&show_link=%s" % url

    # initialise listitem object
    li = xbmcgui.ListItem(title, iconImage = thumbnail, thumbnailImage = thumbnail)
    
    # set title of list item
    li.setInfo( type = "Video", infoLabels = { "Title" : 'Next Page', "Plot": description })
    
    # set fanart image for video
    li.setProperty( "Fanart_Image", os.path.join(__addondir__, 'fanart.jpg'))
    
    # add listitem object to list
    xbmcplugin.addDirectoryItem(handle = __addonidint__, url = u, listitem = li, isFolder = True)


def endDir():
    
    """Tell XBMC we have finished adding items to the directory list"""
    
    xbmcplugin.endOfDirectory(handle = __addonidint__)


def playVideo(episode_link, episode_name, episode_thumb):
    
    """Resolve the provided url and play video"""
        
    if re.search(r'-1$', episode_link):
        log('Multipart video found: %s' % episode_link)
        episode_link = episode_link.rstrip('123456789')
        
        for i in range(1,100):

            player = XBMCPlayer(xbmc.PLAYER_CORE_DVDPLAYER)

            # call getVideoUrl to resolve url for playback
            videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))
    
            # set success to true if video found
            if videoUrl == []:
                
                if episode_link.startswith('/the-'):
                
                    break

                else:
                    
                    episode_link = '/' + episode_link.split('/')[1] + '/' + 'the-' + episode_link.split('/')[2]
                
                    # call getVideoUrl to resolve url for playback
                    videoUrl = cache.cacheFunction(vice.get_video_details, episode_link + str(i))
            
            log('Video Details: %s' % str(videoUrl))
                
            if not videoUrl == [] and videoUrl['vid_url']:
                
                listitem = xbmcgui.ListItem(episode_name, iconImage = episode_thumb, thumbnailImage = episode_thumb)
                listitem.setInfo('video', {'Title': episode_name})
                player.play(videoUrl['vid_url'], listitem)
    
                while not player.isPlaying():
                    player.sleep(100)
                
                player.setSubtitles(convertSubs(videoUrl['sub_url']))

                while player.active:
                    player.sleep(100)
            
                while not player.result:
                    player.sleep(100)
                
                if player.result == 'stopped':
                    break
    
            else:
                
                break

    else:
        
        videoUrl = cache.cacheFunction(vice.get_video_details, episode_link)
        
        player = XBMCPlayer(xbmc.PLAYER_CORE_DVDPLAYER)

        if videoUrl['vid_url']:
                
            listitem = xbmcgui.ListItem(episode_name, iconImage = episode_thumb, thumbnailImage = episode_thumb)
            listitem.setInfo('video', {'Title': episode_name})
            player.play(videoUrl['vid_url'], listitem)
            
            while not player.isPlaying():
                player.sleep(100)
                
            player.setSubtitles(convertSubs(videoUrl['sub_url']))

