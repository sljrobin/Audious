#!/usr/bin/env python3
import argparse
import sys
import lib as audiouslib


def main():
    """Main entry point. Handle an argument parser and the different options."""
    display = audiouslib.display.Display()
    preferences = audiouslib.preferences.Preferences(display)
    collection = audiouslib.collection.Collection(display, preferences)

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('-e', '--export', action='store_true',
                        help='Export the playlists in FLAC or in MP3')
    parser.add_argument('-p', '--pick', action='store_true',
                        help='Pick the albums from the music collection that are not in the playlists')
    parser.add_argument('-s', '--stats', action='store_true',
                        help='Provide statistics of the music collection and the playlists')
    args = parser.parse_args()

    # Action: pick not listened albums
    if args.pick:
        display.show_step('Picking albums to listen...')
        picker = audiouslib.picker.Picker(display, preferences, collection)
        picker.init()
        picker.pick_albums()
        display.show_step('Picking albums to listen: done!')
    # Action: provide music collection statistics
    elif args.stats:
        display.show_step('Providing statistics of the music collection...')
        stats = audiouslib.statistics.Statistics(display, preferences, collection)
        stats.init()
        stats.compute()
        display.show_step('Providing statistics of the music collection: done!')
    # Action: export playlists
    elif args.export:
        display.show_step('Exporting the playlists...')
        exporter = audiouslib.exporter.Exporter(display, preferences, collection)
        exporter.init()
        exporter.export()
        display.show_step('Exporting the playlists: done!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nOperation interrupted')
        sys.exit(1)
