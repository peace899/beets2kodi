
import os, time
import sys
import re
import simplejson, json
import base64
import yaml
import urllib
from urllib.request import Request, urlopen
import beets.library
from beets import config

"""Creates Kodi nfo files (artist.nfo & album.nfo) for your beets library/managed music.
Still some errors there and there, a work-in-progress project

Put something like the following in your config.yaml to configure: as per kodiupdate plugin
    kodi:
        host: localhost
        port: 8080
        user: user
        pwd: secret
    audiodb:
        key: secretkey
"""
emptyalbum = '''{"album":[{"idAlbum":"","idArtist":"","idLabel":"","strAlbum":"","strAlbumStripped":"","strArtist":"","intYearReleased":"","strStyle":"","strGenre":"","strLabel":"Columbia","strReleaseFormat":"Album","intSales":"0","strAlbumThumb":"","strAlbumThumbBack":"","strAlbumCDart":"","strAlbumSpine":"","strDescriptionEN":"","strDescriptionDE":"","strDescriptionFR":"","strDescriptionCN":"","strDescriptionIT":"","strDescriptionJP":"","strDescriptionRU":"","strDescriptionES":"","strDescriptionPT":"","strDescriptionSE":"","strDescriptionNL":"","strDescriptionHU":"","strDescriptionNO":"","strDescriptionIL":"","strDescriptionPL":"","intLoved":"","intScore":"","intScoreVotes":"","strReview":" ","strMood":"","strTheme":"","strSpeed":"","strLocation":"","strMusicBrainzID":"","strMusicBrainzArtistID":"","strItunesID":"","strAmazonID":"","strLocked":"unlocked"}]}'''
emptyartist = '''{"artists":[{"idArtist":"","strArtist":"","strArtistAlternate":"","strLabel":"","idLabel":"","intFormedYear":"","intBornYear":"","intDiedYear":"","strDisbanded":"","strStyle":"","strGenre":"","strMood":"","strWebsite":"","strFacebook":"","strTwitter":"","strBiographyEN":"","strBiographyDE":"","strBiographyFR":"","strBiographyCN":"","strBiographyIT":"","strBiographyJP":"","strBiographyRU":"","strBiographyES":"","strBiographyPT":"","strBiographySE":"","strBiographyNL":"","strBiographyHU":"","strBiographyNO":"","strBiographyIL":"","strBiographyPL":"","strGender":"","intMembers":"","strCountry":"","strCountryCode":"","strArtistThumb":"","strArtistLogo":"","strArtistFanart":"","strArtistFanart2":"","strArtistFanart3":"","strArtistBanner":"","strMusicBrainzID":"","strLastFMChart":"","strLocked":"unlocked"}]}'''
libpath = os.path.expanduser('~/.config/beets/library.blb')
lib = beets.library.Library(libpath)
path = 'path:' + ('%s' % config['directory'])

def artist_info():
    #albumid = 'mb_albumid:'+ mb_albumid
    for album in lib.albums(albumid):
        data = album.albumartist,album.albumartist_sort,album.mb_albumartistid,album.genre,album.path
        url = "http://www.theaudiodb.com/api/v1/json/{0}/artist-mb.php?i=".format(config['audiodb']['key'])
        
        try:
            response = urllib.request.urlopen(url+data[2])
            data2 = simplejson.load(response)["artists"][0]
            
        except (ValueError, TypeError):  # includes simplejson.decoder.JSONDecodeError
            data2 = json.loads(emptyartist)["artists"][0]

        ainfo = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<artist>
    <name>{0}</name>
    <musicBrainzArtistID>{1}</musicBrainzArtistID>
    <sortname>{2}</sortname> 
    <genre>{3}</genre>
    <style>{4}</style>
    <mood>{5}</mood>
    <born>{6}</born>
    <formed>{7}</formed>
    <biography>{8}</biography>
    <died>{9}</died>
    <disbanded>{10}</disbanded>""".format(data[0], data[2], data[1], data[3], data2["strStyle"] or '', data2["strMood"] or '', 
         data2["intBornYear"] or '', data2["intFormedYear"] or '', data2["strBiographyEN"] or '', data2["intDiedYear"] or '', 
         data2["strDisbanded"] or '')
        print (ainfo, file=open(artistnfo,"w+"))
        paths('artist','path')
        paths('artist','thumb')
        print ("    <thumb>{0}</thumb>".format(data2["strArtistThumb"] or ''), file=open(artistnfo,"a"))
        print ("    <fanart>{0}</fanart>".format(data2["strArtistFanart"] or ''), file=open(artistnfo,"a"))
        artistid = 'mb_albumartistid:' + data[2]
        albumdata = []
        for album in lib.albums(artistid):
            row = album.album,album.year
            albumdata.append(list(tuple([row[1],row[0]]))) #create sortable list
            albumlist = (sorted(albumdata)) #sort list to start with first release/album
        for i in albumlist:
            albums = """    <album>
            <title>%s</title> 
            <year>%s</year>\n    </album>""" % (i[1], i[0]) 
            print (albums, file=open(artistnfo,"a")) 
        print ("</artist>", file=open(artistnfo,"a"))
    
def album_info():
    #albumid = 'mb_albumid:'+ mb_albumid
    for album in lib.albums(albumid):
        data = album.albumartist,album.mb_albumartistid,album.mb_releasegroupid,album.album,album.genre,album.comp,album.label,album.albumtype
        date = album.original_year,album.original_month,album.original_day
        rel_date = ("%s-%s-%s" % (date[0], format(date[1], '02'),format(date[2], '02')));
        url= "http://www.theaudiodb.com/api/v1/json/{0}/album-mb.php?i=".format(config['audiodb']['key']) 
        if data[5] == 0:
            comp = 'False'
        else:
            comp = 'True'
                     
        try:
            response = urllib.request.urlopen(url+data[2])
            data2 = simplejson.load(response)["album"][0]
             
        except (ValueError, TypeError):
            data2 = json.loads(emptyalbum)["album"][0]
        
        ainfo = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<album>
    <title>{0}</title>
    <musicBrainzAlbumID>{1}</musicBrainzAlbumID>
    <artist>{2}</artist>
    <genre>{3}</genre>
    <style>{4}</style>
    <mood>{5}</mood>
    <theme>{6}</theme>
    <compilation>{7}</compilation>
    <review>{8}</review>
    <type>{9}</type>
    <releasedate>{10}</releasedate>
    <label>{11}</label>""".format(data[3], data[1], data[0], data[4], data2["strStyle"] or '', data2["strMood"] or '',
        data2["strTheme"] or '', comp, data2["strReview"] or '', data[7], rel_date, data[6])
        print (ainfo, file=open(albumnfo,"w+"))
        paths('album','path')
        paths('album','thumb')
        print ("    <thumb>{0}</thumb>".format(data2["strAlbumThumb"] or ''), file=open(albumnfo,"a"))
        print ("    <rating>{0}</rating>".format(yaml.load(data2["intScore"] or '0')/2,'.1f'), file=open(albumnfo,"a"))
        print ("    <year>{0}</year>".format(date[0]), file=open(albumnfo,"a"))
        print ("    <albumArtistCredits>", file=open(albumnfo,"a"))
        print ("       <artist>{0}</artist>".format(data[0]), file=open(albumnfo,"a"))
        print ("       <musicBrainzArtistID>{0}</musicBrainzArtistID>".format(data[1]), file=open(albumnfo,"a"))
        print ("    </albumArtistCredits>", file=open(albumnfo,"a"))
        trackdata = []    
        for item in lib.items(albumid):
            row = item.track,item.mb_trackid,item.length,item.title
            duration = time.strftime("%M:%S", time.gmtime(row[2]))
            trackdata.append(list(tuple([row[0],duration,row[1],row[3]])))
            tracklist = (sorted(trackdata)) #sort list by track number
        for i in tracklist:
            tracks = """    <track>
           <position>%s</position>
           <title>%s</title>
           <duration>%s</duration>
           <musicBrainzTrackID>%s</musicBrainzTrackID>\n    </track>""" % (i[0], i[3], i[1], i[2])
            print (tracks, file=open(albumnfo,"a"))
        print ("</album>", file=open(albumnfo,"a"))

def paths(tag, element):
    
    auth = str.encode('%s:%s' % (config['kodi']['user'], config['kodi']['pwd']))
    authorization = b'Basic ' + base64.b64encode(auth) 
    headers = { 'Content-Type': 'application/json', 'Authorization': authorization }
    url = "http://{0}:{1}/jsonrpc".format(config['kodi']['host'], config['kodi']['port'])
    data={"jsonrpc": "2.0", "method": "Files.GetSources", "params": {"media": "music"}, "id": 1}
    json_data = json.dumps(data).encode('utf-8')
    request = Request(url, json_data, headers)
    result = simplejson.load(urlopen(request))
    xbmc_path = result['result']['sources'][0]['file']
    out_data = []
    for album in lib.albums(albumid):
        row = album.albumartist,album.album,album.artpath,album.path
        data = str(config["directory"]) 
        length = int(len(data)+1)                         
        album_path = row[3].decode("utf-8")
        artist_path = os.path.dirname(album_path)
        if not row[2]:
            artfile = ''
        else:
            artfile = os.path.basename(row[2].decode("utf-8"))

        if row[0] in album_path or row[0] in artist_path:
            out_data = (album_path, (xbmc_path + album_path[length:])), (artist_path, (xbmc_path + artist_path[length:])), row[0]
        else:
            out_data = (album_path, (xbmc_path + album_path[length:])), '', row[0]  
        pathlist = list(set(out_data))

        if "artist" in tag  and "path" in element:
            for d in out_data[1]:
                dirs = """    <path>%s</path>""" % d
                print (dirs, file=open(artistnfo,"a"))

        if "artist" in tag  and "thumb" in element:
            for a in out_data[1]:
                thumbs = """    <thumb>%s/artist.tbn</thumb>""" % a
                print (thumbs, file=open(artistnfo,"a"))

        if "album" in tag  and "path" in element:
            for d in out_data[0]:
                dirs = """    <path>%s</path>""" % d
                print (dirs, file=open(albumnfo,"a"))

        if "album" in tag  and "thumb" in element:
            if artfile == '':
                pass
            else:        
                for a in out_data[0]:
                    thumbs = """    <thumb>%s/%s</thumb>""" % (a, artfile)
                    print (thumbs, file=open(artistnfo,"a"))

        if "list" in tag and "path" in element:
            return out_data

albumids = []
for album in lib.albums(path):
    row = album.mb_albumid,album.mb_albumartistid,album.albumartist
    albumids.append(row)
result = list(filter(None, albumids))

for i in result:
        
    if not i[0] or i[0] in open('/home/user/.config/beets/nfolog.txt').read():
        continue
    else:
        albumid = 'mb_albumid:'+ i[0]
        info = paths('list','path')
        try:
            albumnfo = os.path.join(info[0][0], 'album.nfo')
            artistnfo = os.path.join((os.path.dirname(info[0][0])), 'artist.nfo')
            print ("Processing Album: {0}".format(i[0])) 
            album_info()
            if info[2] in {'Various Artists', 'Soundtracks', ''}:
                pass
            else:
                artist_info()
                print (i[0], file=open('/home/user/.config/beets/nfolog.txt',"a+"))
        except OSError:
            continue    






