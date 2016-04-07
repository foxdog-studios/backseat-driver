#!/usr/bin/env python

import logging
import queue as queuelib
import signal
import threading
import time
import traceback
from argparse import ArgumentParser
from collections import OrderedDict
from contextlib import ExitStack, contextmanager, suppress
from functools import wraps
from pathlib import Path

import bluetooth
from MeteorClient import MeteorClient


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


def main():
    print('Press ^C to quit')
    args = parse_args()
    configure_logging(args)
    with flag_signals(signal.SIGINT, signal.SIGTERM) as received_signal:
        while not received_signal.is_set():
            try:
                party_hat_main(received_signal, args)
            except:
                logger.warning('An error has stopped the main loop',
                                exc_info=True)
                time.sleep(1)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-d', '--device', default='hat', dest='device_id')
    parser.add_argument('-l', '--log-level', choices=LOG_NAME_TO_LEVEL.keys(),
                        default=LOG_LEVEL_TO_NAMES[logging.INFO])
    parser.add_argument(
        dest='bluetooth_address',
        default='30:14:11:19:09:71',
        help='address of the bluetooth device to open a socket to'
    )
    parser.add_argument('-u', '--url', default='ws://127.0.0.1:3000/websocket')
    return parser.parse_args()


def configure_logging(args):
    global logger
    logging.basicConfig(
            datefmt='%H:%M:%S',
            format='[%(levelname).1s %(asctime)s] %(message)s',
            level=LOG_NAME_TO_LEVEL[args.log_level])
    logger = logging.getLogger(__name__)


def party_hat_main(received_signal, args):
    queue = queuelib.Queue()
    device_changes = DeviceChanges(args.device_id, queue)

    def is_websocket_alive():
        return client.ddp_client.ddpsocket._th.is_alive()

    with create_client(args.url) as client, \
         on_message(client, 'added', device_changes.added), \
         on_message(client, 'changed', device_changes.changed), \
         on_message(client, 'removed', device_changes.removed), \
         subscription(client, 'device', params=[args.device_id]), \
         create_bluetooth_socket(str(args.bluetooth_address)) as bt_s, \
         create_pin_manager(bt_s) as pin_manager:
        while not received_signal.is_set() and is_websocket_alive():
            with suppress(queuelib.Empty):
                changes = queue.get(timeout=1)
                if 'is_active' in changes:
                    pin_manager.set_is_active(changes['is_active'])
                if 'pulse_width' in changes:
                    pin_manager.set_pulse_width(changes['pulse_width'])
                pin_manager.update()


# =============================================================================
# = Meteor                                                                    =
# =============================================================================

@contextmanager
def create_client(url):
    client = MeteorClient(url)
    logger.info('Connecting to Meteor server ...')
    try:
        client.connect()
        yield client
    finally:
        logger.info('Disconnecting from Meteor server ...')
        client.close()


@contextmanager
def on_message(client, message, callback):
    try:
        client.on(message, callback)
        yield
    finally:
        client.remove_listener(message, callback)


@contextmanager
def subscription(client, name, *args, **kwargs):
    logger.info('Subscribing to %s ...', name)
    try:
        client.subscribe(name, *args, **kwargs)
        yield
    finally:
        client.unsubscribe(name)


class DeviceChanges:
    def __init__(self, device_id, queue):
        self._collection = 'Devices'
        self._device_id = device_id
        self._queue = queue

    def _filter(method):
        @wraps(method)
        def wrapper(self, collection, device_id, *args, **kwargs):
            if collection == self._collection or device_id == self._device_id:
                return method(self, collection, device_id, *args, **kwargs)
        return wrapper

    @_filter
    def added(self, collection, device_id, fields):
        changes = self._extract_changes(fields)
        if 'isActivated' not in fields:
            changes['is_active'] = False
        if 'pulseWidth' not in fields:
            changes['pulseWidth'] = 0.0
        self._handle_changes(changes)

    @_filter
    def changed(self, collection, device_id, fields, cleared):
        changes = self._extract_changes(fields)
        if 'isActivated' in cleared:
            changes['is_active'] = False
        if 'pulseWidth' in cleared:
            changes['pulse_width'] = 0.0
        self._handle_changes(changes)

    def _extract_changes(self, fields):
        kwargs = {}
        if 'isActivated' in fields:
            kwargs['is_active'] = fields['isActivated']
        if 'pulseWidth' in fields:
            kwargs['pulse_width'] = fields['pulseWidth']
        return kwargs

    @_filter
    def removed(self, collection, device_id):
        self._handle_changes({'is_active': False, 'pulse_width': 0.0})

    def _handle_changes(self, changes):
        if changes:
            self._queue.put(changes)


# =============================================================================
# = Arduino                                                                   =
# =============================================================================

@contextmanager
def create_pin_manager(bluetooth_socket):
    pin_manager = PinManager(bluetooth_socket)

    logger.info('Setting pin to default state ...')
    pin_manager.update()
    logger.info('Set pin to default state')

    try:
        yield pin_manager
    finally:
        logger.info('Setting pin to low ...')
        pin_manager.set_is_active(False)
        pin_manager.set_pulse_width(0.0)
        pin_manager.update()


class PinManager:
    def __init__(self, bluetooth_socket):
        self._dirty = True
        self._is_active = False
        self._just_active = False
        self._bluetooth_socket = bluetooth_socket
        self._pulse_width = 0.0

    def set_pulse_width(self, pulse_width):
        self._pulse_width = pulse_width
        self._dirty = True

    def set_is_active(self, is_active):
        if not self._is_active and is_active:
            self._just_active = True
        self._is_active = is_active
        self._dirty = True

    def update(self):
        if self._dirty:
            self._dirty = False
            if self._is_active:
                if self._just_active:
                    self._just_active = False
                    self._write(1.0)
                    time.sleep(0.05)
                self._write(self._pulse_width)
            else:
                self._write(0.0)

    def _write(self, pulse_width):
        pw = int(pulse_width * 255)
        data = chr(int(pw))
        logger.debug('Writing pulse width: %d with byte value  %s ...',
                    pw, data)
        self._bluetooth_socket.send(data)


# =============================================================================
# = Bluetooth                                                                 =
# =============================================================================

@contextmanager
def create_bluetooth_socket(address):
    logger.info('Connecting to bluetooth address %s...', address)
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = 1
    socket.connect((address, port))
    logger.info('Bluetooth connected')
    try:
        yield socket
    finally:
        socket.close()
        logger.info('Bluetooth disconnected')


# =============================================================================
# = Signals                                                                   =
# =============================================================================

@contextmanager
def flag_signals(*signums):
    received_signal = threading.Event()
    with ExitStack() as stack:
        for signum in signums:
            stack.enter_context(flag_signal(received_signal, signum))
        yield received_signal


@contextmanager
def flag_signal(received_signal, signum):
    def handler(signum, frame):
        logger.info('Received signal %d', signum)
        received_signal.set()
    prev_handler = signal.signal(signum, handler)
    try:
        yield
    finally:
        signal.signal(signum, prev_handler)


# =============================================================================

if __name__ == '__main__':
    main()

