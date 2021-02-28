#!/usr/bin/env python3
import json
import pathlib
import sys


class Preferences(object):
    def __init__(self, display):
        """Initialize the Preferences object internally."""
        self.__prefs_path = './preferences/preferences.json'
        self.__display = display
        self.__load_and_check()

    def __load_and_check(self):
        """Load the Preferences file, set and validate JSON keys, and check the presence of music categories."""
        try:
            with open(self.__prefs_path, 'r') as prefs_file:
                self.__prefs_data = json.load(prefs_file)
        except FileNotFoundError:
            self.__display.show_error('The Preferences could not be found. Ensure the \'preferences.json\' file is '
                                      'located under a \'preferences/\' directory at the root of the project and try '
                                      'again.')
            sys.exit(1)

        self.__prefs_data_collection = self.__validate_key('collection', self.__prefs_data)
        self.__prefs_data_collection_root = self.__validate_key('root', self.__prefs_data_collection)
        self.__prefs_data_collection_playlists = self.__validate_key('playlists', self.__prefs_data_collection)
        self.__prefs_data_collection_music = self.__validate_key('music', self.__prefs_data_collection)
        self.__prefs_data_exportation = self.__validate_key('exportation', self.__prefs_data)
        self.__prefs_data_exportation_root = self.__validate_key('root', self.__prefs_data_exportation)
        self.__prefs_data_exportation_playlists = self.__validate_key('playlists', self.__prefs_data_exportation)
        self.__prefs_data_exportation_format = self.__validate_key('format', self.__prefs_data_exportation)
        self.__check_presence_collection_music_categories()

    def __validate_key(self, key, data):
        """Validate if a provided key is correct and present in the Preferences. If not, generate an error and leave the
        program.

        :param str key: the JSON key to check.
        :param str data: the JSON string to parse.
        :return str string[key]: the JSON string successfully parsed or generate an error and leave the program.
        """
        try:
            return data[key]
        except KeyError as e:
            self.__display.show_error('The following key was not found:\n{}\nPlease ensure that a correct key has been '
                                      'provided in the Preferences and try again.'.format(e))
            sys.exit(1)

    def __check_presence_collection_music_categories(self):
        """Check the presence of at least one music category. If none found, generate an error and leave the program."""
        if (len(self.__prefs_data_collection_music)) == 0:
            self.__display.show_error('At least one category is required.\nPlease add a category (e.g. Artists) with '
                                      'its corresponding path and try again.')
            sys.exit(0)

    def __validate_path(self, path):
        """Validate if a provided path is correct. If not, generate an error and leave the program.

        :param str path: path to check.
        """
        path_parsed = pathlib.Path(path)
        if not path_parsed.is_dir():
            self.__display.show_error('The following path is invalid:\n{}\nPlease ensure that a correct path has been '
                                      'provided in the Preferences and try again.'.format(path_parsed))
            sys.exit(1)

    def get_collection_path_root(self):
        """Validate and get the root path of the music collection.

        :return str path: root path of the music collection.
        """
        path = self.__prefs_data_collection_root
        self.__validate_path(path)
        return path

    def get_collection_path_playlists(self):
        """Validate and get path of the directory where are stored the playlists in the music collection.

        :return str path: path of playlists.
        """
        path = self.__prefs_data_collection_root + self.__prefs_data_collection_playlists
        self.__validate_path(path)
        return path

    def get_collection_paths_music_categories(self):
        """Validate and get all the paths of all music categories in the music collection.

        :return dict music_categories_paths: the music categories paths.
        """
        music_categories_paths = {}

        for category in self.__prefs_data_collection_music:
            category_path = self.__prefs_data_collection_root + self.__prefs_data_collection_music[category]
            self.__validate_path(category_path)
            music_categories_paths[category] = category_path

        return music_categories_paths

    def get_collection_prefixes_music_categories(self):
        """Get the prefixes of music categories in the music collection.

        :return list music_prefixes: prefixes of music categories.
        """
        music_prefixes = []

        for category in self.__prefs_data_collection_music:
            music_prefixes.append(self.__prefs_data_collection_music[category])

        return music_prefixes

    def get_exportation_path_root(self):
        """Validate and get the root path of the playlists exportation. Also check that the directory is empty without
        including hidden files.

        :return str path: root path of the playlists exportation or generate an error and leave the program.
        """
        path = self.__prefs_data_exportation_root
        self.__validate_path(path)

        visible_files = [file for file in pathlib.Path(path).iterdir() if not file.name.startswith('.')]
        if len(visible_files) != 0:
            self.__display.show_error('The directory used for the exportation is not empty. Please remove all the '
                                      'files in this directory and try again.')
            sys.exit(1)
        else:
            return path

    def get_exportation_path_playlists(self):
        """Get the path of the directory where will be stored the playlists during the exportation.

        :return str path: path of playlists.
        """
        path = self.__prefs_data_exportation_root + self.__prefs_data_exportation_playlists
        return path

    def get_exportation_format(self):
        """Check and get the exportation format.

        :return str self.__prefs_data_exportation_format: preferred exportation format or, if invalid, generate an
         error and leave the program.
        """
        if self.__prefs_data_exportation_format != 'mp3' and self.__prefs_data_exportation_format != 'flac':
            self.__display.show_error('The provided format (\'{}\') is not valid. Only \'mp3\' and \'flac\' formats '
                                      'are supported. Please modify the Preferences and try again.'
                                      .format(self.__prefs_data_exportation_format))
            sys.exit(1)
        else:
            return self.__prefs_data_exportation_format
