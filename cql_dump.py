#!/usr/bin/env python

import argparse
import logging
import cassandra.cluster
from cassandra.encoder import cql_encode_all_types

def main():
    parser = argparse.ArgumentParser(description='Dump cassandra data in cql format.')
    parser.add_argument('keyspace')
    parser.add_argument('column_family')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    

    session = setup_session(args)

    session.set_keyspace(args.keyspace)

    session.row_factory = make_row_factory(args.keyspace, args.column_family)
    session.default_fetch_size = 5

    rows = session.execute("SELECT * FROM %s" % (args.column_family,))

    for r in rows:
        print r+';'


def make_row_factory(keyspace, column_family):
    def _factory(colnames, rows):
        columns = '"'+'", "'.join(colnames)+'"'
        for r in rows:
            r = map(cql_encode_all_types, r)
            values = ', '.join(r)
            yield "INSERT INTO %s.%s (%s) VALUES (%s)" % (keyspace, column_family, columns, values)
    
    return _factory
    


def setup_session(args):
    cluster = cassandra.cluster.Cluster(['54.85.130.35'])
    session = cluster.connect()
    
    return session



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()