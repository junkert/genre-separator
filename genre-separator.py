#!/usr/bin/env python
import os
import argparse
from pprint import pprint
from shutil import copyfile
from mutagen.easyid3 import EasyID3
from mutagen.aiff import AIFF


class Crawler(object):
    def __init__(self):
        pass

    # This is a slow version. Super inefficient
    def crawl_path(self, path):
        file_list = []
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                self.crawl_path(os.path.join(root, dir))
            for file in files:
                if os.path.join(root, file) == root:
                    return
                if os.path.isfile(os.path.join(root, file)):
                    file_list.append(os.path.join(root, file))
        pprint(f"FILE_LIST: {file_list}")
        return file_list


class AudioFile():
    def __init__(self, path):
        self.path = path
        self.has_id3 = False
        self.genre = None
        self.id3 = self.get_id3_tags()

    def get_id3_tags(self):
        if (".aif" in os.path.basename(self.path) or
            ".mp3" in os.path.basename(self.path)):
            try:
                if ".aif" in os.path.basename(self.path):
                    aiff = AIFF(self.path)
                    self.id3 = aiff.tags
                    self.genre = aiff.tags['TCON'].text[0].replace('/', '&')
                    self.has_id3 = True
                elif ".mp3" in os.path.basename(self.path):
                    self.id3 = EasyID3(self.path)
                    self.genre = str(self.id3['genre'][0]).replace('/', '&')
                    self.has_id3 = True
                else:
                    self.has_id3 = False

            except Exception as e:
                print(e.__str__())
                print("WARN: %s does not have an ID3 tag." % self.path)
                self.has_id3 = False
        else:
            self.has_id3 = False
            self.id3 = None


def parseArgs():
    defaults = {}
    conf_parser = argparse.ArgumentParser(
        description=("Genera Separator is a tool for seperating a "
                     "collection of music files into folders based on the "
                     "musical ID3 genre tags in MP3 and AIFF files."))
    conf_parser.add_argument("-c",
                             "--config",
                             dest="config",
                             metavar="config",
                             help="ini configuration file.")
    conf_parser.add_argument("-d",
                             "--dest-path",
                             dest="dest_path",
                             metavar="dest_path",
                             required=True,
                             help="Path of root directory to copy files to.")
    conf_parser.add_argument("-s",
                             "--source-path",
                             dest="source_path",
                             metavar="source_path",
                             required=True,
                             help="Path to crawl for audio files.")
    return conf_parser.parse_args()


def main(args):
    audio_files = []

    # Crawl the source path and build AudioFile objects
    crawler = Crawler()
    unknown_path = os.path.join(args.dest_path, "UNKNOWN")
    file_paths = crawler.crawl_path(args.source_path)

    if not os.path.isdir(os.path.dirname(unknown_path)):
        print(f"Creating directory for unknown ID3 tags: {os.path.dirname}")
        os.mkdir(os.path.dirname(unknown_path))
    for p in file_paths:
        dest_path = None
        audio_file = AudioFile(p)
        try:
            print(f"{audio_file.path}: {audio_file.genre}: {audio_file.has_id3}")
            if not audio_file.has_id3:
                dest_path = os.path.join(args.dest_path, "UNKNOWN") +\
                            "/" + os.path.basename(p)
            else:
                dest_path = os.path.join(args.dest_path) + "/" + \
                    audio_file.genre + "/" + os.path.basename(p)
        except Exception as e:
            print(f"EXCEPTION: {e.__str__()}")
            dest_path = os.path.join(args.dest_path, "UNKNOWN") + \
                        "/" + os.path.basename(p)

        print("==========================================")
        print("source: %s" % p)
        print("dest: %s" % dest_path)
        print("genre: %s" % audio_file.genre)# create Genre directory
        if not os.path.isdir(os.path.dirname(dest_path)):
            print("Creating directory: %s" % os.path.dirname(dest_path))
            os.mkdir(os.path.dirname(dest_path))

        # Now copy file
        if os.path.isfile(dest_path):
            print("WARN: File already exists!")
        else:
            print("Copying %s to %s" % (p, dest_path))
            copyfile(p, dest_path)

    return 0

if __name__ == "__main__":
    # Change to BASH return codes:
    # 0   -> True
    # 1   -> False
    # > 1 -> That value
    val = main(parseArgs())
    if val == 'False' or val == '0':
        exit(1)
    elif val == 'True' or val == '1':
        exit(0)
    else:
        exit(int(val))


