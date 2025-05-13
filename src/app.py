#!/usr/bin/env python3
"""
標準電波 JJY に相当する信号を送信するライブラリです。

Usage:
  app.py [-c CONFIG] [-D]

Options:
  -c CONFIG         : CONFIG を設定ファイルとして読み込んで実行します。[default: config.yaml]
  -D                : デバッグモードで動作します。
"""

import logging
import pathlib
import signal

import my_lib.footprint
import my_lib.rpi

import jjy.clock

SCHEMA_CONFIG = "config.schema"

should_terminate = False


def sig_handler(num, _):
    global should_terminate  # noqa: PLW0603

    logging.warning("receive signal %d", num)

    if num == signal.SIGTERM:
        should_terminate = True


def execute(config):
    global should_terminate

    pin_no = config["control"]["gpio"]

    def send_pulse_func(mode):
        if mode == jjy.clock.pulse_mode.ON.value:
            my_lib.rpi.gpio.output(pin_no, my_lib.rpi.gpio.level.HIGH.value)
        else:
            my_lib.rpi.gpio.output(pin_no, my_lib.rpi.gpio.level.LOW.value)

    my_lib.rpi.gpio.setwarnings(False)
    my_lib.rpi.gpio.setmode(my_lib.rpi.gpio.BCM)
    my_lib.rpi.gpio.setup(pin_no, my_lib.rpi.gpio.OUT)

    jjy.clock.init(send_pulse_func)

    signal.signal(signal.SIGTERM, sig_handler)

    while True:
        jjy.clock.start()

        my_lib.footprint.update(pathlib.Path(config["liveness"]["file"]["sensing"]))

        if should_terminate:
            logging.warning("SIGTERM received")
            break


######################################################################
if __name__ == "__main__":
    import docopt
    import my_lib.config
    import my_lib.logger

    args = docopt.docopt(__doc__)

    config_file = args["-c"]
    debug_mode = args["-D"]

    my_lib.logger.init("jjy", level=logging.DEBUG if debug_mode else logging.INFO)

    config = my_lib.config.load(config_file, pathlib.Path(SCHEMA_CONFIG))

    execute(config)
