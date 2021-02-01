import logging
import json
import requests
import datetime
import base64
import os
import subprocess
from tonclient.client import TonClient


logging.basicConfig(
    level=logging.INFO,
    format="DateTime : %(asctime)s : %(levelname)s : %(message)s",)


def main():
    client = TonClient()


if __name__ == '__main__':
    main()