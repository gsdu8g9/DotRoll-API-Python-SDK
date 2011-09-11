#!/usr/bin/python

import sys
import optparse
import unittest
import api

CURRENTAPIVERSION='1.0'

class ArgumentParser:
    """
    This class parses command line options and dispatches them to the DotRoll
    API lib.
    """

    def __init__(self):
        """
        This function sets up the option parser to use for command line
        processing.
        """
        self.parser = optparse.OptionParser(description='Access the DotRoll'
                                                        ' API functionality'
                                                        ' from command line.')
        apigroup = optparse.OptionGroup(self.parser,
                                        'API options',
                                        'These options modify, how the API'
                                        ' endpoint is connected')
        apigroup.add_option('--apikey',
                            type='string',
                            help='The API key used to access the service')
        apigroup.add_option('--username',
                            type='string',
                            help='The username used to authenticate with'
                                 ' the API')
        apigroup.add_option('--password',
                            type='string',
                            help='The password used to authenticate with'
                                 ' the API')
        apigroup.add_option('--apiendpoint',
                            type='string',
                            help='The endpoint URL used to access the'
                                 ' service. You don\'t normally need'
                                 ' to change this. Defaults to'
                                 ' "%default"',
                            default='https://webservices.dotroll.com/rest')
        apigroup.add_option('--apiversion',
                            type='string',
                            help='The API version used to access the service.'
                                 ' You don\'t normally need to change this.'
                                 ' Defaults to "%default"',
                            default=CURRENTAPIVERSION)
        self.parser.add_option_group(apigroup)
        actiongroup = optparse.OptionGroup(self.parser,
                                           'Actions',
                                           'These options change, which action'
                                           ' is called. They are mutually'
                                           ' exclusive.')
        actiongroup.add_option('--getdomainprices',
                               action='store_true',
                               help='Download domain pricelist')
        actiongroup.add_option('--gethostingprices',
                               action='store_true',
                               help='Download hosting pricelist')
        actiongroup.add_option('--getvpsprices',
                               action='store_true',
                               help='Download VPS pricelist')
        actiongroup.add_option('--getdomainavailability',
                               action='store_true',
                               help='Check, if a domain is available for'
                                    ' registration.')
        actiongroup.add_option('--getdomainlist',
                               action='store_true',
                               help='Download a list of all domains owned'
                                    ' by the user')
        self.parser.add_option_group(actiongroup)
        pricegroup = optparse.OptionGroup(self.parser,
                                          'Price options',
                                          'Sets options for pricelist'
                                          ' download')
        pricegroup.add_option('--currency',
                              help='Sets currency for pricelist download'
                                   ' operation.')
        self.parser.add_option_group(pricegroup)
        domaingroup = optparse.OptionGroup(self.parser,
                                          'Domain options',
                                          'Sets options for domain'
                                          ' functions')
        domaingroup.add_option('--domainname',
                              help='Sets the domain name for the current '
                                   'operation')
        self.parser.add_option_group(domaingroup)

    def usage(self):
        """
        This function provides an external option to print the usage text.
        """
        self.parser.print_help()

    def error(self, message):
        """
        This function provides an external option to raise a parser error and
        terminate the program.
        """
        self.parser.error(message)

    def parse(self, args):
        """
        This function parses and validates a set of arguments.
        Returns a tupple (function, arguments)
        """
        if len(args) < 2:
            raise ArgumentError('Incorrect number of arguments')
        (options, args) = self.parser.parse_args(args)
        actionargs=['getdomainprices', 'gethostingprices', 'getvpsprices',
                    'getdomainavailability', 'getdomainlist']
        for i in actionargs:
            for j in actionargs:
                if i != j and getattr(options, i) and getattr(options, j):
                    raise ArgumentError('Only one action can be called at a'
                                        ' time. --' + i + ' and --' + j +
                                        ' are incompatible.')
        if ((options.getdomainprices or options.gethostingprices or
            options.getvpsprices) and options.currency
            not in ['HUF', 'EUR', 'USD']):
            raise ArgumentError('A valid currency code is required for'
                                ' pricelist download')
        func = None
        for i in actionargs:
            if getattr(options, i):
                func = i
        return (func, options)

    def call(self, func, options):
        """
        Call corresponding API function with arguments
        """
        qh = api.HTTPQueryHandler(options.apiendpoint, options.apiversion,
                                  options.apikey, options.username,
                                  options.password)
        apih = api.ActionHandler(qh)
        result = ''
        if func == 'getdomainprices':
            res = apih.get_domain_prices(options.currency)
            result = []
            for i in res['prices'].keys():
                for j in res['prices'][i].keys():
                    result.append([i, j, res['prices'][i][j]['gross'],
                                   res['prices'][i][j]['net']])
        if func == 'gethostingprices':
            res = apih.get_hosting_prices(options.currency)
            result = []
            for i in res['prices'].keys():
                for j in res['prices'][i].keys():
                    result.append([i, j, res['prices'][i][j]['gross'],
                                   res['prices'][i][j]['net']])
        if func == 'getvpsprices':
            res = apih.get_vps_prices(options.currency)
            result = []
            for i in res['prices'].keys():
                for j in res['prices'][i].keys():
                    result.append([i, j, res['prices'][i][j]['gross'],
                                   res['prices'][i][j]['net']])
        if func == 'getdomainavailability':
            res = apih.get_domain_availability(options.domainname)
            result = [[res['result']]]
        if func == 'getdomainlist':
            res = apih.get_domain_list()
            result = []
            for row in res['domains']:
                rowresult = []
                for j in row.keys():
                    rowresult.append(row[j])
                result.append(rowresult)
        return result

    def parse_and_call(self, args):
        """
        Parse arguments and call function
        """
        (func, options) = self.parse(args)
        return self.call(func, options)


class ArgumentError(Exception):
    """
    This exception indicates, that an error has occured parsing command line
    arguments.
    """

    def __init__(self, message):
        """
        Initializes the class with an error message.
        """
        self.message = message

    def __str__(self):
        """
        Returns the error message passed to the Exception in __init__()
        """
        return self.message


###############################################################################
# Unit testing code                                                           #
###############################################################################


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
        Tests, if the command line interface correctly fails, if the user tries
        to submit a contact and domain registration at the same time, etc.
        """
        parser = ArgumentParser()
        try:
            parser.parse(['dotrollcli', '--getdomainlist'])
        except ArgumentError:
            self.fail('Calling a single action raises an ArgumentError')
        self.assertRaises(ArgumentError, parser.parse, ['dotrollcli',
                                                        '--getdomainprices',
                                                        '--gethostingprices'])
        self.assertRaises(ArgumentError, parser.parse, ['dotrollcli',
                                                        '--getdomainprices',
                                                        '--getvpsprices'])
        self.assertRaises(ArgumentError, parser.parse, ['dotrollcli',
                                                        '--gethostingprices',
                                                        '--getvpsprices'])
        self.assertRaises(ArgumentError, parser.parse, ['dotrollcli',
                                                        '--gethostingprices',
                                                        '--getdomainavailability'])
        self.assertRaises(ArgumentError, parser.parse, ['dotrollcli',
                                                        '--getvpsprices',
                                                        '--getdomainlist'])


if __name__ == '__main__':
    unittest.main()
