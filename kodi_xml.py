

#!/usr/bin/env python

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
from lxml import etree as ET
 
artist_tags = ['name', 'musicBrainzArtistID', 'sortname', 'genre', 'style', 'mood',
               'born', 'formed', 'biography', 'died', 'disbanded', 'thumb', 'fanart']

album_tags = ['title', 'musicBrainzAlbumID', 'artist', 'genre', 'style', 'mood',
              'theme', 'compilation', 'type', 'releasedate', 'label', 'rating', 'year']

emptyalbum = '''{"album":[{"idAlbum":"","idArtist":"","idLabel":"","strAlbum":"",
             "strAlbumStripped":"","strArtist":"","intYearReleased":"","strStyle":"",
             "strGenre":"","strLabel":"","strReleaseFormat":"","intSales":"",
             "strAlbumThumb":"","strAlbumThumbBack":"","strAlbumCDart":"","strAlbumSpine":"",
             "strDescriptionEN":"","strDescriptionDE":"","strDescriptionFR":"",
             "strDescriptionCN":"","strDescriptionIT":"","strDescriptionJP":"",
             "strDescriptionRU":"","strDescriptionES":"","strDescriptionPT":"",
             "strDescriptionSE":"","strDescriptionNL":"","strDescriptionHU":"",
             "strDescriptionNO":"","strDescriptionIL":"","strDescriptionPL":"",
             "intLoved":"","intScore":"","intScoreVotes":"","strReview":" ",
             "strMood":"","strTheme":"","strSpeed":"","strLocation":"","strMusicBrainzID":"",
             "strMusicBrainzArtistID":"","strItunesID":"","strAmazonID":"","strLocked":""}]}'''

emptyartist = '''{"artists":[{"idArtist":"","strArtist":"","strArtistAlternate":"","strLabel":"",
              "idLabel":"","intFormedYear":"","intBornYear":"","intDiedYear":"","strDisbanded":"",
              "strStyle":"","strGenre":"","strMood":"","strWebsite":"","strFacebook":"",
              "strTwitter":"","strBiographyEN":"","strBiographyDE":"","strBiographyFR":"",
              "strBiographyCN":"","strBiographyIT":"","strBiographyJP":"","strBiographyRU":"",
              "strBiographyES":"","strBiographyPT":"","strBiographySE":"","strBiographyNL":"",
              "strBiographyHU":"","strBiographyNO":"","strBiographyIL":"","strBiographyPL":"",
              "strGender":"","intMembers":"","strCountry":"","strCountryCode":"","strArtistThumb":"",
              "strArtistLogo":"","strArtistFanart":"","strArtistFanart2":"","strArtistFanart3":"",
              "strArtistBanner":"","strMusicBrainzID":"","strLastFMChart":"","strLocked":"unlocked"}]}'''

libpath = os.path.expanduser(config['library'])
lib = beets.library.Library(libpath)

albumid = 'mb_albumid:'+ mb_albumid
for album in lib.albums(albumid):
    artistid = 'mb_albumartistid' + album.mb_albumartistid

def artist_info():
    for album in lib.albums(albumid):
        data = album.albumartist,album.albumartist_sort,album.mb_albumartistid,album.genre,album.path
        url = "http://www.theaudiodb.com/api/v1/json/{0}/artist-mb.php?i=".format(config['audiodb']['key'])
        
        try:
            response = urllib.request.urlopen(url+data[2])
            data2 = simplejson.load(response)["artists"][0]
            
        except (ValueError, TypeError):  # includes simplejson.decoder.JSONDecodeError
            data2 = json.loads(emptyartist)["artists"][0]

def artist_albums():
    albumdata = []
    for album in lib.albums(artistid):
        row = album.album,album.year
        albumdata.append(list(tuple([row[1],row[0]]))) #create sortable list
        albumlist = (sorted(albumdata)) #sort list to start with first release/album
    return albumlist

def album_info():
    for album in lib.albums(albumid):
        data = (album.albumartist,album.mb_albumartistid,album.mb_releasegroupid,album.album,
               album.genre,album.comp,album.label,album.albumtype,album.mb_albumid)
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


def album_tracks():
    trackdata = []    
    for item in lib.items(albumid):
        row = item.track,item.mb_trackid,item.length,item.title
        duration = time.strftime("%M:%S", time.gmtime(row[2]))
        trackdata.append(list(tuple([row[0],duration,row[1],row[3]])))
        tracklist = (sorted(trackdata)) #sort list by track number
    return tracklist

def artist_nfo():
    root = ET.Element('artist')
    for i in range(len(tags)):
        tags[i] = ET.SubElement(root, '{}'.format(tags[i]))
        tags[i].text = album_info()[i]

    for i in range(len(artist_albums())):
        album = ET.SubElement(root, 'album')
        title = ET.SubElement(album, 'title')
        title.text = artist_albums()[i][0]
        year =   ET.SubElement(album, 'year')
        year.text = artist_albums()[i][1]

    xml =  ET.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone="yes").decode()
    print (xml, file=open('output.xml', 'w+'))

def album_nfo():
    root = ET.Element('album')
    for i in range(len(album_tags)):
        album_tags[i] = ET.SubElement(root, '{}'.format(album_tags[i]))
        album_tags[i].text = album_info()[i]

    for i in range(len(album_tracks())):
        track = ET.SubElement(root, 'track')
        position = ET.SubElement(track, 'position')
        position.text = album_tracks()[i][0]
        title =   ET.SubElement(track, 'title')
        title.text = album_tracks()[i][1]
        duration = ET.SubElement(track, 'duration')
        position.text = album_tracks()[i][2]
        musicBrainzTrackID =   ET.SubElement(track, 'musicBrainzTrackID')
        musicBrainzTrackID.text = album_tracks()[i][3]

    xml =  ET.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone="yes").decode()
    print (xml, file=open('output.xml', 'w+'))
