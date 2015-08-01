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
    parser.add_argument('-p', '--port', default='/dev/partyhat',
                        dest='port_path', type=Path)
    parser.add_argument('-u', '--url', default='ws://127.0.0.1:3002/websocket')
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

    is_active = False
    is_first = False
    pulse_width = 0

    @only_device
    def added_or_changed(collection, id_, fields, *args):
        nonlocal is_first
        nonlocal is_active
        nonlocal pulse_width
        dirty = False
        if 'isActivated' in fields:
            old_is_active = is_active
            is_active = fields['isActivated']
            if not old_is_active and is_active:
                is_first = True
            dirty = True
        if 'pulseWidth' in fields:
            pulse_width = fields['pulseWidth']
            dirty = True
        if dirty:
            write_pulse_width()

    @only_device
    def removed(collection, id_):
        nonlocal is_active
        nonlocal pulse_width
        is_active = False
        pulse_width = 0.0
        write_pulse_width()

    lock = threading.Lock()
    pin = None

    def write_pulse_width():
        nonlocal is_first
        with lock:
            if pin is None:
                return
            if is_active:
                if is_first:
                    is_first = False
                    pin.write(1)
                    time.sleep(0.05)
                pin.write(pulse_width)
            else:
                pin.write(0)

    print('Press ^C to exit')

    with create_board(args.port_path) as board:
        pin_tmp = board.get_pin('d:9:p')
        with lock:
            pin = pin_tmp
        with create_client(args.url) as client:
            client.on('added', added_or_changed)
            client.on('changed', added_or_changed)
            client.on('removed', removed)
            with subscription(client, 'device', params=[args.device_id]):
                while not is_stopping:
                    time.sleep(1)
        is_active = False
        pulse_width = 0
        write_pulse_width()


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

