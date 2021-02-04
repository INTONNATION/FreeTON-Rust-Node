import os
import datetime
import logging
import json
import subprocess

elector_addr="-1:3333333333333333333333333333333333333333333333333333333333333333"
msig_addr_hex="0x4000610da7d7f89b92cd64212e5b983d9ccac9938333174f352a5b3c416997c4"
msig_addr="0:4000610da7d7f89b92cd64212e5b983d9ccac9938333174f352a5b3c416997c4"
# It stores ABIs, keys and configs like  msig.keys.json, Elector.abi.json, SafeMultisigWallet.abi.json, console.json etc
configs_dir="/etc/rustnode"
remained_for_fees=100

logging.basicConfig(
    level=logging.INFO,
    format="DateTime : %(asctime)s : %(levelname)s : %(message)s",)

# Add tonos-cli setup to playbook
# place Elector.abi.json, SafeMultisigWallet.abi.json, msig.keys.json to configs dir

try:
    recover_amount=cli_get_recover_amount()
    if recover_amount != "0":
        logging.info(recover_amount)
        console_recover_stake()
        boc=recover_query_boc()
        cli_submit_transaction(msig_addr, elector_addr, 1000000000, boc)
except:
    logging.info('recover_amount is empty')

try: 
    active_election_id=cli_get_active_election_id(elector_addr)
    if active_election_id != "0":
        console_create_elector_request()
        boc=validator_query_boc()
        stake=get_stake()
except:
    logging.info('No current elections')

def cli_get_recover_amount (elector_addr: str, msig_addr_hex: str):
    recover_amount=subprocess.check_output('tonos-cli run %s compute_returned_stake \"{\\"wallet_addr\\":\\"%s\\"}\" --abi %s/Elector.abi.json' % (elector_addr, msig_addr_hex, configs_dir), encoding = 'utf-8', shell=True)
    return recover_amount

def console_recover_stake ():
    os.system('console -C %s/console.json -c recover_stake' % (configs_dir))

def recover_query_boc ():
    recover_query_boc=subprocess.check_output('base64 --wrap=0 recover-query.boc', encoding = 'utf-8', shell=True)
    return recover_query_boc

def cli_submit_transaction (msig_addr_hex: str, elector_addr: str, value: str, boc: str):
    subprocess.check_output('tonos cli call %s submitTransaction \
            \"{\\"dest\\":\\"%s\\",\\"value\\":\\"%s\\",\\"bounce\\":true,\\"allBalance\\":false,\\"payload\\":\\"%s\\"}\" \
            --abi %s/SafeMultisigWallet.abi.json \
            --sign %s/msig.keys.json' % (msig_addr_hex, elector_addr, value, boc, configs_dir, configs_dir), encoding = 'utf-8', shell=True)

def cli_get_active_election_id (elector_addr: str):
    active_election_id=subprocess.check_output('tonos-cli run %s active_election_id {} --abi %s/Elector.abi.json | grep value0 | awk \'{print $2}\' | tr -d \"\\"\"|tr -d \"\n\"' % (elector_addr, configs_dir), encoding = 'utf-8', shell=True)
    return active_election_id

def console_create_elector_request():
    os.system('tonos-cli getconfig 15 > global_config_15_raw')
    elections_end_before=os.system('cat global_config_15_raw | grep elections_end_before | awk \'{print $2}\' | tr -d \',\'')
    elections_start_before=os.system('cat global_config_15_raw | grep "elections_start_before" | awk \'{print $2}\' | tr -d \',\'')
    stake_held_for=os.system('cat global_config_15_raw | grep "stake_held_for" | awk \'{print $2}\' | tr -d \',\'')
    validators_elected_for=os.system('cat global_config_15_raw | grep "validators_elected_for" | awk \'{print $2}\' | tr -d \',\'')
    election_start=cli_get_active_election_id(elector_addr)
    election_stop=(int(election_start) + 1000 +  elections_start_before + elections_end_before + stake_held_for + validators_elected_for)
    print(election_start)
    os.system('console -C %s/console.json -c "election-bid %s %s"' % (configs_dir, election_start, election_stop))

def validator_query_boc():
    validator_query_boc=subprocess.check_output('base64 --wrap=0 validator-query.boc', encoding = 'utf-8', shell=True)
    return validator_query_boc

def check_validator_balance (msig_addr_hex: str):
    balance=subprocess.check_output('tonos-cli account %s | grep balance | awk \'{print $2}\'' % (msig_addr_hex), shell=True)
    balance_in_tokens= balance / 1000000000
    return balance_in_tokens

def get_min_stake (): 
    min_stake=subproccess.check_output('tonos-cli getconfig 17 | grep min_stake | awk \'{print $2}\' | tr -d \'\\"\' | tr -d \',\'', encoding = 'utf-8',  shell=True)
    min_stake_in_tokens=str(min_stake) / 1000000000
    return min_stake_in_tokens

def get_stake():
    actual_balance=check_validator_balance()
    stake=(actual_balance - remained_for_fees)/2
    return stake

def submit_stake():
    stake=get_stake()
    nanostake=subprocess.check_output('tonos-cli convert tokens %s | tail -1' % (int(stake)), encoding = 'utf-8', shell=True)
    boc=validator_query_boc();
    cli_submit_transaction(msig_addr_hex, elector_addr, nanostake, boc)
