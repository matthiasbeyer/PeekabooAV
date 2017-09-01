###############################################################################
#                                                                             #
# Peekaboo Extended Email Attachment Behavior Observation Owl                 #
#                                                                             #
# config.py                                                                   #
###############################################################################
#                                                                             #
# Copyright (C) 2016-2017  science + computing ag                             #
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


import sys
import logging
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError
from peekaboo import logger


class PeekabooConfig(object):
    """
    This class represents the Peekaboo configuration file.

    :author: Sebastian Deiss
    """
    def __init__(self, config_file='./peekaboo.conf'):
        self.__config = None
        self.user = None
        self.group = None
        self.pid_file = None
        self.sock_file = None
        self.log_level = logging.INFO
        self.interpreter = None
        self.chown2me_exec = None
        self.worker_count = 3
        self.sample_base_dir = None
        self.job_hash_regex = None
        self.use_debug_module = None
        self.db_url = None
        self.cuckoo_storage = None
        self.cuckoo_exec = None
        self.cuckoo_submit = None
        self.db_con = None
        ##############################################
        # setup default logging to log any errors during the
        # parsing of the config file.
        self.__setup_logging()
        self.__parse(config_file)

    def __parse(self, config_file):
        config = SafeConfigParser()
        config.read(config_file)
        self.__config = config
        try:
            log_level = config.get('global', 'log_level')
            self.log_level = self.__parse_log_level(log_level)
            self.user = config.get('global', 'user')
            self.group = config.get('global', 'group')
            self.pid_file = config.get('global', 'pid_file')
            self.sock_file = config.get('global', 'socket_file')
            self.interpreter = config.get('global', 'interpreter')
            self.chown2me_exec = config.get('global', 'chown2me_exec')
            self.worker_count = int(config.get('global', 'worker_count'))
            self.sample_base_dir = config.get('global', 'sample_base_dir')
            self.job_hash_regex = config.get('global', 'job_hash_regex')
            self.use_debug_module = True if config.get('global', 'use_debug_module') == \
                                            'yes' else False
            self.db_url = config.get('db', 'url')
            self.cuckoo_storage = config.get('cuckoo', 'storage_path')
            self.cuckoo_exec = config.get('cuckoo', 'exec')
            self.cuckoo_submit = config.get('cuckoo', 'submit')
            logger.setLevel(self.log_level)
        except NoSectionError as e:
            logger.critical('configuration section not found')
            logger.exception(e)
            sys.exit(1)
        except NoOptionError as e:
            logger.critical('configuration option not found')
            logger.exception(e)
            sys.exit(1)

    def change_log_level(self, log_level):
        """
        Overwrite the log level from the configuration file.

        :param log_level: The new log level.
        """
        ll = self.__parse_log_level(log_level)
        self.log_level = ll
        logger.setLevel(ll)

    def add_db_con(self, db_con):
        self.db_con = db_con

    def get_db_con(self):
        if self.db_con:
            return self.db_con
        raise ValueError('Database connection is not configured.')

    def __parse_log_level(self, log_level):
        if log_level == 'CRITICAL':
            return logging.CRITICAL
        elif log_level == 'ERROR':
            return logging.ERROR
        elif log_level == 'WARNING':
            return logging.WARNING
        elif log_level == 'INFO':
            return logging.INFO
        elif log_level == 'DEBUG':
            return logging.DEBUG

    def __setup_logging(self):
        """
        Setup logging to console.
        """
        logger.setLevel(self.log_level)
        # log format
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - '
                                          '%(module)s - %(threadName)s - '
                                          '%(process)s - %(message)s')
        # create console handler and set level to debug
        to_console_log_handler = logging.StreamHandler()
        to_console_log_handler.setLevel(logging.DEBUG)
        to_console_log_handler.setFormatter(log_formatter)
        logger.addHandler(to_console_log_handler)
        logger.setLevel(self.log_level)

    def __str__(self):
        sections = {}
        for section in self.__config.sections():
            sections[section] = {}
            for key, value in self.__config.items(section):
                sections[section][key] = value
        return '<PeekabooConfig(%s)>' % str(sections)

    __repr__ = __str__
