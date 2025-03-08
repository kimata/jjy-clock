#!/usr/bin/env python3
"""
標準電波 JJY に相当する信号を生成するライブラリです．

Usage:
  clock.py [-D]

Options:
  -D                : デバッグモードで動作します．
"""

import datetime
import enum
import logging
import time

send_pulse = None

pulse_mode = enum.Enum("pulse_mode", {"ON": 1, "OFF": 0})


def send_bit(bit):
    logging.debug("send bit: %d", bit)

    if bit == -1:  # マーカ
        send_pulse(pulse_mode.ON.value)
        time.sleep(0.2)
        send_pulse(pulse_mode.OFF.value)
        time.sleep(0.799)
    elif bit == 0:  # 0
        send_pulse(pulse_mode.ON.value)
        time.sleep(0.799)
        send_pulse(pulse_mode.OFF.value)
        time.sleep(0.2)
    elif bit == 1:  # 1
        send_pulse(pulse_mode.ON.value)
        time.sleep(0.499)
        send_pulse(pulse_mode.OFF.value)
        time.sleep(0.5)


def send_bcd(num, count, parity=0):
    logging.debug("send bcd: %d (%d)", num, count)
    for i in range(count):
        bit = (int(num) >> ((count - 1) - i)) & 0x1
        send_bit(bit)
        parity ^= bit
    return parity


def send_datetime(now):
    now = datetime.datetime.now()
    minute = now.minute
    hour = now.hour
    day = now.toordinal() - datetime.date(now.year, 1, 1).toordinal() + 1
    year = now.year % 100
    wday = now.isoweekday() % 7
    sec = now.second
    usec = now.microsecond

    min_parity = 0
    hour_parity = 0

    ############################################################
    send_bit(-1)

    # 10分位のBCD
    min_parity = send_bcd(minute / 10, 3, min_parity)

    send_bit(0)

    # 1分位のBCD
    min_parity = send_bcd(minute % 10, 4, min_parity)

    send_bit(-1)

    ############################################################
    send_bit(0)
    send_bit(0)

    # 10時位のBCD
    hour_parity = send_bcd(hour / 10, 2, hour_parity)

    send_bit(0)

    # 1時位のBCD
    hour_parity = send_bcd(hour % 10, 4, hour_parity)

    send_bit(-1)

    ############################################################
    send_bit(0)
    send_bit(0)

    # 累計日数100日位のBCD
    send_bcd(day / 100, 2)

    send_bit(0)

    # 累計日数10日位のBCD
    send_bcd((day % 100) / 10, 4)

    send_bit(-1)

    ############################################################
    # 累計日数1日位のBCD
    send_bcd(day % 10, 4)

    send_bit(0)
    send_bit(0)

    # パリティ
    send_bit(hour_parity)
    send_bit(min_parity)

    send_bit(0)
    send_bit(-1)

    ############################################################
    send_bit(0)

    # 西暦年10年位のBCD
    send_bcd((year % 100) / 10, 4)

    # 西暦年1年位のBCD
    send_bcd(year % 10, 4)

    send_bit(-1)

    ############################################################
    # 曜日のBCD
    send_bcd(wday, 3)

    send_bit(0)
    send_bit(0)
    send_bit(0)
    send_bit(0)
    send_bit(0)
    send_bit(0)

    # マーカ
    send_pulse(pulse_mode.ON.value)
    time.sleep(0.2)
    send_pulse(pulse_mode.OFF.value)
    # 0.8 秒残しておき，次回呼び出しタイミングの調整代とする


def start():
    logging.info("start to send JJY code.")

    now = datetime.datetime.now()
    sec = now.second
    usec = now.microsecond

    # 0 秒になるまで待つ
    wait_sec = 60 - (sec + usec / 1000000.0)
    if wait_sec > 1:
        logging.warning("wait %.1f sec", wait_sec)
    time.sleep(wait_sec)

    target_time = now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)

    send_datetime(target_time)

    logging.info("send %s (calibration time: %1.2f sec).", target_time, wait_sec)


def init(send_pulse_func):
    global send_pulse

    send_pulse = send_pulse_func
    send_pulse(pulse_mode.OFF.value)


######################################################################
if __name__ == "__main__":
    import docopt
    import my_lib.logger
    import my_lib.rpi

    args = docopt.docopt(__doc__)

    debug_mode = args["-D"]

    log_level = logging.DEBUG if debug_mode else logging.INFO

    my_lib.logger.init("test", level=log_level)

    def send_pulse_func(mode):
        logging.debug(mode)

    init(send_pulse_func)
    start()
