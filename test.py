#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from IPython import embed

from pyfirmata import Arduino


def on():
    board.digital[13].write(1)


def off():
    board.digital[13].write(0)


def main():
    global board

    # Connect to Arduino board
    print('Connecting to Arduino board...', end='')
    sys.stdout.flush()
    board = Arduino('/dev/ttyACM0')
    print(' done')

    # Turn pin 13 on
    on()

    embed()


if __name__ == '__main__':
    main()

