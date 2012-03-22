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


def get_video_url(episode_link):

    # Create a new soup instance and assign a video list html to a variable
    
    episode_page = 'http://www.vice.com%s' % episode_link
    
    try:
        
        soup = BeautifulSoup(get_remote_data(episode_page))
    
    except HTTPError:
        
        return None
    
    js_player_url = soup.find('div', 'video_area').script['src']
    
    try:
        
        jsplayer = get_remote_data(js_player_url)
    
    except HTTPError:
        
        return None

    mp_regex = re.compile("mobile_player_url=([^\+]*)")
    
    mobile_player_url = mp_regex.findall(jsplayer)[0].lstrip('\"').rstrip('\"')

    try:
    
        mobile_player = get_remote_data(mobile_player_url + 'ipad').replace('\\\"', '\"')
    
    except HTTPError:
        
        return None

    vid_regex = re.compile("ipad_url\\\":\\\"([^\"]*)\"")
    
    vid_url = vid_regex.findall(mobile_player)[0].replace('\\u0026', '&')
    
    return vid_url


def get_episodes(show_link, page_number):
    
    show_page = 'http://www.vice.com%s?Article_page=%s' % (show_link, str(page_number))
    
    soup = BeautifulSoup(get_remote_data(show_page))
    
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
        
        #print get_shows()
        #print get_episodes('/americana', 1)
        print get_video_url('/hamiltons-pharmacopeia/hamilton-and-the-philosophers-stone-part-3')
