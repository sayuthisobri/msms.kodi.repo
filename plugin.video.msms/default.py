import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string, sys, os
import commonresolvers
import urlresolver
import json
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from htmlentitydefs import name2codepoint as n2cp
import HTMLParser

try:
        from sqlite3 import dbapi2 as sqlite
        print "Loading sqlite3 as DB engine"
except:
        from pysqlite2 import dbapi2 as sqlite
        print "Loading pysqlite2 as DB engine"
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
dialog = xbmcgui.Dialog()
addon_id = 'plugin.video.msms'
plugin = xbmcaddon.Addon(id=addon_id)
#DB = os.path.join(xbmc.translatePath("special://database"), 'dfv.db')
BASE_URL = 'http://v2.msms.cf'
V2_URL = BASE_URL + '/malay/v2'
net = Net()
addon = Addon(addon_id, sys.argv)

###### PATHS ###########
AddonPath = addon.get_path()
IconPath = AddonPath + "/icons/"
FanartPath = AddonPath + "/icons/"

##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
link = addon.queries.get('link', None)
linkType = addon.queries.get('linkType', None)
content = addon.queries.get('content', None)
query = addon.queries.get('query', None)
startPage = addon.queries.get('startPage', None)
numOfPages = addon.queries.get('numOfPages', None)
listitem = addon.queries.get('listitem', None)
urlList = addon.queries.get('urlList', None)
section = addon.queries.get('section', 'ALL')
image = addon.queries.get('image', None)

def GetDomain(url,friendlyName = True):
    tmp = re.compile('//(.+?)/').findall(url)
    domain = 'Unknown'
    if len(tmp) > 0 :
        domain = tmp[0].replace('www.', '')
    return domain

###################################################################### menus ####################################################################################################

def MainMenu():    #homescreen
    addon.add_directory({'mode': 'Menu1'}, {'title':  '[COLOR cyan]Browse[/COLOR] >>'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
    # listitem = xbmcgui.ListItem()
    # listitem.setInfo('video',{'Title': 'test play'})
    addon.add_directory({'mode': 'GetSearchQuery', 'url': V2_URL}, {'title':  '[COLOR cyan]Search[/COLOR] >>'}, img=IconPath + 'search.png', fanart=FanartPath + 'fanart.png')
    #addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR red]Resolver Settings[/COLOR]'}, img=IconPath + 'resolver.png', fanart=FanartPath + 'fanart.png')       
    xbmcplugin.endOfDirectory(_handle)

def Menu1():
    category = ['Filem', 'Telemovie', 'Drama', 'TvShow', 'Klasik', 'Indonesia', 'All']
    url = V2_URL + '/list'
    for item in category:
        itemUrl = url + '?'
        if item != 'All':
            itemUrl += 'category=' + item
        addon.add_directory({'mode': 'HandleUrl', 'section': 'ALL', 'url': itemUrl,
                             'startPage': '1', 'numOfPages': '1'}, {'title':  '[COLOR {0}]{1}[/COLOR]'.format('blue' if item=='All' else 'white',item)}, img=IconPath + 'video.png', fanart=FanartPath + 'screens.jpg')
    xbmcplugin.endOfDirectory(_handle)

def HandleContent(obj=None, link=False, linkType=False, mode='All'):
    links = []
    if linkType != 'direct_play':
        obj = json.loads(obj)
        links = obj['links']
        if not linkType:
            linkType = obj.get('type',False)
    source = None
    addon.log(msg= link)
    if linkType:
        if len(links)>1:
            # arr = [link['text'] for link in links]
            # index = dialog.select("Please choose:", arr)
            # if index > -1:
            #     addon.log(msg= str(index) + ' enter')
            #     link = links[index]
            for link in links:
                addon.add_item({'mode': 'HandleContent', 'content': 'false', 'link': link['link'], 'linkType': 'direct_play' }, {'title':  link['text']}, img=IconPath + 'video.png', fanart=FanartPath + 'screens.jpg')
            addon.end_of_directory()
        elif len(links)==1:
            index = 0
            link = links[0]
        # if link and index > -1:
        if link:
            # notify(str(index) + ' - ' + link['link'])
            if linkType != 'direct_play':
                link = link['link']
            HandleUrl(link)
    else:
        mediaSrcs = []
        for link in links:
            mediaSrcs.append(urlresolver.HostedMediaFile(url=link,title=GetDomain(link), include_universal=True))
        source = urlresolver.choose_source(mediaSrcs)
        try:            
            if source:
                stream_url = source.resolve()
                # stream_url = commonresolvers.get(url).result
            if stream_url:
                return addon.resolve_url(stream_url)
            
        except:
            e = sys.exc_info()[0]
            if source:
                notify(msg='[COLOR red]Sorry, Can\'t play from this source![/COLOR]')

def HandleContentList(obj):
    obj = json.loads(obj)
    links = obj['links']
    linkType = obj.get('type',False)
    link = False
    source = None
    if linkType:
        if len(links)>1:
            # arr = [link['text'] for link in links]
            for link in links:
                addon.add_directory({'mode': 'HandleUrl', 'url': link['link']}, {'title': link['text'] }, img=IconPath + 'video.png', fanart=FanartPath + 'screens.jpg')
            # index = dialog.select("Please choose:", arr)
            # if index > -1:
                # addon.log(msg= str(index) + ' enter')
                # link = links[index]
            addon.endOfDirectory()
        elif len(links)==1 and links[0]:
            HandleUrl(links[0]['link'])
            # index = 0
            # link = links[0]
        # if link and index > -1:
            # notify(str(index) + ' - ' + link['link'])
            # link = link['link']
            # HandleUrl(link)
    else:
        mediaSrcs = []
        for link in links:
            mediaSrcs.append(urlresolver.HostedMediaFile(url=link,title=GetDomain(link)))
        source = urlresolver.choose_source(mediaSrcs)
        try:            
            if source:
                stream_url = source.resolve()
                # stream_url = commonresolvers.get(url).result
            if stream_url:
                xbmc.Player().play(stream_url)
        except:
            e = sys.exc_info()[0]
            if source:
                notify(msg='[COLOR red]Sorry, Can\'t play from this source![/COLOR]')

def HandleUrl(url, page = '1'):
    url = SetQuery(url,'page',str(page))
    # notify('page: ' + page)
    addon.log('Handle: ' + str(url) + ' : ')
    if re.search('msms\.cf',url):
        data=json.loads(net.http_GET(url).content.encode('utf-8'))
        if data:
            entries = data.get('entry', [])
            itemType = False
            for item in entries:
                itemType = item.get('type', False)
                if itemType:
                    addon.add_directory({'mode': 'HandleContent', 'section': 'ALL', 'content': json.dumps(item).encode('utf-8')}, {'title':  item['title']}, img=item['image'], fanart=item.get('image',FanartPath + 'fanart.png'), is_folder=True)
                else:
                    HandleContent(json.dumps(item))
            if itemType and hasNextPage(data):
                nextPage = str(int(page)+1)
                addon.add_directory({'mode': 'HandleUrl', 'section': 'ALL', 'url': url, 'startPage': nextPage}, {'title':  '[COLOR blue]Next (Page {0})[/COLOR]'.format(nextPage)}, img=IconPath + 'next.png', fanart=item.get('image',FanartPath + 'fanart.png'))

def hasNextPage(obj):
    return obj and int(obj.get('totalResults','0'))>int(obj.get('startIndex','0'))

def SetQuery(url, key, val):
    if not url or not key or not val:
        return
    url = re.sub(r'' + re.escape(key) + '=[^&]', '', url)
    if re.search(r'\?', url):
        url = re.sub(r'&$', '', url) + '&' + key + '=' + str(val)
    else:
        url += '?' + key + '=' + str(val)
    return url


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def GetSearchQuery(url):
    if not url:
        return
    url = re.sub(r'q=[^&]', '', url)
    if re.search(r'\?', url):
        url += '&q='
    else:
        url += '?q='
    last_search = addon.load_data('search')
    if not last_search: last_search = ''
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('[COLOR green]Search[/COLOR]')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        addon.save_data('search',query)
        url = url + query
        HandleUrl(url)
    else:
        return  

def get_path():
    return addon.get_path().decode('utf-8')

def notify(header=None, msg='', duration=2000, sound=None):
    if header is None: header = addon.get_name()
    if sound is None: sound = addon.get_setting('mute_notifications') == 'false'
    icon_path = os.path.join(get_path(), 'icon.png')
    try:
        xbmcgui.Dialog().notification(header, msg, icon_path, duration, sound)
    except:
        builtin = "XBMC.Notification(%s,%s, %s, %s)" % (header, msg, duration, icon_path)
        xbmc.executebuiltin(builtin)

#################################################################################################################################################################################

if mode == 'main':
    MainMenu()
elif mode == 'Menu1':
    Menu1()
elif mode == 'HandleContent':
    HandleContent(content, link, linkType)  
elif mode == 'HandleContentList':
    HandleContentList(content)  
elif mode == 'HandleUrl':
    HandleUrl(url, startPage) 
elif mode == 'GetSearchQuery':
    GetSearchQuery(url)        
#elif mode == 'ResolverSettings':
        #urlresolver.display_settings()
xbmcplugin.endOfDirectory(_handle)
