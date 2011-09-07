#!/usr/bin/python

import sys
import optparse
import unittest

CURRENTAPIVERSION='1.0'

class ArgumentParser:
    """
    This class parses command line options and dispatches them to the DotRoll API lib.
    """

    def __init__(self):
        """
        This function sets up the option parser to use for command line processing.
        """
        self.parser = optparse.OptionParser(description='Access the DotRoll API functionality from command line.')
        self.parser.add_option('--apikey', type='string', dest='apikey', help='The API key used to access the service')
        self.parser.add_option('--apiendpoint', type='string', dest='apiendpoint',
                               help='The endpoint URL used to access the service. You don\'t normally need to change this. Defaults to "%default"',
                               default='https://webservices.dotroll.com/rest')
        self.parser.add_option('--apiversion', type='string', dest='apiversion',
                               help='The API version used to access the service. You don\'t normally need to change this. Defaults to "%default"',
                               default=CURRENTAPIVERSION)
        self.parser.add_option('--registercontact', dest='registercontact', action='store_true', help='Invoke contact registration')
        self.parser.add_option('--registerdomain', dest='registerdomain', action='store_true', help='Invoke domain registration')

    def usage(self):
        """
        This function provides an external option to print the usage text.
        """
        self.parser.print_help()

    def error(self, message):
        """
        This function provides an external option to raise a parser error and terminate the program.
        """
        self.parser.error(message)

    def parse(self, args):
        """
        This function parses and validates a set of arguments.
        """
        (options, args) = self.parser.parse_args(args)
        if len(args) < 2:
            raise ArgumentError('Incorrect number of arguments')
        if options.registercontact and options.registerdomain:
            raise ArgumentError('Only one action can be called at a time. --registercontact and --registerdomain are incompatible.')


class ArgumentError(Exception):
    """
    This exception indicates, that an error has occured parsing command line arguments.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ArgumentParserTest(unittest.TestCase):
    """
    This class tests the DotRoll.ArgumentParser class.
    """

    def test_zero_arguments(self):
        """
        Tests, if the parse run fails, if there are no arguments.
        """
        parser = ArgumentParser()
        self.assertRaises(ArgumentError, parser.parse, ['dotrollcli'])

    def test_incompatible_actions(self):
        """
        Tests, if the command line interface correctly fails, if the user tries to
        submit a contact and domain registration at the same time.
        """
        parser = ArgumentParser()
        self.assertRaises(ArgumentError, parser.parse, ['--registercontact', '--registerdomain'])


if __name__ == '__main__':
    unittest.main()
