#!/usr/bin/env python
from os import environ
import argparse
import logging
from pseg import pseg
from discord import webhook


def parseArgs():
    parser = argparse.ArgumentParser(
        description='Lookup next meter reading date')
    parser.add_argument(
        '--username', default=environ.get("PSEG_USERNAME"),
        help="pseg.com account username (overrides PSEG_USERNAME)"
    )
    parser.add_argument(
        '--password', default=environ.get("PSEG_PASSWORD"),
        help="pseg.com account password (overrides PSEG_PASSWORD)"
    )
    parser.add_argument(
        "--discord-webhook", default=environ.get("DISCORD_WEBHOOK"),
        help="discord webhook url to send messages to (overrides DISCORD_WEBHOOK"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="DEFAULT: False"
    )
    args = parser.parse_args()
    if not args.username or not args.password:
        exit(parser.print_help())
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    return args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:[%(levelname)s]:%(message)s"
    )
    args = parseArgs()
    discord = webhook.Discord(args.discord_webhook)
    client = pseg.Pseg(args.username, args.password)
    try:
        client.login()
        if args.discord_webhook:
            discord.send("Your next PSE&G meter reading will be on " +
                         client.getReadingDate())
        client.logout()
    except Exception as e:
        logging.critical(e)
        discord.error(e)
    finally:
        client.quit()
