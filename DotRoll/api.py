#!/usr/bin/python

import unittest, json, httplib, urllib

class QueryHandler:
    """
    This class is the abstract query handler for raw HTTP queries.
    """
    endpoint = ''
    apikey = ''
    username = ''
    password = ''
    def __init__(self, endpoint, apikey, username, password):
        """
        Initialize the QueryHandler with authentication information.
        """
        self.endpoint = endpoint
        self.apikey = apikey
        self.username = username
        self.password = password

    def get(self, url):
        """
        Perform a HTTP GET query.
        """
        raise NotImplementedError('Use a subclass of QueryHandler')

    def delete(self, url):
        """
        Perform a HTTP DELETE query.
        """
        raise NotImplementedError('Use a subclass of QueryHandler')

    def post(self, url, data):
        """
        Perform a HTTP POST query.
        """
        raise NotImplementedError('Use a subclass of QueryHandler')

    def put(self, url, data):
        """
        Perform a HTTP PUT query.
        """
        raise NotImplementedError('Use a subclass of QueryHandler')

    def encode(self, rawstring):
        """
        Encode a string to make it usable in an URL
        """
        return urllib.quote(str(rawstring))


class QueryFailed(Exception):
    """
    This exception indicates, that a given query has somehow failed, containing
    details in the description.
    """
    def __init__(self, description):
        """
        Initialize exception with a description.
        """
        self.description = description
        super(QueryFailed, self).__init__()
    def __str__(self):
        """
        Return a meaningfull string representation of th exception.
        """
        return 'Query failed: ' + self.description


class ActionHandler:
    """
    This class calls the QueryHandler with appropriate parameters and
    transforms the data that comes back.
    """
    def __init__(self, queryhandler):
        """
        This function initializes the backend query handler.
        """
        self.queryhandler = queryhandler

    def get_domain_prices(self, currency):
        """
        This function downloads the domain pricelist in a given currency.
        """
        return self.queryhandler.get('domain/prices/' + currency)

    def get_hosting_prices(self, currency):
        """
        This function downloads the hosting pricelist in a given currency.
        """
        return self.queryhandler.get('hosting/prices/' + currency)

    def get_vps_prices(self, currency):
        """
        This function downloads the VPS pricelist in a given currency.
        """
        return self.queryhandler.get('vps/prices/' + currency)

    def get_domain_availability(self, domainname):
        """
        This function checks, if a domain is available for registration.
        """
        return self.queryhandler.get('domain/search/' +
                                     self.queryhandler.encode(domainname))

    def get_domain_list(self):
        """
        This function downloads a list of all domains registered under the
        current user.
        """
        return self.queryhandler.get('domain/list')


###############################################################################
# Unit testing code                                                           #
###############################################################################


class MockQueryHandler(QueryHandler):
    """
    This is the mock query handler used for unit testing.
    To make it work, you have to feed it "expectations". The queries
    are then matched against these expectations. The result attached to
    them is returned as a result.
    """
    expectations = []
    def add_expectation(self, expected_url, expected_query_type,
                        expected_body, response_code, response_body):
        """
        Queue an expectation.
        """
        self.expectations.append({'expected_url':expected_url,
                                  'expected_query_type':expected_query_type,
                                  'expected_body':expected_body,
                                  'response_code':response_code,
                                  'response_body':response_body})

    def get_expectation(self):
        """
        Fetch one expectation off the beginning of the expectations list.
        """
        return self.expectations.pop(0)

    def check_expectation(self, url, query_type, body):
        """
        Check a given request against the next expectation in the list.
        """
        exp = self.get_expectation()
        if exp['expected_url'] != url:
            raise ExpectationFailed('Expected URL ' + exp['expected_url'] +
                                    ' , got ' + url)
        if exp['expected_query_type'] != query_type:
            raise ExpectationFailed('Expected ' + exp['expected_query_type'] +
                                    ' query, got ' + query_type + ' query')
        if exp['expected_body'] != body:
            raise ExpectationFailed('Expectation body mismatch. Expected '
                                    'body: ' . exp['expected_body'] + ' '
                                    'actual body: ' + str(body))
        return {'code': exp['response_code'], 'body': exp['response_body']}

    def get(self, url):
        """
        Perform a mock HTTP GET query and parse the results as a JSON string.
        """
        result = self.check_expectation(url, 'get', '')
        if result['code'] != 200:
            raise QueryFailed()
        return json.loads(result['body'])

    def delete(self, url):
        """
        Perform a mock HTTP DELETE query and parse the results as a JSON
        string.
        """
        result = self.check_expectation(url, 'delete', '')
        if result['code'] != 200:
            raise QueryFailed()
        return json.loads(result.body)

    def post(self, url, data):
        """
        Perform a mock HTTP POST query and parse the results as a JSON
        string.
        """
        result = self.check_expectation(url, 'post', 'data')
        if result['code'] != 201:
            raise QueryFailed()
        return json.loads(result['body'])

    def put(self, url, data):
        """
        Perform a mock HTTP PUT query and parse the results as a JSON
        string.
        """
        result = self.check_expectation(url, 'put', 'data')
        if result['code'] != 200 and result['code'] != 201 and result['code'] != 204:
            raise QueryFailed()
        return json.loads(result['body'])


class ExpectationFailed(Exception):
    """
    This exception is used to indicate, that an expectation in MockQueryHandler
    has not been matched.
    """
    def __init__(self, description):
        """
        Initialize exception with a description.
        """
        self.description = description
        super(ExpectationFailed, self).__init__()
    def __str__(self):
        """
        Return a meaningfull string representation of th exception.
        """
        return 'Expectation failed: ' + self.description


class ActionHandlerTest(unittest.TestCase):
    def test_get_prices(self):
        """
        Test querying the service price lists.
        This test uses mock testing, it does not actually perform
        HTTP queries.
        """
        qh = MockQueryHandler('', '', '')
        ah = ActionHandler(qh)
        qh.add_expectation('domain/prices/HUF', 'get', '', 200, '{"new": 1}')
        qh.add_expectation('domain/prices/EUR', 'get', '', 200, '{"new": 2}')
        qh.add_expectation('hosting/prices/HUF', 'get', '', 200, '{"new": 3}')
        qh.add_expectation('hosting/prices/EUR', 'get', '', 200, '{"new": 4}')
        qh.add_expectation('vps/prices/HUF', 'get', '', 200, '{"new": 5}')
        qh.add_expectation('vps/prices/EUR', 'get', '', 200, '{"new": 6}')
        self.assertEqual(ah.get_domain_prices('HUF'), {'new': 1})
        self.assertEqual(ah.get_domain_prices('EUR'), {'new': 2})
        self.assertEqual(ah.get_hosting_prices('HUF'), {'new': 3})
        self.assertEqual(ah.get_hosting_prices('EUR'), {'new': 4})
        self.assertEqual(ah.get_vps_prices('HUF'), {'new': 5})
        self.assertEqual(ah.get_vps_prices('EUR'), {'new': 6})

    def test_get_domain_availability(self):
        """
        Test querying the domain availability.
        This test uses mock testing, it does not actually perform
        HTTP queries.
        """
        qh = MockQueryHandler('', '', '')
        ah = ActionHandler(qh)
        qh.add_expectation('domain/search/janoszen.hu', 'get', '', 200,
                           '{"status": "available"}');
        self.assertEqual(ah.get_domain_availability('janoszen.hu'),
                         {'status': 'available'})

    def test_get_domain_list(self):
        """
        Test querying the domain list of the current user.
        This test uses mock testing, it does not actually perform
        HTTP queries.
        """
        qh = MockQueryHandler('', '', '')
        ah = ActionHandler(qh)
        qh.add_expectation('domain/list', 'get', '', 200,
                           '["janoszen.hu"]');
        self.assertEqual(ah.get_domain_list(), ['janoszen.hu'])


if __name__ == '__main__':
    unittest.main()
