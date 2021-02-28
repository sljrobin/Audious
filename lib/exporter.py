#!/usr/bin/env python3
import pathlib
import shutil
import subprocess
import tinytag
import lib as audiouslib


class Exporter(object):
    def __init__(self, display, preferences, collection):
        """Initialize the Exporter object internally."""
        self.__display = display
        self.__prefs = preferences
        self.__coll = collection
        self.__play = audiouslib.playlists.Playlists(display, preferences)

        self.__collection_path_root = None
        self.__exportation_path_root = None
        self.__exportation_format = None
        self.__byte_to_gigabyte = 1 / (1024 * 1024 * 1024)
        self.__number_digits = 2

    def init(self):
        """Initialize the Exporter object."""
        self.__play.init()
        self.__exportation_format = self.__prefs.get_exportation_format()
        self.__exportation_path_root = self.__prefs.get_exportation_path_root()
        self.__collection_path_root = self.__prefs.get_collection_path_root()

    def export(self):
        """Main function that is used for the exportation process. First get all the songs that are available in the
        playlists. Give an overview of the hard drive space that will be required and ask confirmation before
        continuing. Export the songs in the format selected in the Preferences. Finally, export the playlists.
        """
        playlists_songs = self.__play.get_songs()

        exportation_size = self.__get_exportation_size(playlists_songs)
        self.__show_exportation_size(exportation_size)

        self.__show_exportation_format()
        self.__export_songs(playlists_songs)

        self.__show_exportation_playlists()
        self.__export_playlists()

    def __get_exportation_size(self, playlists_songs):
        """Calculate the total size of the exportation process in GigaBytes.

        :param list playlists_songs: list of all songs available in the playlists.
        :return float exportation_size: the total size of the exportation process in GigaBytes.
        """
        exportation_size = 0.
        for song in playlists_songs:
            try:
                exportation_size += pathlib.Path(song).stat().st_size
            except FileNotFoundError as f:
                self.__display.show_error('The following song was not found: \'{}\''.format(f.filename))

        exportation_size = round(exportation_size * self.__byte_to_gigabyte, self.__number_digits)
        return exportation_size

    def __show_exportation_size(self, exportation_size):
        """Show the exportation size that will be required.

        :param float exportation_size: the total size of the exportation process in GigaBytes.
        """
        self.__display.show_substep('Calculating exportation size')
        self.__display.show_warning_question('A maximum of {:,.2f} additional GB will be created on the disk. Shall '
                                             'we continue? (y/n): '.format(exportation_size))
        self.__display.show_warning('Note that only songs found in the music collection will be used to calculate the '
                                    'total exportation size.')
        self.__display.show_warning('If a song is not found, please ensure that it is in your music collection. If '
                                    'not, remove it from the playlist not to see again an error message about this '
                                    'song.')

    def __show_exportation_format(self):
        """Show the exportation format that is selected in the Preferences."""
        self.__display.show_substep('Exporting songs')
        self.__display.show_warning('If a song is not found, it will not be exported. Please ensure that the song is '
                                    'in your music collection. If not, remove it from the playlist not to see again an '
                                    'error message about this song.')
        if self.__exportation_format == 'flac':
            self.__display.show_validation('Exporting playlists in FLAC')
        elif self.__exportation_format == 'mp3':
            self.__display.show_validation('Exporting playlists in MP3')

    def __export_songs(self, playlists_songs):
        """Export all the songs that are available in the playlists. Indicate the number of songs to export. Also
        select the appropriate format for the exportation by checking that the file to convert has the '.flac'
        extension. If not, the file will be ignored. Initialize and increment a counter to get an overview of the
        exportation process.

        :param list playlists_songs: list of all songs available in the playlists.
        """
        total_playlists_songs = len(playlists_songs)
        self.__display.show_warning('Depending on the quantity of songs, this operation might take a while...')
        self.__display.show_validation('Quantity of songs: {}'.format(total_playlists_songs))
        cnt = 1

        for collection_path_song in playlists_songs:
            extension_flac = pathlib.Path(collection_path_song).suffix
            if extension_flac == '.flac':
                exportation_path_song = self.__create_exportation_architecture(collection_path_song)
                if self.__exportation_format == 'flac':
                    self.__export_song_flac(collection_path_song, exportation_path_song, cnt, total_playlists_songs)
                elif self.__exportation_format == 'mp3':
                    self.__export_song_mp3(collection_path_song, exportation_path_song, cnt, total_playlists_songs)
            else:
                pass
            cnt += 1

    def __show_exportation_playlists(self):
        """Show the playlists that will be exported during the exportation process."""
        self.__display.show_substep('Exporting playlists')

    def __create_exportation_architecture(self, collection_path_song):
        """Create the directories for the exportation, following the same architecture that is available in the music
        collection. Create all the parent directories if necessary.

        :param str collection_path_song: full path of the song in the music collection.
        :return str exportation_path_song: full path of the song in the exportation directory.
        """
        exportation_path_song = collection_path_song.replace(self.__collection_path_root, self.__exportation_path_root)
        exportation_path_album = exportation_path_song.rsplit('/', 1)[0]
        exportation_path_album = pathlib.Path(exportation_path_album)
        exportation_path_album.mkdir(parents=True, exist_ok=True)

        return exportation_path_song

    def __export_song_flac(self, collection_path_song, exportation_path_song, cnt, total_playlists_songs):
        """Export a song in FLAC contained in the playlists. As the music collection is only with FLAC songs, this
        function actually copies the files and does not perform any conversion. Copy the song in the exportation
        directory, while preserving the song OS metadata (e.g. date, last modification, etc.).

        :param str collection_path_song: full path of the song in the music collection.
        :param str exportation_path_song: full path of the song in the exportation directory.
        :param int cnt: counter for current song.
        :param int total_playlists_songs: total of songs to export.
        """
        try:
            shutil.copy2(collection_path_song, exportation_path_song)
            self.__show_exported_song(collection_path_song, exportation_path_song, cnt, total_playlists_songs)
        except FileNotFoundError as f:
            self.__display.show_error('The following song was not found: \'{}\''.format(f.filename))

    def __export_song_mp3(self, collection_path_song, exportation_path_song, cnt, total_playlists_songs):
        """Export a song in MP3 contained in the playlists. As the music collection is only with FLAC songs, this
        function actually converts the files from FLAC to MP3 via FFmpeg. After conversion, copy the song in the
        exportation directory, while preserving the song OS metadata (e.g. date, last modification, etc.).

        :param str collection_path_song: full path of the song in the music collection.
        :param str exportation_path_song: full path of the song in the exportation directory.
        :param int cnt: counter for current song.
        :param int total_playlists_songs: total of songs to export.
        """
        exportation_path_song = exportation_path_song.replace('.flac', '.mp3')
        try:
            command = 'ffmpeg -v quiet -y -i "{}" ' \
                      '-codec:a libmp3lame -qscale:a 0 -map_metadata 0 -id3v2_version 3 ' \
                      '"{}"'.format(collection_path_song, exportation_path_song)
            subprocess.run(command, shell=True)
            self.__show_exported_song(collection_path_song, exportation_path_song, cnt, total_playlists_songs)
        except FileNotFoundError as f:
            self.__display.show_error('The following song was not found: \'{}\''.format(f.filename))
        except NameError as n:
            self.__display.show_error('The following error occurred during the MP3 conversion:\n{}'.format(n))

    def __show_exported_song(self, collection_path_song, exportation_path_song, cnt, total_playlists_songs):
        """Show the song that has been successfully exported. Try to show song metadata first. If no metadata found,
        show only the name of the song and the corresponding album.

        :param str collection_path_song: full path of the song in the music collection.
        :param str exportation_path_song: full path of the song in the exportation directory.
        :param int cnt: counter for current song.
        :param int total_playlists_songs: total of songs to export.
        """
        try:
            tag = tinytag.TinyTag.get(collection_path_song)
            tag_title = tag.title
            tag_artist = tag.albumartist
            tag_album = tag.album
            self.__display.show_validation('Successfully exported ({}/{}): \'{}\' from \'{}\' in \'{}\''
                                           .format(cnt, total_playlists_songs, tag_title, tag_artist, tag_album))
        except tinytag.TinyTagException:
            exported_song_name = exportation_path_song.rsplit('/', 1)[1]
            exported_album_name = exportation_path_song.rsplit('/', 1)[0]
            exported_album_name = exported_album_name.rsplit('/', 1)[1] + '/'
            self.__display.show_validation('Successfully exported ({}/{}): \'{}\' in \'{}\''
                                           .format(cnt, total_playlists_songs, exported_song_name, exported_album_name))

    def __export_playlists(self):
        """Export the playlists that in the music collection. First get the path where the playlists will be exported.
        Then create the directory for the exportation. Create all the parent directories if necessary and finally
        copy the playlists in the exportation directory, while preserving the playlist OS metadata (e.g. date, etc.).
        """
        exportation_path_playlists = self.__prefs.get_exportation_path_playlists()
        pathlib.Path(exportation_path_playlists).mkdir(parents=True, exist_ok=True)
        self.__display.show_validation('Created directory for playlists')

        collection_paths_playlists = self.__play.get_playlists_paths()
        for collection_playlist in collection_paths_playlists:
            try:
                shutil.copy2(collection_playlist, exportation_path_playlists)
                self.__show_exported_playlist(collection_playlist)
            except FileNotFoundError as f:
                self.__display.show_error('The following playlist was not found: \'{}\'\nPlease ensure that this '
                                          'playlist is in your music collection and try again.\n'.format(f.filename))

    def __show_exported_playlist(self, collection_playlist):
        """Show the playlist that has been successfully exported.

        :param str collection_playlist: full path a playlist in the music collection.
        """
        exported_playlist_name = collection_playlist.rsplit('/', 1)[1]
        self.__display.show_validation('Successfully exported: \'{}\''.format(exported_playlist_name))
