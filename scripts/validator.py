import datetime
import logging
import subprocess
from dotenv import load_dotenv
import os
import time
import sys

elector_addr = os.getenv('ELECTOR_ADDR')
elector_addr_hex = os.getenv('ELECTOR_ADDR_HEX')
msig_addr_hex = os.getenv('MSIG_ADDR_HEX')
msig_addr_hex_0 = os.getenv('MSIG_ADDR_HEX_0')
msig_addr = os.getenv('MSIG_ADDR')
configs_dir = os.getenv('CONFIGS_DIR')
remained_for_fees = os.getenv('REMAINED_FOR_FEES')
depool_addr = os.getenv('DEPOOL_ADDR')
elector_type = os.getenv('ELECTOR_TYPE')
validator = os.getenv('VALIDATOR')
helper_addr = os.getenv('HELPER_ADDR')

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="fmt=validator-rust-node[%(process)d]: %(levelname)s: %(message)s", )

def cli_get_active_election_id_from_depool_event():
    subprocess.check_output(
        'tonos-cli depool --addr %s events > %s/events.txt 2>&1' % (
            depool_addr, configs_dir), encoding='utf-8', shell=True)
    active_election_id_from_depool_event = subprocess.check_output(
        'grep \"^{\" %s/events.txt | grep electionId |jq \".electionId\" | head -1 | tr -d \'"\' | xargs printf '
        '"%%d\n" | tr -d \"\n\" ' % (
            configs_dir), encoding='utf-8', shell=True)
    return active_election_id_from_depool_event

def get_proxy_addr_from_depool_event():
    proxy_addr_from_depool_event = subprocess.check_output(
        'grep \"^{\" %s/events.txt | grep electionId |jq \".proxy\" | head -1 | tr -d \'"\' | tr -d \"\n\" ' % (
            configs_dir), encoding='utf-8', shell=True)
    return proxy_addr_from_depool_event

def add_proxy_addr_to_console(validator_msig_addr):
    subprocess.check_output(
        'jq \".wallet_id = \\"%s\\" \" %s/console.json > /tmp/console.json' % (
            validator_msig_addr, configs_dir), encoding='utf-8', shell=True)
    subprocess.check_output(
        'cp /tmp/console.json %s/console.json' % (configs_dir), encoding='utf-8', shell=True)

def tick_tock():
    subprocess.check_output(
        'tonos-cli call %s sendTicktock {} --abi %s/DePoolHelper.abi.json --sign %s/helper.keys.json' % (
            helper_addr, configs_dir, configs_dir), encoding='utf-8', shell=True)

def cli_get_recover_amount(elector_addr: str, msig_addr_hex: str):
    recover_amount = subprocess.check_output(
        'tonos-cli run %s compute_returned_stake \"{\\"wallet_addr\\":\\"%s\\"}\" --abi %s/Elector.abi.json | grep '
        'value0 | awk \'{print $2}\' | tr -d \'"\' | printf %%d' % (
            elector_addr, msig_addr_hex, configs_dir), encoding='utf-8', shell=True)
    return recover_amount

def cli_get_recover_amount_fift(elector_addr: str, msig_addr_hex: str):
    recover_amount = subprocess.check_output(
        'tonos-cli runget %s compute_returned_stake %s 2>&1 | grep "Result:" | awk -F\'"\' \'{print $2}\' | tr -d '
        '\"\n\"' % (
            elector_addr, msig_addr_hex), encoding='utf-8', shell=True)
    return recover_amount

def console_check():
    console_check=subprocess.check_output('console -C %s/console.json -c getstats' % (configs_dir), encoding='utf-8', shell=True)
    if "Error" in console_check or "error" in console_check:
        logging.error('CONSOLE CHECK FAILS')
        quit()
    return console_check

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
    if elector_type == 'fift':
        active_election_id = subprocess.check_output(
            'tonos-cli runget %s active_election_id | grep Result: | awk -F \'\\"\' \'{print $2}\' |tr -d \"\n\"' % (
                elector_addr), encoding='utf-8', shell=True)
    else:
        active_election_id = subprocess.check_output(
            'tonos-cli run %s active_election_id {} --abi %s/Elector.abi.json | grep value0 | awk \'{print $2}\' | tr '
            '-d \"\\"\"|tr -d \"\n\"' % (
                elector_addr, configs_dir), encoding='utf-8', shell=True)
    return active_election_id

def validators_elected_for():
    validators_elected_for = subprocess.check_output(
        'cat %s/global_config_15_raw | grep "validators_elected_for" | awk \'{print $2}\' | tr -d \',\'' % configs_dir,
        encoding='utf-8',
        shell=True)
    return(validators_elected_for)

def stake_held_for():
    stake_held_for = subprocess.check_output(
        'cat %s/global_config_15_raw | grep stake_held_for | awk \'{print $2}\' | tr -d \',\'' % configs_dir,
        encoding='utf-8',
        shell=True)
    return(stake_held_for)

def elections_start_before():
    elections_start_before = subprocess.check_output(
        'cat %s/global_config_15_raw | grep elections_start_before | awk \'{print $2}\' | tr -d \',\'' % configs_dir,
        encoding='utf-8',
        shell=True)
    return(elections_start_before)

def elections_end_before():
    elections_end_before = subprocess.check_output(
        'cat %s/global_config_15_raw | grep elections_end_before | awk \'{print $2}\' | tr -d \',\'' % configs_dir,
        encoding='utf-8',
        shell=True)
    return(elections_end_before)

def console_create_elector_request(election_start):
    subprocess.check_output('tonos-cli getconfig 15 > %s/global_config_15_raw' % configs_dir, encoding='utf-8',
                            shell=True)
    elections_end_before_local = elections_end_before()
    logging.info('CONSOLE_CREATE_ELECTOR_REQUEST: END BEFORE: %s' % elections_end_before_local)
    elections_start_before_local = elections_start_before()
    logging.info('CONSOLE_CREATE_ELECTOR_REQUEST: START BEFORE: %s' % elections_start_before_local)
    stake_held_for_local = stake_held_for()
    logging.info('CONSOLE_CREATE_ELECTOR_REQUEST: STAKE HELD FOR: %s' % stake_held_for_local)
    validators_elected_for_local = validators_elected_for()
    logging.info('CONSOLE_CREATE_ELECTOR_REQUEST: ELECTED FOR: %s' % validators_elected_for_local)
    election_stop = (int(election_start) + 1000 + int(elections_start_before_local) + int(elections_end_before_local) + int(
        stake_held_for_local) + int(validators_elected_for_local))
    logging.info('CONSOLE_CREATE_ELECTOR_REQUEST: ')
    request = subprocess.check_output(
        'cd %s && console -C console.json -c "election-bid %s %s"' % (configs_dir, election_start, election_stop),
        encoding='utf-8', shell=True)
    logging.info('VALIDATOR BOC IS GENERATED')
    if "error" in request or "Error" in request:
        logging.info(request)
        quit()
    return (elections_start_before_local)

def validator_query_boc():
    validator_query_boc = subprocess.check_output('base64 --wrap=0 %s/validator-query.boc'  % (configs_dir), encoding='utf-8', shell=True)
    logging.info('VALIDATOR QUERY BOC %s' % validator_query_boc)
    return validator_query_boc

def check_validator_balance():
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
    actual_balance = check_validator_balance()
    stake = (int(actual_balance) - int(remained_for_fees)) / 2
    print(stake)
    logging.info('WILL BE STAKED %s' % stake)
    return stake

def submit_stake():
    if validator == 'depool':
        boc = validator_query_boc()
        result_of_submit = cli_submit_transaction(msig_addr, depool_addr, 1000000000, boc)
    elif validator == 'single':
        stake = get_stake()
        nanostake = subprocess.check_output('tonos-cli convert tokens %s | tail -1' % (int(stake)), encoding='utf-8',
                                            shell=True)
        boc = validator_query_boc()
        result_of_submit = cli_submit_transaction(msig_addr, elector_addr_hex, int(nanostake), boc)
    return result_of_submit

while True:
    try:
        console_check()
        logging.info('VALIDATOR MODE: %s' % validator)
        if validator == 'depool':
            try:
                current_time=int(time.time())
                with open("%s/second-tick-tock-time" % configs_dir, 'r') as tick_tock_time:
                    active_election_tick_tock_time = tick_tock_time.read()
                    active_election_tick_tock_time = int(active_election_tick_tock_time)
                    if active_election_tick_tock_time != 0:
                      if active_election_tick_tock_time < current_time:
                        logging.info('SENDING SECOND TICK-TOCK')
                        tick_tock()
                        with open("%s/second-tick-tock-time" % configs_dir, 'w') as the_file:
                          second_tick = '0'
                          the_file.write(second_tick)
                      else:
                          tick_send_in = active_election_tick_tock_time - current_time
                          logging.info('SECOND TICK TOCK WILL BE SENT IN: %s seconds' % (tick_send_in))
                    else:
                      logging.info('SECOND TICK TOCK TIME: %s. ALREADY SENT' % (active_election_tick_tock_time))
            except Exception as e:
                print(e)
                logging.info('File second-tick-tock-time DOES NOT EXIST')
                pass
            active_election_id_from_depool_event = cli_get_active_election_id_from_depool_event()
            logging.info('ACTIVE ELECTION ID FROM DEPOOL EVENT: %s' % active_election_id_from_depool_event)
            active_election_id = cli_get_active_election_id(elector_addr)
            logging.info('ACTIVE ELECTION ID: %s' % active_election_id)
            try:
                with open("%s/active-election-id-submitted" % configs_dir, 'r') as the_file:
                    submitted_election_id = the_file.read()
            except:
                submitted_election_id = 0
            if int(active_election_id) != 0 and int(active_election_id) != int(submitted_election_id):
                logging.info('SENDING FIRST TICK TOCK')
                tick_tock()
                if active_election_id_from_depool_event == active_election_id:
                    proxy_msig_addr = get_proxy_addr_from_depool_event()
                    logging.info('PROXY ADDR: %s' % proxy_msig_addr)
                    add_proxy_addr_to_console(proxy_msig_addr)
                    logging.info('PROXY ADDR ADDED TO console.json')
                    elections_start_before = console_create_elector_request(active_election_id)
                    logging.info('START BEFORE: %s' % (elections_start_before))
                    elections_end_before = elections_end_before()
                    logging.info('END BEFORE: %s' % (elections_end_before))
                    validators_elected_for = validators_elected_for()
                    logging.info('VALIDATORS ELECTED FOR: %s' % (validators_elected_for))
                    second_tick_tock_delay = int(validators_elected_for) - (int(elections_start_before) + int(
                        elections_end_before)) + 1000
                    logging.info('SECOND TICK TOCK DELAY: %s' % second_tick_tock_delay)
                    logging.info('SUBMITTING STAKE')
                    submit_stake()
                    logging.info('STAKE IS SUBMITTED')
                    submitted_election_id = active_election_id
                    logging.info('SUBMITTED ELECTION ID: %s' % submitted_election_id)
                    with open("%s/active-election-id-submitted" % configs_dir, 'w') as the_file:
                        the_file.write(submitted_election_id)
                        logging.info('SAVE ACTIVE-ELECTION-ID TO active-election-id-submitted FILE')
                    with open("%s/second-tick-tock-time" % configs_dir, 'w') as tick_tock_time:
                        tick_tock_time.write(str(int(time.time()) + int(second_tick_tock_delay)))
                        logging.info('SAVE SECOND-TICK-TOCK-TIME TO second-tick-tock-time FILE')
                else:
                    logging.error("ACTIVE_ELECTION_ID_FROM_DEPOOL_EVENT %s DOESNT MATCH TO ACTIVE_ELECTION_ID %s" % (int(active_election_id_from_depool_event), active_election_id))
                    continue
            elif int(active_election_id) == 0:
                logging.info('NO ACTIVE ELECTIONS')
            elif int(active_election_id) == int(submitted_election_id):
                logging.info('ELECTIONS ALREADY SUBMITTED')
        elif validator == 'single':
            if elector_type == 'fift':
                recover_amount = cli_get_recover_amount_fift(elector_addr, msig_addr_hex_0)
                logging.info('recover amount = %s' % recover_amount)
            else:
                recover_amount = cli_get_recover_amount(elector_addr, msig_addr_hex)
                logging.info('recover amount = %s' % recover_amount)
            if recover_amount != "0":
                console_recover_stake()
                boc = recover_query_boc()
                cli_submit_transaction(msig_addr, elector_addr_hex, 1000000000, boc)
                logging.info('RECOVER STAKE REQUESTED')
            else:
                logging.info('NO TOKENS TO RECOVER')
            election_id = cli_get_active_election_id(elector_addr)
            try:
                with open("%s/active-election-id-submitted" % configs_dir, 'r') as the_file:
                    submitted_election_id = the_file.read()
            except:
                submitted_election_id = 0
            if int(election_id) != 0 and int(election_id) != int(submitted_election_id):
                try:
                    console_create_elector_request(election_id)
                    submit_stake()
                    submitted_election_id = election_id
                    with open("%s/active-election-id-submitted" % configs_dir, 'w') as the_file:
                        the_file.write(submitted_election_id)
                except Exception as e:
                    print(e)
                    logging.error('STAKE DOES NOT SENT!')
            else:
                logging.info('ALREADY SUBMITTED OR NOT ACTIVE ELECTIONS')
        else:
            logging.error('VALIDATOR MUST BE depool OR single!')
        time.sleep(60)
    except Exception as e:
        print(e)
        logging.error('VALIDATOR SCRIPT FAILS')
        time.sleep(60)
