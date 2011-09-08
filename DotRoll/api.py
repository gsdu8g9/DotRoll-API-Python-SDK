#!/bin/bash

import unittest
import json

class QueryHandler:
    def set_expected_error(self, errorcode):
        pass

    def get(self, uri):
        pass

    def delete(self, uri):
        pass

    def post(self, uri, data):
        pass

    def put(self, uri, data):
        pass

    def encode(self, string):
        pass

class ActionHandler:
    def __init__(self, queryhandler):
        self.queryhandler = queryhandler

    def get_domain_prices(self, currency):
        return self.queryhandler.get('domain/prices/' + currency)

    def get_hosting_prices(self, currency):
        return self.queryhandler.get('hosting/prices/' + currency)

    def get_vps_prices(self, currency):
        return self.queryhandler.get('vps/prices/' + currency)

    def get_domain_availability(self, domainname):
        return self.queryhandler.get('domain/search/' +
                                 self.queryhandler.encode(domainname))

    def get_domain_list(self):
        return self.queryhandler.get('domain/list/')

if __name__ == '__main__':
    unittest.main()