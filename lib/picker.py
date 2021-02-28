#!/usr/bin/env python3
import re
import lib as audiouslib


class Picker(object):
    def __init__(self, display, preferences, collection):
        """Initialize the Picker object internally."""
        self.__display = display
        self.__prefs = preferences
        self.__coll = collection
        self.__play = audiouslib.playlists.Playlists(display, preferences)

        self.__collection_paths_music_categories = None
        self.__collection_prefixes_music_categories = None
        self.__playlists_albums = None
        self.__total_albums_collection = 0
        self.__total_albums_playlists = 0
        self.__total_albums_picked = 0
    
    def init(self):
        """Initialize the Picker object. Get the paths of the music collection categories and their prefixes."""
        self.__play.init()
        self.__coll.init()
        self.__collection_paths_music_categories = self.__prefs.get_collection_paths_music_categories()
        self.__collection_prefixes_music_categories = self.__prefs.get_collection_prefixes_music_categories()

    def pick_albums(self):
        """Pick the albums that are not in playlists. Then, for each music collection category:
          * First, get the albums of the category
          * Pick all the albums that are not listened in a category
          * Set totals for the albums in the category and the albums picked in this category
          * Show the statistics of the current category as well as the picked albums
          * Increment the totals
        Finally, show a summary for all categories.
        """
        self.get_playlists_albums()

        for category, path in self.__collection_paths_music_categories.items():
            category_albums = self.__get_category_albums(category, path)
            category_albums_picked = self.__pick_albums_category(category_albums)
            total_category_albums = len(category_albums)
            total_category_albums_picked = len(category_albums_picked)

            self.__show_statistics_category(total_category_albums, total_category_albums_picked)
            self.__show_picked_albums_category(category_albums_picked)
            self.__total_albums_collection += total_category_albums
            self.__total_albums_picked += total_category_albums_picked

        self.__show_statistics()

    def get_playlists_albums(self):
        """Get all the albums that are in the playlists."""
        self.__display.show_substep('Parsing playlists')
        self.__play.show_playlists_total()
        self.__playlists_albums = self.__play.get_albums()

    def __get_category_albums(self, category, path):
        """Get all the albums that are in a music collection category.

        :param str category: the music collection category name.
        :param str path: the path where the music collection category is located.
        :return list category_albums: list of albums contained in a music category.
        """
        self.__display.show_substep('Picking albums to listen in \'{}\''.format(category.title()))
        category_songs = self.__coll.get_category_songs(category, path)
        category_albums = self.__coll.get_category_albums(category_songs)
        return category_albums

    def __pick_albums_category(self, category_albums):
        """Pick all the albums not listened in a category. Also sort the albums alphabetically.

        :param list category_albums: list of albums contained in a music category.
        :return list category_albums_picked: list of albums picked in a music category.
        """
        category_albums_picked = []

        for album in category_albums:
            if album not in self.__playlists_albums:
                category_albums_picked.append(album)

        category_albums_picked = sorted(category_albums_picked, key=str.lower)
        return category_albums_picked

    def __show_statistics_category(self, total_category_albums, total_category_albums_picked):
        """Show the statistics of a music collection category, including the albums that are already present in the
        playlists and those that are not.

        :param int total_category_albums: length of the list of albums in a music category.
        :param int total_category_albums_picked: length of the list of albums picked in a music category.
        """

        # Showing the total of albums already listened in a category
        total_listened = total_category_albums - total_category_albums_picked
        self.__display.show_triple(self.__display.show_validation, total_listened,
                                   '{} albums are already in the playlists'.format(total_listened),
                                   '1 album is already in the playlists',
                                   'No albums were found in the playlists for this category')

        # Showing the total of albums that need to be listened in a category
        self.__display.show_triple(self.__display.show_warning, total_category_albums_picked,
                                   '{} albums are not in the playlists'.format(total_category_albums_picked),
                                   '1 album is not in the playlists', 'No albums to pick')

    def __show_statistics(self):
        """Show the statistics of the music collection as well as of the playlists, including the albums that are in
        the music collection and the ones that are in the playlists. Also show the albums that are picked.
        """
        self.__display.show_substep('Summary')

        # Showing the total of albums in the music collection
        self.__display.show_validation('Albums in the music collection: {}'.format(self.__total_albums_collection))
        self.__coll.check_total_albums_collection()

        # Showing the total of albums in the playlists
        self.__total_albums_playlists = self.__total_albums_collection - self.__total_albums_picked
        pc_playlists = (self.__total_albums_playlists / self.__total_albums_collection) * 100.
        self.__display.show_validation('Albums in the playlists: {} ({:,.2f}%)'
                                       .format(self.__total_albums_playlists, pc_playlists))

        # Showing the total of picked albums
        pc_picked = 100. - pc_playlists
        self.__display.show_warning('Albums not in the playlists: {} ({:,.2f}%)'
                                    .format(self.__total_albums_picked, pc_picked))

    def __show_picked_albums_category(self, category_albums_picked):
        """Show the list of albums picked in a music category. First, remove music prefixes and then display the
        album one by one, using a bitwise operation to alternate the printing of every two albums.

        :param: list category_albums_picked: list of albums picked in a music category.
        """
        for album in range(len(category_albums_picked)):
            for prefix in self.__collection_prefixes_music_categories:
                category_albums_picked[album] = re.sub(prefix, '', category_albums_picked[album])

        cnt = 0
        for album in category_albums_picked:
            album = album.replace('/', ' \u2192 ', 1)
            cnt += 1
            if (cnt & 1) == 0:
                self.__display.show_picked_album_odd(album)
            else:
                self.__display.show_picked_album_even(album)
