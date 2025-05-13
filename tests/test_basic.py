#!/usr/bin/env python3
# ruff: noqa: S101

import pathlib

import my_lib.config
import pytest

CONFIG_FILE = "config.example.yaml"


@pytest.fixture(scope="session", autouse=True)
def config():
    return my_lib.config.load(CONFIG_FILE)


@pytest.fixture(scope="session", autouse=True)
def _clear(config):
    import my_lib.footprint

    my_lib.footprint.clear(pathlib.Path(config["liveness"]["file"]["jjy-wave"]))


######################################################################
def test_execute(config):
    import app

    app.execute(config, True)

    assert True


def test_liveness(config):
    import healthz

    assert healthz.check_liveness(
        [
            {
                "name": name,
                "liveness_file": pathlib.Path(config["liveness"]["file"][name]),
                "interval": 10,
            }
            for name in ["jjy-wave"]
        ]
    )
