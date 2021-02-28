#!/usr/bin/env python3
import os
import re
import sys


class Collection(object):
    def __init__(self, display, preferences):
        """Initialize the Collection object internally."""
        self.__display = display
        self.__prefs = preferences

        self.__collection_path_root = None
        self.__collection_paths_music_categories = None
        self.__total_albums = 0

    def init(self):
        """Initialize the Collection object. Get the paths of the music collection and categories. Also check the
        presence of at least one music category.
        """
        self.__collection_path_root = self.__prefs.get_collection_path_root()
        self.__collection_paths_music_categories = self.__prefs.get_collection_paths_music_categories()
        self.__check_total_music_categories()

    def __check_total_music_categories(self):
        """Check the total of music categories. If none found, generate an error and leave the program."""
        if len(self.__collection_paths_music_categories) == 0:
            self.__display.show_error('At least one music category is required. Please add a music category '
                                      'and try again.')
            sys.exit(0)

    def get_category_albums(self, category_songs):
        """Open a category in the music collection and get a list of all the albums contained in this category.
        Handle macOS hidden files. Check the number of albums in the music category as well as in the music collection.
        Increment the total.

        :param list category_songs: list of songs contained in a music category.
        :return list category_albums: list of albums contained in a music category.
        """
        category_albums = []

        for song in category_songs:
            if '.DS_Store' not in song:
                album = song.rsplit('/', 1)[0]
                album = album.replace(self.__collection_path_root, '')
                if album not in category_albums:
                    category_albums.append(album)

        total_albums_category = len(category_albums)
        self.__check_total_albums_category(total_albums_category)
        self.__total_albums += total_albums_category
        return category_albums

    def __check_total_albums_category(self, total):
        """Check the total of albums in a music collection category and display a message depending on the quantity
        that was found.

        :param int total: length of the list of albums contained in a music collection category.
        """
        self.__display.show_triple(self.__display.show_validation, total,
                                   '{} albums were found in this category'.format(total),
                                   '1 album was found in this category',
                                   'No albums were found in this category')

    def get_category_songs(self, category, path):
        """Open a category in the music collection and get a list of all the songs contained in this category. Select
        only .mp3 and .flac files with a regex.

        :param str category: the music collection category name.
        :param str path: the path where the music collection category is located.
        :return list category_songs: list of songs contained in a music category.
        """
        self.__display.show_validation('Parsing \'{}\' in the music collection'.format(category.title()))
        regex = re.compile(r'\.(flac)$|\.(mp3)$')

        category_songs = []
        for path, dnames, fnames in os.walk(path):
            category_songs.extend([os.path.join(path, x) for x in fnames if regex.search(x)])
        return category_songs

    def check_total_albums_collection(self):
        """Check the total of albums in the music collection. If none found, generate an error and leave the program."""
        if self.__total_albums == 0:
            self.__display.show_error('At least one album is required. Please add an album in the music collection and '
                                      'try again.')
            sys.exit(0)
