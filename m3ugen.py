import sys
import os
import codecs
import string
import re
from mutagen.id3 import ID3, TIT2
from mutagen.mp3 import EasyMP3 as MP3

__doc__ = "Generate m3u playlists in all subdirs where mp3s are found"
__author__ = "vbs <vbs@springrts.de>"
__date__ = "06 11 2012"
__version__ = "0.2"

FORMAT_DESCRIPTOR = "#EXTM3U"
RECORD_MARKER = "#EXTINF"

errors = []

def cleanupFilename(filename):
    ichars = "[/:*?<>|]"
    ichars2 = '"'
    filename = re.sub(ichars, '-', filename)
    filename = re.sub(ichars2, "'", filename)
    return filename.replace("\\","-")
    
def getM3uFilename(file):
    tags = ID3(file)
    albArtist = unicode(tags["TPE2"])
    album = unicode(tags["TALB"])

    discStr = u""
    if "TPOS" in tags:
        discStr = u" CD" + unicode(tags["TPOS"])
    
    name = u"00 "
    if albArtist != "Various":
        name += u"%s - " % albArtist
    name += u"%s%s.m3u8" % (album, discStr)
    return cleanupFilename(name)
    
def writeM3u(path, files):
    if len(files) == 0:
        return
    
    m3ufilename = getM3uFilename(os.path.join(path, files[0]))
    name = os.path.join(path, m3ufilename)
    with codecs.open(name, 'w', encoding='utf-8') as fp:
        fp.write(FORMAT_DESCRIPTOR + "\n")

        for track in files:
            audio = MP3(os.path.join(path, track))
            tags = ID3(os.path.join(path, track))
            
            artist = unicode(tags["TPE1"])
            title = unicode(tags["TIT2"])
            displayName = artist + u" - " + title
            seconds = int(round(audio.info.length))
            
            fp.write("%s:%s,%s\n" % (RECORD_MARKER, seconds, displayName))
            fp.write(track + "\n")
        fp.close()
    
def generateM3u(tuple):
    path = tuple[0]
    print "in Dir %s" % tuple[0].encode("utf8")
    files = tuple[2]
    mp3s = [i for i in files if i[-3:] == "mp3"]
    
    if len(mp3s) == 0:
        return
    
    print "Found %s mp3 files" % len(mp3s)
    writeM3u(path, mp3s)

def deleteAllM3us(path):
    print "Searching and deleting existing M3Us..."

    items = os.walk(path)
    for item in items:
        files = item[2]
        m3us = [i for i in files if (i[-3:] == "m3u" or i[-4:] == "m3u8")]
        for m3u in m3us:
            m3upath = os.path.join(item[0], m3u)
            print "Deleting: %s" % m3upath.encode("utf8")
            os.remove(m3upath)

def process(dir):
    print "Searching files in directory: %s" % dir.encode("utf8")
    items = os.walk(dir)
    for item in items:
        try:
            generateM3u(item)
        except Exception as ex:
            print "Error processing directory '%s': %s" % (item[0], unicode(ex))
     
def _usage():
    """ print the usage message """
    msg = "Usage:  %s [path]\n" % sys.argv[0]
    msg += __doc__ + "\n"
    msg += "Options:\n"
#    msg += "\n%5s,\t%s\t\t\t%s\n\n" % ("-h", "--help", "display this help and exit")

    print msg

def printErrorSummary():
    print "Errors: %s" % len(errors)
    for error in errors:
        print("%s -> %s" % (error['dir'].encode("utf8"), error['ex'].encode("utf8")))
    print "---"
    
def main():
    reload(sys) 
    sys.setdefaultencoding('utf-8')
    if len(sys.argv) < 2:
        _usage()
        sys.exit(1)

    path = sys.argv[1].decode("iso-8859-1")
    
    if os.path.exists(path):
        deleteAllM3us(path)
        process(path)
        printErrorSummary()
    else:
        sys.stderr.write("Given path does not exist\n")
        sys.exit(2)

if __name__ == '__main__':
    main()