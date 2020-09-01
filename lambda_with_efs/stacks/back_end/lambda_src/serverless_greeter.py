# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import random
import time
import fcntl


class GlobalArgs:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "greeter_lambda"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    RANDOM_SLEEP_ENABLED = os.getenv("RANDOM_SLEEP_ENABLED", False)
    RANDOM_SLEEP_SECS = int(os.getenv("RANDOM_SLEEP_SECS", 2))
    ANDON_CORD_PULLED = os.getenv("ANDON_CORD_PULLED", False)


def set_logging(lv=GlobalArgs.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initial some defaults in global context to reduce lambda start time, when re-using container
logger = set_logging()


def random_sleep(max_seconds=10):
    if bool(random.getrandbits(1)):
        logger.info(f"sleep_start_time:{str(datetime.datetime.now())}")
        time.sleep(random.randint(0, max_seconds))
        logger.info(f"sleep_end_time:{str(datetime.datetime.now())}")


MSG_FILE_PATH = "/mnt/efs/mystique-message-wall"
DIR_PATH = "/mnt/efs"


def _get_all_files_in_dir(DIR_PATH):
    res = []
    for root, dirs, files in os.walk(DIR_PATH):
        for f in files:
            res.append(os.path.join(root, f))
    return res


def get_messages():
    try:
        with open(MSG_FILE_PATH, "r") as msg_file:
            fcntl.flock(msg_file, fcntl.LOCK_SH)
            msg = msg_file.read()
            fcntl.flock(msg_file, fcntl.LOCK_UN)
    except:
        msg = "No message yet."
    return msg


def add_message(_msg):
    if _msg:
        with open(MSG_FILE_PATH, "a") as msg_file:
            fcntl.flock(msg_file, fcntl.LOCK_EX)
            msg_file.write(_msg + "\n")
            fcntl.flock(msg_file, fcntl.LOCK_UN)


def delete_messages():
    try:
        os.remove(MSG_FILE_PATH)
    except:
        pass


def lambda_handler(event, context):
    logger.info(f"rcvd_evnt:{event}")
    greet_msg = "Hello from Miztiikal World, How is it going?"

    # random_sleep(GlobalArgs.RANDOM_SLEEP_SECS)
    method = event["requestContext"]["httpMethod"]
    if method == "GET":
        greet_msg = get_messages()
    elif method == "POST":
        new_message = event.get("body")
        add_message(new_message)
        greet_msg = get_messages()
    elif method == "DELETE":
        delete_messages()
        greet_msg = "Messages deleted."
    else:
        greet_msg = "API Method unsupported."

    msg = {
        "statusCode": 200,
        "body": (
            f'{{"message": "{greet_msg}",'
            f'"lambda_version":"{context.function_version}",'
            f'"ts": "{str(datetime.datetime.now())}"'
            f'}}'
        )
    }

    print(_get_all_files_in_dir(DIR_PATH))

    return msg
