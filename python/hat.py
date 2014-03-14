#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from argparse import ArgumentParser
from collections import OrderedDict
import logging
import sys
import time

import ddp

LOG_LEVELS = (
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG
)

LOG_LEVEL_TO_NAMES = OrderedDict((level, logging.getLevelName(level).lower())
                                 for level in LOG_LEVELS)
LOG_NAME_TO_LEVEL = OrderedDict((name, level)
                                for level, name in LOG_LEVEL_TO_NAMES.items())


class HatController(object):
    def __init__(self, url):
        self._conn = ddp.DdpConnection(
            url,
            received_message_callback=self._recieved_message,
        )
        self._id = None
        self._is_ready = False
        self._is_activated = False

    def _recieved_message(self, message):
        hat = u'hat'
        is_activated = u'isActivated'
        name = u'name'

        if isinstance(message, ddp.ReadyMessage):
            self._is_ready = True
        elif isinstance(message, ddp.AddedMessage):
            fields = message.fields
            if fields.get(name) == hat:
                self._id = message.id_
                self._set_hat_state(fields.get(is_activated, False))
        elif isinstance(message, ddp.ChangedMessage):
            fields = message.fields
            if message.id_ == self._id and is_activated in fields:
                self._set_hat_state(fields[is_activated])
        else:
            logger.debug('Ignoring message: %s', message)

    def _set_hat_state(self, is_activated):
        if self._is_activated == is_activated:
            return
        self._is_activated = is_activated

        if self._is_activated:
            logger.debug('Hat activated')
        else:
            logger.debug('Hat deactivated')

    def connect(self):
        self._conn.connect()
        msg = ddp.SubMessage('1', 'hat')
        self._conn.send(msg)

    def disconnect(self):
        self._conn.disconnect()


def main(argv=None):
    global logger

    if argv is None:
        argv = sys.argv

    parser = ArgumentParser()
    parser.add_argument('-l', '--log-level', choices=LOG_NAME_TO_LEVEL.keys(),
                        default=LOG_LEVEL_TO_NAMES[logging.INFO])
    parser.add_argument('-s', '--server', default='127.0.0.1:3000')
    args = parser.parse_args(args=argv[1:])

    logging.basicConfig(
        datefmt='%H:%M:%S',
        format='[%(levelname).1s %(asctime)s] %(message)s',
        level=LOG_NAME_TO_LEVEL[args.log_level]
    )
    logger = logging.getLogger(__name__)

    url = ddp.ServerUrl(args.server)
    hat_controller = HatController(url)
    try:
        hat_controller.connect()
        wait_for_user_to_exit()
    finally:
        try:
            hat_controller.disconnect()
        except BaseException as e:
            logger.exception(
                'An error occured while disconnecting from the DDP server.'
            )

    return 0


def wait_for_user_to_exit():
    try:
        print('Press ^C to exit')
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    exit(main())

