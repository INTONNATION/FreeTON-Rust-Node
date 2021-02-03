import logging
import json
import requests
import datetime
import base64
import os
import subprocess
from tonclient.client import TonClient
from tonclient.types import Abi, KeyPair, ClientConfig, DeploySet, CallSet, Signer, \
    MessageSource, StateInitSource, ParamsOfEncodeMessage, ParamsOfProcessMessage, ParamsOfRunGet

from tonclient.types import Abi, DeploySet, CallSet, Signer, StateInitSource, \
    AccountForExecutor, ParamsOfEncodeMessage, ParamsOfProcessMessage, \
    ParamsOfWaitForCollection, ParamsOfParse, ParamsOfRunExecutor, \
    ParamsOfRunTvm, ParamsOfEncodeAccount, ParamsOfRunGet, ParamsOfQueryCollection

logging.basicConfig(
    level=logging.INFO,
    format="DateTime : %(asctime)s : %(levelname)s : %(message)s", )

client_config = ClientConfig()
client_config.network.server_address = "https://rustnet.ton.dev"
config = ClientConfig()
config.network.server_address = "https://rustnet.ton.dev"
config.abi.message_expiration_timeout = 30000
client_config.abi.message_expiration_timeout = 30000
client = TonClient(config=config, is_async=False)
async_core_client = TonClient(config=client_config)

elector_addr = "-1:3333333333333333333333333333333333333333333333333333333333333333"


def main():
    config = ClientConfig()
    config.network.server_address = "https://rustnet.ton.dev"
    config.abi.message_expiration_timeout = 30000

    client = TonClient(config=config)
    version = client.version()


def call_example(address: str):
    elector_abi = Abi.from_path(
        path=os.path.join("./", 'Elector.abi.json'))
    call_set = CallSet(
        function_name='compute_returned_stake',
        input={'wallet_addr': address})
    encode_params = ParamsOfEncodeMessage(
        abi=elector_abi, signer=Signer.NoSigner(), address=elector_addr,
        call_set=call_set)
    process_params = ParamsOfProcessMessage(
        message_encode_params=encode_params, send_events=False)
    async_core_client.processing.process_message(params=process_params)


def compute_returned_stake(address: str):
    elector_abi = Abi.from_path(
        path=os.path.join("./", 'Elector.abi.json'))
    call_set = CallSet(
        function_name='compute_returned_stake',
        input={'wallet_addr': address})
    encode_params = ParamsOfEncodeMessage(
        abi=elector_abi, signer=Signer.NoSigner(), address=elector_addr, call_set=call_set)
    encoded_message = async_core_client.abi.encode_message(
        params=encode_params)
    ql_params = ParamsOfQueryCollection(
        collection='accounts', result='boc', filter={'id': {'eq': elector_addr}})
    result = client.net.query_collection(params=ql_params)
    account = result.result[0]['boc']

    run_params = ParamsOfRunTvm(
        message=encoded_message.message, abi=elector_abi, account=account)
    output_run = async_core_client.tvm.run_tvm(params=run_params)
    result = output_run.decoded.output
    print(result)

compute_returned_stake('0x4000610da7d7f89b92cd64212e5b983d9ccac9938333174f352a5b3c416997c4')
