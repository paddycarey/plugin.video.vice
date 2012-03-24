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
    
    episode_page = 'http://www.vice.com%s' % episode_link
    
    results = {}
    
    try:
        
        soup = BeautifulSoup(get_remote_data(episode_page))
    
    except HTTPError:
        
        return ''
    
    js_player_url = soup.find('div', 'video_area').script['src']
    
    try:
        
        jsplayer = get_remote_data(js_player_url)
    
    except HTTPError:
        
        return ''

    mp_regex = re.compile("mobile_player_url=([^\+]*)")
    
    mobile_player_url = mp_regex.findall(jsplayer)[0].lstrip('\"').rstrip('\"')

    try:
    
        mobile_player = get_remote_data(mobile_player_url + 'ipad').replace('\\\"', '\"')
    
    except HTTPError:
        
        return ''

    vid_regex = re.compile("ipad_url\\\":\\\"([^\"]*)\"")
    
    vid_url = vid_regex.findall(mobile_player)[0].replace('\\u0026', '&')

    sub_regex = re.compile("closed_caption_url\\\":\\\"([^\"]*)\"")
    
    sub_url = sub_regex.findall(mobile_player)[0]
        
    results['vid_url'] = vid_url
    results['sub_url'] = sub_url
    
    return results


def get_episodes(show_link, page_number):
    
    show_page = 'http://www.vice.com%s?Article_page=%s' % (show_link, str(page_number))
    
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


def get_shows():
    
    show_page = 'http://www.vice.com/shows'
    
    soup = BeautifulSoup(get_remote_data(show_page))
    
    show_list = soup.find('ul', 'story_list').findAll('li')
    
    shows = []
    
    for show in show_list:
        
        show_details = {}
        
        show_details['link'] = show.a['href']
        show_details['thumb'] = show.a.img['src']
        show_details['title'] = show.h2.a.string
        show_details['description'] = show.p.string.lstrip().rstrip()
        
        shows.append(show_details)

    return shows

if __name__ == '__main__':

    print get_video_url('/vice-special/abel-ferraras-pizza-connection-episode-1')
