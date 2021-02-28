#!/usr/bin/env python3
import colorama
import sys


class Display(object):
    def __init__(self):
        """Initialize the Display object internally."""
        self.__header_main = '\u266A '
        self.__header = '\u2192 '

    def show_error(self, message):
        """Display an error message.

        :param str message: error message to display.
        """
        style = colorama.Style.NORMAL + colorama.Fore.RED + message + colorama.Style.RESET_ALL
        print(style)

    def show_picked_album_even(self, album):
        """Display a picked album (even in the list).

        :param str album: the even album to display.
        """
        style = colorama.Style.NORMAL + colorama.Fore.CYAN + ' ' * 2 + '\u2b91  ' + album + colorama.Style.RESET_ALL
        print(style)

    def show_picked_album_odd(self, album):
        """Display a picked album (odd in the list).

        :param str album: the odd album to display.
        """
        style = colorama.Style.NORMAL + colorama.Fore.GREEN + ' ' * 2 + '\u2b91  ' + album + colorama.Style.RESET_ALL
        print(style)

    def show_step(self, message):
        """Display a step message.

        :param str message: step message to display.
        """
        style = colorama.Style.BRIGHT + colorama.Fore.RED + self.__header_main + message + colorama.Style.RESET_ALL
        print(style)

    def show_substep(self, message):
        """Display a substep message.

        :param str message: substep message to display.
        """
        style = colorama.Style.BRIGHT + colorama.Fore.WHITE + '\n' + self.__header + message + colorama.Style.RESET_ALL
        print(style)

    def show_triple(self, method, total, plural, singular, zero):
        """Display three messages of the same type. Also check if the Display object has an attribute called with an
        internal Display method name, then check if that attribute is a method, and then call it.

        :param func method: internal Display method.
        :param int total: total (e.g. of albums).
        :param str plural: message in plural.
        :param str singular: message in singular.
        :param str zero: message if total is equal to 0.
        """
        callable_method = getattr(Display, method.__name__, None)
        if callable(callable_method):
            if total > 1:
                method(plural)
            elif total == 1:
                method(singular)
            else:
                method(zero)
        else:
            self.show_error('An error occurred while printing. Please try restart the program and try again.')

    def show_validation(self, message):
        """Display a validation message.

        :param str message: validation message to display.
        """
        style = colorama.Style.NORMAL + colorama.Fore.BLUE + self.__header + message + colorama.Style.RESET_ALL
        print(style)

    def show_warning(self, message):
        """Display a warning message.

        :param str message: validation message to display.
        """
        style = colorama.Style.NORMAL + colorama.Fore.YELLOW + self.__header + message + colorama.Style.RESET_ALL
        print(style)

    def show_warning_question(self, message):
        """Display a warning question.

        :param str message: question to display.
        """
        style = colorama.Style.NORMAL + colorama.Fore.YELLOW + self.__header + message + colorama.Style.RESET_ALL
        while True:
            answer = input(style).lower().strip()
            if answer in ('y', 'yes'):
                return answer in ('y', 'yes')
            elif answer in ('n', 'no'):
                self.show_error('Quitting...')
                sys.exit(0)
            else:
                self.show_error('You must answer \'yes\'/\'y\' or \'no\'/\'n\').')
