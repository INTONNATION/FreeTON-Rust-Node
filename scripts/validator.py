import os
import datetime
import logging
import json
import subprocess

elector_addr = "-1:3333333333333333333333333333333333333333333333333333333333333333"
msig_addr = "0x4000610da7d7f89b92cd64212e5b983d9ccac9938333174f352a5b3c416997c4"
msig_addr_null = "0:4000610da7d7f89b92cd64212e5b983d9ccac9938333174f352a5b3c416997c4"
# It stores ABIs, keys and configs like  msig.keys.json, Elector.abi.json, SafeMultisigWallet.abi.json, console.json etc
configs_dir = "/etc/rustnode"

logging.basicConfig(
    level=logging.INFO,
    format="DateTime : %(asctime)s : %(levelname)s : %(message)s", )


# Add tonos-cli setup to playbook
# place Elector.abi.json, SafeMultisigWallet.abi.json, msig.keys.json to configs dir
def cli_get_recover_amount(elector_addr: str, msig_addr: str):
    os.system('tonos-cli run %s compute_returned_stake \"{\\"wallet_addr\\":\\"%s\\"}\" --abi %s/Elector.abi.json' % (
    elector_addr, msig_addr, configs_dir))


def console_recover_stake():
    os.system('console -C %s/console.json -c recover_stake' % (configs_dir))


def recover_query_boc():
    recover_query_boc = os.system('base64 --wrap=0 recover-query.boc')
    return recover_query_boc


def cli_submit_transaction(msig_addr: str, elector_addr: str):
    os.system('tonos cli call %s submitTransaction \
            \"{\\"dest\\":\\"%s\\",\\"value\\":\\"1000000000\\",\\"bounce\\":true,\\"allBalance\\":false,\\"payload\\":\\"%s\\"}\" \
            --abi %s/SafeMultisigWallet.abi.json \
            --sign %s/msig.keys.json' % (msig_addr, elector_addr, recover_query_boc, configs_dir, configs_dir))


def cli_get_active_election_id(elector_addr: str):
    active_election_id = subprocess.check_output(
        'tonos-cli run %s active_election_id {} --abi %s/Elector.abi.json | grep value0 | awk \'{print $2}\' | tr -d \"\\"\"|tr -d \"\n\"' % (
        elector_addr, configs_dir), encoding='utf-8', shell=True)
    return active_election_id


def console_create_elector_request():
    os.system('tonos-cli getconfig 15 > global_config_15_raw')
    elections_end_before = os.system(
        'cat global_config_15_raw | grep elections_end_before | awk \'{print $2}\' | tr -d \',\'')
    elections_start_before = os.system(
        'cat global_config_15_raw | grep "elections_start_before" | awk \'{print $2}\' | tr -d \',\'')
    stake_held_for = os.system('cat global_config_15_raw | grep "stake_held_for" | awk \'{print $2}\' | tr -d \',\'')
    validators_elected_for = os.system(
        'cat global_config_15_raw | grep "validators_elected_for" | awk \'{print $2}\' | tr -d \',\'')
    election_start = cli_get_active_election_id(elector_addr)
    election_stop = (int(
        election_start) + 1000 + elections_start_before + elections_end_before + stake_held_for + validators_elected_for)
    print(election_start)
    os.system('console -C %s/console.json -c "election-bid %s %s"' % (configs_dir, election_start, election_stop))


def check_validator_balance(msig_addr: str):
    balance = subprocess.check_output('tonos-cli account %s | grep balance | awk \'{print $2}\'' % (msig_addr),
                                      shell=True)

    return balance


def validator_query_boc():
    validator_query_boc = os.system('base64 --wrap=0 validator-query.boc')
    return validator_query_boc


# cli_get_recover_amount(elector_addr, msig_addr)
# console_recover_stake()
# cli_submit_transaction(msig_addr, elector_addr)
# cli_get_active_election_id(elector_addr)
check_validator_balance(msig_addr_null)