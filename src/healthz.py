#!/usr/bin/env python3
"""
Liveness のチェックを行います

Usage:
  healthz.py [-c CONFIG] [-D]

Options:
  -c CONFIG         : CONFIG を設定ファイルとして読み込んで実行します。[default: config.yaml]
  -D                : デバッグモードで動作します。
"""

import logging
import pathlib
import sys

import my_lib.healthz
from docopt import docopt


def check_liveness(target_list):
    for target in target_list:
        if not my_lib.healthz.check_liveness(target["name"], target["liveness_file"], target["interval"]):
            return False

    return True


######################################################################
if __name__ == "__main__":
    import my_lib.config
    import my_lib.logger

    args = docopt(__doc__)

    config_file = args["-c"]
    debug_mode = args["-D"]

    my_lib.logger.init("hems.jjy-wave", level=logging.DEBUG if debug_mode else logging.INFO)

    logging.info("Using config config: %s", config_file)
    config = my_lib.config.load(config_file)

    target_list = [
        {
            "name": name,
            "liveness_file": pathlib.Path(config["liveness"]["file"][name]),
            "interval": 60,
        }
        for name in ["jjy-wave"]
    ]

    if check_liveness(target_list):
        logging.info("OK.")
        sys.exit(0)
    else:
        sys.exit(-1)
