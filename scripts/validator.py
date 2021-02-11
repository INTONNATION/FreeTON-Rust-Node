import datetime
import logging
import subprocess
from dotenv import load_dotenv
import os

load_dotenv('/etc/rustvalidator/.env')

elector_addr = os.getenv('elector_addr')
elector_addr_hex = os.getenv('elector_addr_hex')
msig_addr_hex = os.getenv('msig_addr_hex')
msig_addr = os.getenv('msig_addr')
configs_dir = os.getenv('configs_dir')
remained_for_fees = os.getenv('remained_for_fees')
depool_addr = os.getenv('depool_addr')

logging.basicConfig(
    level=logging.INFO,
    format="DateTime : %(asctime)s : %(levelname)s : %(message)s", )


def cli_get_recover_amount(elector_addr: str, msig_addr_hex: str):
    recover_amount = subprocess.check_output(
        'tonos-cli run %s compute_returned_stake \"{\\"wallet_addr\\":\\"%s\\"}\" --abi %s/Elector.abi.json | grep value0 | awk \'{print $2}\' | tr -d \'"\' | printf %%d' % (
            elector_addr, msig_addr_hex, configs_dir), encoding='utf-8', shell=True)
    logging.info('RECOVER AMOUNT: %s' % recover_amount)
    return recover_amount


def console_recover_stake():
    subprocess.check_output('console -C %s/console.json -c recover_stake' % (configs_dir), encoding='utf-8', shell=True)


def recover_query_boc():
    recover_query_boc = subprocess.check_output('base64 --wrap=0 recover-query.boc', encoding='utf-8', shell=True)
    logging.info('RECOVER QUERY BOC: %s' % recover_query_boc)
    return recover_query_boc


def cli_submit_transaction(msig_addr: str, elector_addr_hex: str, value: str, boc: str):
    trx = subprocess.check_output('tonos-cli call %s submitTransaction \
            \"{\\"dest\\":\\"%s\\",\\"value\\":\\"%s\\",\\"bounce\\":true,\\"allBalance\\":false,\\"payload\\":\\"%s\\"}\" \
            --abi %s/SafeMultisigWallet.abi.json \
            --sign %s/msig.keys.json' % (msig_addr, elector_addr_hex, value, boc, configs_dir, configs_dir),
                                  encoding='utf-8', shell=True)
    logging.info(trx)
    return trx


def cli_get_active_election_id(elector_addr: str):
    active_election_id = subprocess.check_output(
        'tonos-cli run %s active_election_id {} --abi %s/Elector.abi.json | grep value0 | awk \'{print $2}\' | tr -d \"\\"\"|tr -d \"\n\"' % (
            elector_addr, configs_dir), encoding='utf-8', shell=True)
    logging.info('ACTIVE ELECTION ID: %s' % active_election_id)
    return active_election_id


def console_create_elector_request():
    subprocess.check_output('tonos-cli getconfig 15 > global_config_15_raw', encoding='utf-8', shell=True)
    elections_end_before = subprocess.check_output(
        'cat global_config_15_raw | grep elections_end_before | awk \'{print $2}\' | tr -d \',\'', encoding='utf-8',
        shell=True)
    elections_start_before = subprocess.check_output(
        'cat global_config_15_raw | grep "elections_start_before" | awk \'{print $2}\' | tr -d \',\'', encoding='utf-8',
        shell=True)
    stake_held_for = subprocess.check_output(
        'cat global_config_15_raw | grep "stake_held_for" | awk \'{print $2}\' | tr -d \',\'', encoding='utf-8',
        shell=True)
    validators_elected_for = subprocess.check_output(
        'cat global_config_15_raw | grep "validators_elected_for" | awk \'{print $2}\' | tr -d \',\'', encoding='utf-8',
        shell=True)
    election_start = cli_get_active_election_id(elector_addr)
    election_stop = (int(election_start) + 1000 + int(elections_start_before) + int(elections_end_before) + int(
        stake_held_for) + int(validators_elected_for))
    request = subprocess.check_output(
        'console -C %s/console.json -c "election-bid %s %s"' % (configs_dir, election_start, election_stop),
        encoding='utf-8', shell=True)
    logging.info(request)


def validator_query_boc():
    validator_query_boc = subprocess.check_output('base64 --wrap=0 validator-query.boc', encoding='utf-8', shell=True)
    logging.info('VALIDATOR QUERY BOC %s' % validator_query_boc)
    return validator_query_boc


def check_validator_balance(msig_addr_hex: str):
    balance = subprocess.check_output('tonos-cli account %s | grep balance | awk \'{print $2}\'' % (msig_addr),
                                      encoding='utf-8', shell=True)
    balance_in_tokens = int(balance) / 1000000000
    logging.info('BALANCE %s' % balance_in_tokens)
    return balance_in_tokens


def get_min_stake():
    min_stake = subprocess.check_output(
        'tonos-cli getconfig 17 | grep min_stake | awk \'{print $2}\' | tr -d \'\\"\' | tr -d \',\'', encoding='utf-8',
        shell=True)
    min_stake_in_tokens = int(min_stake) / 1000000000
    logging.info('MIN STAKE %s' % min_stake_in_tokens)
    return min_stake_in_tokens


def get_stake():
    actual_balance = check_validator_balance(msig_addr_hex)
    stake = (actual_balance - remained_for_fees) / 2
    logging.info('WILL BE STAKED %s' % stake)
    return stake


def submit_stake():
    stake = get_stake()
    nanostake = subprocess.check_output('tonos-cli convert tokens %s | tail -1' % (int(stake)), encoding='utf-8',
                                        shell=True)
    boc = validator_query_boc();
    result_of_submit = cli_submit_transaction(msig_addr, elector_addr_hex, int(nanostake), boc)
    logging.info(result_of_submit)
    return result_of_submit


try:
    recover_amount = cli_get_recover_amount(elector_addr, msig_addr_hex)
    logging.info('recover amount = 0')
    if recover_amount != "0":
        console_recover_stake()
        boc = recover_query_boc()
        cli_submit_transaction(msig_addr, elector_addr_hex, 1000000000, boc)
        logging.info('RECOVER STAKE REQUESTED')
    else:
        logging.info('NO TOKENS TO RECOVER')

    console_create_elector_request()
    submit_stake()
except:
    logging.info('ERROR running validator')
