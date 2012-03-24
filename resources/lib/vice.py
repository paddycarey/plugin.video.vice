# import required modules
import urllib2
import re
from BeautifulSoup import BeautifulSoup
from urllib2 import HTTPError


def get_remote_data(url):
    
    """Retrieve and return remote resource as string
    
    Arguments:  url -- A string containing the url of a remote page to retrieve
    Returns:    data -- A string containing the contents to the remote page"""

    # Build the page request including setting the User Agent
    req  = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')

    # connect to url using urlopen
    client = urllib2.urlopen(req)
    
    # read data from page
    data = client.read()
    
    # close connection to url
    client.close()
    
    # return the retrieved data
    return data


def get_video_details(episode_link):
    
    """Retrieve video url and subtitle url for a given episode_link"""
    
    # generate video url
    episode_page = 'http://www.vice.com%s' % episode_link
    
    # declare empty dict to store results
    results = {}
    
    try:
        
        # retrieve and parse episode page
        soup = BeautifulSoup(get_remote_data(episode_page))
    
    except:
        
        utils.log('Error retrieving video details from %s' % episode_link)
        # return empty string on httperrorr
        return ''
    
    # find url of html5 player
    js_player_url = soup.find('div', 'video_area').script['src']
    
    try:
        
        # retrieve and parse html5 player
        jsplayer = get_remote_data(js_player_url)
    
    except:
        
        utils.log('Error retrieving video details from %s' % episode_link)
        # return empty string on httperror
        return ''

    # compile regex to find link to mobile player
    mp_regex = re.compile("mobile_player_url=([^\+]*)")
    
    # get mobile player url
    mobile_player_url = mp_regex.findall(jsplayer)[0].lstrip('\"').rstrip('\"')

    try:
    
        # retrieve mobile player url
        mobile_player = get_remote_data(mobile_player_url + 'ipad').replace('\\\"', '\"')
    
    except:
        
        utils.log('Error retrieving video details from %s' % episode_link)
        # return empty string on error
        return ''

    # compile regex to find video url
    vid_regex = re.compile("ipad_url\\\":\\\"([^\"]*)\"")
    
    # find video url
    vid_url = vid_regex.findall(mobile_player)[0].replace('\\u0026', '&')

    # compile regex to find sub url
    sub_regex = re.compile("closed_caption_url\\\":\\\"([^\"]*)\"")
    
    # find sub url
    sub_url = sub_regex.findall(mobile_player)[0]
    
    # add results to dictionary
    results['vid_url'] = vid_url
    results['sub_url'] = sub_url
    
    # return dictionary of urls
    return results


def get_episodes(show_link = '', page_number = 1):
    
    if not show_link == '':
        show_page = 'http://www.vice.com%s?Article_page=%s' % (show_link, str(page_number))
    else:
        show_page = 'http://www.vice.com/shows'
    
    try:
        
        soup = BeautifulSoup(get_remote_data(show_page))
    
    except HTTPError:
        
        return ''
    
    episode_list = soup.find('ul', 'story_list').findAll('li')
    
    episodes = []
    
    for episode in episode_list:
        
        episode_details = {}
        
        episode_details['link'] = episode.a['href']
        episode_details['thumb'] = episode.a.img['src']
        episode_details['title'] = episode.h2.a.string
        episode_details['description'] = episode.p.string.lstrip().rstrip()
        
        episodes.append(episode_details)

    return episodes


# produce some test output when module run standalone
if __name__ == '__main__':

    print get_episodes()
    print get_episodes('/vice-music-specials', 1)
    print get_video_details('/vice-special/abel-ferraras-pizza-connection-episode-1')
