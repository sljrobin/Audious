#!/usr/bin/env python3
import os
import re
import sys


class Playlists(object):
    def __init__(self, display, preferences):
        """Initialize the Playlists object internally."""
        self.__display = display
        self.__prefs = preferences

        self.__collection_path_root = None
        self.__collection_path_playlists = None
        self.__total_albums = 0

    def init(self):
        """Initialize the Playlists object."""
        self.__collection_path_root = self.__prefs.get_collection_path_root()
        self.__collection_path_playlists = self.__prefs.get_collection_path_playlists()

    def get_songs(self):
        """Open recursively all the playlists. Get all the songs that are in the playlists. Also remove all the
        duplicates.

        :return list playlists_songs: list of all songs available in the playlists.
        """
        playlists_paths = self.get_playlists_paths()
        playlists_songs = []

        for playlist in playlists_paths:
            songs = self.__get_playlist_songs(playlist)
            for song in songs:
                playlists_songs.append(song)
        playlists_songs = list(set(playlists_songs))
        return playlists_songs

    def __get_playlist_songs(self, path):
        """Open a playlist and get a list of all the songs contained in this playlist. Remove blank lines as well as
        the leading and trailing characters in a line. Then concatenate the song with its full path.

        :param str path: full path of a playlist
        :return list albums: list of songs contained in a playlist
        """
        songs = []

        with open(path, 'r', encoding="utf8", errors='ignore') as playlist_file:
            for line in playlist_file:
                line = line.strip()
                if line:
                    songs.append(self.__collection_path_root + line)

        return songs

    def get_albums(self):
        """Open recursively all the playlists and get all the albums that are in the playlists. Also remove all the
        duplicates, increment the total of albums found in the playlists, and check the presence of at least one
        album.

        :return list playlists_albums: list of all albums available in the playlists.
        """
        playlists_paths = self.get_playlists_paths()
        playlists_albums = []

        for playlist in playlists_paths:
            albums = self.__get_playlist_albums(playlist)
            for album in albums:
                playlists_albums.append(album)

        playlists_albums = list(set(playlists_albums))
        self.__total_albums = len(playlists_albums)
        self.__check_total_albums()

        return playlists_albums

    def __get_playlist_albums(self, path):
        """Open a playlist and get a list of all the albums contained in a playlist. Remove blank lines as well as the
        leading and trailing characters in a line. Also remove all the duplicates.

        :param str path: full path of a playlist
        :return list albums: list of albums contained in a playlist
        """
        albums = []

        with open(path, 'r', encoding="utf8", errors='ignore') as playlist_file:
            for line in playlist_file:
                line = line.strip()
                if line:
                    albums.append(line.rsplit('/', 1)[0])

        return albums

    def get_playlists_paths(self):
        """Get all the paths of all the playlists. Select only .m3u files with a regex. Check the presence of at least
        one playlist.

        :return list paths: a list containing all playlists with full paths.
        """
        regex = re.compile(r'\.(m3u)$')
        paths = []

        for path, dnames, fnames in os.walk(self.__collection_path_playlists):
            paths.extend([os.path.join(path, x) for x in fnames if regex.search(x)])

        self.__check_total_playlists(len(paths))
        return paths

    def __check_total_playlists(self, total):
        """Check the total of playlists. If none found, generate an error and leave the program.

        :param int total: length of all the paths of all the playlists.
        """
        if total == 0:
            self.__display.show_error('At least one playlist is required. Please add a playlist and try again.')
            sys.exit(0)

    def __check_total_albums(self):
        """Check the total of albums in the playlists and display a message depending on the quantity that was found.
        """
        if self.__total_albums > 1:
            self.__display.show_validation('{} albums were found in the playlists'.format(self.__total_albums))
        elif self.__total_albums == 1:
            self.__display.show_validation('1 album was found in the playlists')
        else:
            self.__display.show_error('No albums were found in the playlists.')

    def show_playlists_total(self):
        """Show the total of playlists that were found in the music collection with a different message, depending on
        the quantity that was found.
        """
        total = len(self.get_playlists_paths())
        if total > 1:
            self.__display.show_validation('{} playlists were found'.format(total))
        elif total == 1:
            self.__display.show_validation('1 playlist was found')
