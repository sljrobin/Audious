#!/usr/bin/env python3
import datetime
import pathlib
import tinytag
import lib as audiouslib


class Statistics(object):
    def __init__(self, display, preferences, collection):
        """Initialize the Statistics object internally."""
        self.__display = display
        self.__prefs = preferences
        self.__coll = collection
        self.__play = audiouslib.playlists.Playlists(display, preferences)

        self.__collection_paths_music_categories = None
        self.__total_collection_songs, self.__total_collection_duration, self.__total_collection_albums = 0, 0, 0
        self.__total_playlists_songs, self.__total_playlists_duration, self.__total_playlists_albums = 0, 0, 0

    def init(self):
        """Initialize the Statistics object."""
        self.__collection_paths_music_categories = self.__prefs.get_collection_paths_music_categories()
        self.__coll.init()
        self.__play.init()

    def __report_song_duration(self, path):
        """Report the duration of a FLAC song by checking the metadata. Also check that the path of the song is valid
        and handle hidden files.

        :param str path: path of the song.
        :return float tag.duration: the duration of a song if the song is valid or 0 if not.
        """
        path_parsed = pathlib.Path(path)
        if path_parsed.is_file() and path_parsed.suffix == '.flac':
            song = path.rsplit('/', 1)[1]
            if not song.startswith('.'):
                tag = tinytag.TinyTag.get(path)
                return tag.duration
            else:
                self.__display.show_error('The following song could not be parsed and will be ignored: '
                                          '\'{}\''.format(path))
                return 0
        else:
            self.__display.show_error('The following song was not found: \'{}\''.format(path))
            return 0

    def compute(self):
        """Compute the statistics of the music collection as well as of the playlists, including the albums that are
        already present in the playlists and those that are not. Also show the total durations.
        """
        self.__display.show_substep('Parsing playlists')
        self.__display.show_warning('Note that only songs found in the music collection will be used to calculate the '
                                    'total duration.')
        self.__display.show_warning('If a song is not found, please ensure that it is in your music collection. If '
                                    'not, remove it from the playlist not to see again an error message about this '
                                    'song.')
        self.__fill_statistics_playlists()
        self.__show_statistics_playlists()

        for category, path in self.__collection_paths_music_categories.items():
            self.__display.show_substep('Getting statistics for \'{}\''.format(category.title()))
            self.__display.show_warning('Depending on the quantity of songs, this operation might take a while...')
            category_stats = self.__get_statistics_category(category, path)
            self.__show_statistics_category(category_stats)

        self.__display.show_substep('Summary')
        self.__show_statistics_summary('music collection', self.__total_collection_albums,
                                       self.__total_collection_songs, self.__total_collection_duration)
        print()
        self.__show_statistics_summary('playlists', self.__total_playlists_albums,
                                       self.__total_playlists_songs, self.__total_playlists_duration)

    def __fill_statistics_playlists(self):
        """Fill the statistics of the playlists. Show the total of available playlists. Get the duration of all songs
        and increment accordingly the total duration of the playlists.
        """
        self.__play.show_playlists_total()
        self.__total_playlists_albums = len(self.__play.get_albums())

        playlists_songs = self.__play.get_songs()

        self.__total_playlists_songs += len(playlists_songs)
        for song in playlists_songs:
            self.__total_playlists_duration += self.__report_song_duration(song)

    def __show_statistics_playlists(self):
        """Show the statistics of the playlists, including the number of songs and the total duration."""
        self.__display.show_triple(self.__display.show_validation, self.__total_playlists_songs,
                                   '{} songs were found in the playlists'.format(self.__total_playlists_songs),
                                   '1 song was found in the playlists', 'No songs were found in the playlists')
        self.__display.show_validation('Total duration of the playlists: {}'
                                       .format(self.__convert_duration(self.__total_playlists_duration)))

    def __get_statistics_category(self, category, path):
        """Get the statistics of a music collection category. Initialize totals for overall duration, the albums, and
        the songs. Get both the songs and the albums of a music collection category. Increment accordingly the totals
        and generate a dictionary containing those stats.

        :param str category: the music collection category name.
        :param str path: the path where the music collection category is located.
        :return dict category_stats: statistics of the music collection category.
        """
        total_duration_category, total_category_songs, total_category_albums = 0, 0, 0

        category_songs = self.__coll.get_category_songs(category, path)
        category_albums = self.__coll.get_category_albums(category_songs)

        total_category_songs += len(category_songs)
        total_category_albums += len(category_albums)
        self.__total_collection_songs += total_category_songs
        self.__total_collection_albums += total_category_albums

        for song in category_songs:
            total_duration_category += self.__report_song_duration(song)
            self.__total_collection_duration += self.__report_song_duration(song)

        category_stats = {'duration': total_duration_category, 'albums': total_category_albums,
                          'songs': total_category_songs}
        return category_stats

    def __show_statistics_category(self, category_stats):
        """Show the statistics of a music collection category, including the number of songs and the total duration.

        :param dict category_stats: statistics of the music collection category.
        """
        duration = self.__convert_duration(category_stats['duration'])
        songs = category_stats['songs']

        self.__display.show_triple(self.__display.show_validation, songs,
                                   '{} songs were found in this category'.format(songs),
                                   '1 song was found in this category', 'No songs were found in this category')
        self.__display.show_validation('Total duration: {}'.format(duration))

    def __show_statistics_summary(self, location, albums, songs, duration):
        """Show the summary of statistics for a location (e.g. playlists or music collection), including the number of
        albums as well as the number of songs and the total duration.

        :param str location: the location of the summary (e.g. playlists or music collection)
        :param int albums: the number of albums to show of a specific location.
        :param int songs: the number of songs to show of a specific location.
        :param str duration: the total duration to show of a specific location.
        """
        # Showing the total of albums in the location
        self.__display.show_triple(self.__display.show_validation, albums,
                                   '{} albums are in the {}'.format(albums, location),
                                   '1 album is in the {}'.format(location), '0 albums are in the {}'.format(location))

        # Showing the total of songs in the location
        self.__display.show_triple(self.__display.show_validation, songs,
                                   '{} songs are in the {}'.format(songs, location),
                                   '1 song is in the {}'.format(location), '0 songs are in the {}'.format(location))

        # Showing the total duration in the location
        duration = self.__convert_duration(float(duration))
        self.__display.show_validation('Total duration of the {}: {}'.format(location, duration))

    def __convert_duration(self, duration):
        """Convert a duration in seconds into a more readable format.

        :param float duration: the duration in seconds.
        :return str duration: the duration converted in a more readable format.
        """
        return str(datetime.timedelta(seconds=round(duration)))
