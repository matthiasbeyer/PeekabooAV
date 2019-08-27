#!/usr/bin/env python
# encoding: utf-8

###############################################################################
#                                                                             #
# Peekaboo Extended Email Attachment Behavior Observation Owl                 #
#                                                                             #
# peekaboo-util.py                                                            #
###############################################################################
#                                                                             #
# Copyright (C) 2016-2019  science + computing ag                             #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or (at       #
# your option) any later version.                                             #
#                                                                             #
# This program is distributed in the hope that it will be useful, but         #
# WITHOUT ANY WARRANTY; without even the implied warranty of                  #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU           #
# General Public License for more details.                                    #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################


from __future__ import print_function
from os import path, linesep
from argparse import ArgumentParser
import socket
import re
import logging
import time
import psutil
import sys
import inspect

currentdir = path.dirname(path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = path.dirname(currentdir)
sys.path.insert(0,parentdir)
from peekaboo.db import PeekabooDatabase


logging.basicConfig()
logger = logging.getLogger(__name__)


class PeekabooUtil(object):
    """ Utility fo interface with Peekaboo API over the socket connection """
    def __init__(self, socket_file):
        logger.debug('Initialising PeekabooUtil')
        self.peekaboo = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        logger.debug('Opening socket %s', socket_file)
        self.peekaboo.connect(socket_file)

    def send_receive(self, request, output=False):
        """ Send request to peekaboo and return its answer """
        logger.debug('Sending request: %s', request)

        self.peekaboo.send(request)
        print ('Waiting for response...')

        buf = ''
        while True:
            data = self.peekaboo.recv(1024)
            if data:
                buf += data
                if output:
                    print(data, end='')
            else:
                self.peekaboo.close()
                break
        logger.debug('Received from peekaboo: %s', buf)
        return buf

    def scan_file(self, filename):
        """ Scan the supplied filenames with peekaboo and output result """
        result_regex = re.compile(r'.*wurde als',
                                  re.MULTILINE + re.DOTALL + re.UNICODE)
        file_snippets = []
        for filename in filename:
            file_snippets.append('{ "full_name": "%s" }' % path.abspath(filename))
        request = '[ %s ]' % ', '.join(file_snippets)

        buf = self.send_receive(request)

        for result in buf.splitlines():
            output = result_regex.search(result)
            if output:
                if 'bad' in result:
                    print(result)
                logger.info(result)

    def clean_db(self, url, seconds=None, result=None):
        """ Remove entries from database older than seconds and with result result. """
        peekaboodb = PeekabooDatabase(url)
        peekaboodb.cleanup(seconds, result)
        print('Database cleaned')

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                        help='List results of all files not only bad ones')
    parser.add_argument('-vv', '--verbose2', action='store_true', required=False,
                        help='List detailed analysis results of every rule')
    parser.add_argument('-d', '--debug', action='store_true', required=False,
                        help='Output additional diagnostics')
    parser.add_argument('-s', '--socket_file', action='store', required=True,
                        help='Path to Peekaboo\'s socket file')

    scan_file_parser = subparsers.add_parser('scan_file',
                                             help='Scan a file and report it')
    scan_file_parser.add_argument('-f', '--filename', action='append', required=True,
                                  help='Path to the file to scan. Can be given more '
                                       'than once to scan multiple files.')
    scan_file_parser.set_defaults(func=command_scan_file)

    clean_db = subparsers.add_parser('clean_db', help='Clean database from specified entries.'
                                                      'Several options imply and')
    clean_db.add_argument('-u', '--db-url', requered=True,
                          help='URL to database.')
    clean_db.add_argument('-s', '--seconds', required=False,
                          help='Entries older than seconds will be removed.')
    clean_db.add_argument('-r', '--result', required=False,
                          help='Entries with result will be removed.')
    clean_db.set_defaults(func=command_clean_db)

    args = parser.parse_args()

    logger.setLevel(logging.ERROR)
    if args.verbose:
        logger.setLevel(logging.INFO)
    if args.verbose2 or args.debug:
        logger.setLevel(logging.DEBUG)

    args.func(args)

def command_scan_file(args):
    """ Handler for command scan_file """
    util = PeekabooUtil(args.socket_file)
    util.scan_file(args.filename)

def command_clean_db(args):
    """ Handler for command clean_db """
    util = PeekabooUtil(args.socket_file)
    util.clean_db(args.db-url, seconds=args.seconds, result=args.result)

if __name__ == "__main__":
    main()