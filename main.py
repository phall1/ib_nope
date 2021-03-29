import argparse
import asyncio
import logging

import toml
from ib_insync import IB, IBC, Watchdog, util

from nope.nope_strategy import NopeStrategy

with open("conf/conf.toml", "r") as f:
    config = toml.load(f)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--debug",
    help="Print lots of debugging statements",
    action="store_const",
    dest="loglevel",
    const=logging.DEBUG,
    default=logging.WARNING,
)
parser.add_argument(
    "-v",
    "--verbose",
    help="Be verbose",
    action="store_const",
    dest="loglevel",
    const=logging.INFO,
    default=config["verbose"],
)
parser.add_argument(
    "--data-source",
    help="Options and equity quotes data source",
    choices=["qt", "tda"],
    default=config["default_client"],
)

args = parser.parse_args()


util.patchAsyncio()

if config["debug"]["enabled"]:
    asyncio.get_event_loop().set_debug(True)
    util.logToConsole(logging.DEBUG)

if config["verbose"]:
    util.logToConsole(logging.INFO)

task_run_ib = None


def onConnect():
    global task_run_ib
    task_run_ib = nope_strategy.execute()


def onDisconnect():
    if task_run_ib is not None:
        task_run_ib.cancel()


ibc = IBC(981, tradingMode="paper")
ib = IB()
ib.connectedEvent += onConnect
ib.disconnectedEvent += onDisconnect

nope_strategy = NopeStrategy(config, ib)

watchdog = Watchdog(ibc, ib)
watchdog.start()
ib.run()
