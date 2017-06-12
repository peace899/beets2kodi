KodiNfo Plugin
=================

The plugin lets you create local `.nfo`_ files for `Kodi`_ music
library whenever you import an album into the library. These .nfo files usually 
contain release information about the media. The information may include authorship and licence information
The plugin relies on the information provided by beets library and `The AudioDB`_
(TADB). It uses MusicBrainz IDs to look up metadata.

.. _.nfo:
    http://kodi.wiki/view/NFO_files
.. _Kodi:
   http://www.kodi.tv
.. _The AudioDB:
   http://www.theaudiodb.com

Installation
______________

The plugin requires `lxml`_ module, which you can install using :ref:`pip` by typing:

``pip install lxml``

After you have pylast installed, enable the ``kodinfo`` plugin in your configuration (see :ref:`using-plugins`).

.. _lxml:
   http://lxml.de/
Configuration
______________
To configure the pluging, create a ``kodi:`` section in your ``config.yaml``,
to look like this::

    kodi:
        host: localhost
        port: 8080
        user: kodi
        pwd: kodi
        nfo_format: xml

host: The host of your kodi library (either the IP address or server name of your kodi installed computer)

    
For the nfo_format key, choices are 'xml' or 'mbid_only_text'.
The choice 'xml' produces XML type document, while the 'mbid_only_text'
produces a text file containing the MusicBrainz url of the artist or album.

To use the ``kodinfo`` plugin you need  (requests, urllib.request, lxml, 
simplejson, base64) modules.

You'll also need to enable JSON-RPC in Kodi in order the use the plugin.
In Kodi's interface, navigate to System/Settings/Network/Services and choose 
"Allow control of Kodi via HTTP."

With that all in place, you can create nfo/xml files for Kodi and update it's 
library after import.
