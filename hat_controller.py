from argparse import ArgumentParser
import time

import ddp

from pyfirmata import Arduino


class HatController(object):
    def __init__(self, url, board):
        self._conn = ddp.DdpConnection(
            url,
            received_message_callback=self._recieved_message,
        )

        self._board = board
        self._id = None
        self._is_activated = False
        self._is_ready = False

    def _recieved_message(self, message):
        hat = u'hat'
        is_activated = u'isActivated'
        name = u'name'

        if isinstance(message, ddp.ReadyMessage):
            self._is_ready = True
            self._set_hat_state(self._is_activated)

        elif isinstance(message, ddp.AddedMessage):
            fields = message.fields
            if fields.get(name) == hat:
                self._id = message.id_
                self._set_hat_state(fields.get(is_activated, False))

        elif isinstance(message, ddp.ChangedMessage):
            fields = message.fields
            if message.id_ == self._id and is_activated in fields:
                self._set_hat_state(fields[is_activated])


    def _set_hat_state(self, is_activated):
        if self._is_activated == is_activated:
            return
        self._is_activated = is_activated

        if self._is_activated:
            self._write(1)
            print 'Hat activated'
        else:
            self._write(0)
            print 'Hat deactivated'

    def _write(self, value):
        self._board.digital[13].write(value)

    def connect(self):
        self._conn.connect()
        msg = ddp.SubMessage('1', 'hat')
        self._conn.send(msg)

    def disconnect(self):
        self._conn.disconnect()


def main():
    parser = ArgumentParser()
    parser.add_argument('-s', '--server', default='127.0.0.1:3000')
    parser.add_argument('device')
    args = parser.parse_args()

    url = ddp.ServerUrl(args.server)
    board = None
    hat_controller = None

    try:
        print 'Connection to Arduino board...'
        board = Arduino(args.device)

        print 'Connecting to DDP server...'
        hat_controller = HatController(url, board)

        hat_controller.connect()
        wait_for_user_to_exit()
    finally:
        if hat_controller is not None:
            try:
                hat_controller.disconnect()
            except:
                print (
                    'An error occurred while disconnecting from the DDP '
                    'server.'
                )

        if board is not None:
            try:
                board.exit()
            except:
                print 'An error occurred while exiting from the Arduino board.'


def wait_for_user_to_exit():
    try:
        print 'Press ^C to exit'
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

