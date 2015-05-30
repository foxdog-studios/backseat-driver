#!/usr/bin/env python

import signal
import threading
import time
from argparse import ArgumentParser
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from MeteorClient import MeteorClient

from pyfirmata import Arduino


def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--device', default='hat', dest='device_id')
    parser.add_argument('-p', '--port', default='/dev/ttyACM0',
                        dest='port_path', type=Path)
    parser.add_argument('-u', '--url', default='ws://127.0.0.1:3000/websocket')
    args = parser.parse_args()

    is_stopping = False

    def stop(signum, frame):
        nonlocal is_stopping
        is_stopping = True

    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, stop)

    def only_device(func):
        @wraps(func)
        def wrapper(collection, id_, *args):
            if collection == 'devices' or id_ == args.device_id:
                return func(collection, id_, *args)
        return wrapper

    @only_device
    def added_or_changed(collection, id_, fields, *args):
        set_activated(fields.get('isActivated', False))

    @only_device
    def removed(collection, id_):
        set_activated(False)

    lock = threading.Lock()
    board = None

    def set_activated(is_activated):
        with lock:
            if board is not None:
                value = 1 if is_activated else 0
                board.digital[9].write(value)

    print('Press ^C to exit')

    with create_board(args.port_path) as board_tmp:
        with lock:
            board = board_tmp
        with create_client(args.url) as client:
            client.on('added', added_or_changed)
            client.on('changed', added_or_changed)
            client.on('removed', removed)
            with subscription(client, 'device', params=[args.device_id]):
                while not is_stopping:
                    time.sleep(1)
        set_activated(False)


@contextmanager
def create_board(port_path):
    board = Arduino(str(port_path))
    yield board
    board.exit()


@contextmanager
def create_client(url):
    client = MeteorClient(url)
    client.connect()
    yield client
    client.close()


@contextmanager
def subscription(client, name, *args, **kwargs):
    client.subscribe(name, *args, **kwargs)
    yield
    client.unsubscribe(name)


if __name__ == '__main__':
    main()

