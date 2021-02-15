
# **FreeTON Rust Node Installation guide**

**ATTENTION !!! README IS WORK IN PROGRESS !!!**

All scripts are in the active development stage and will be updated regularly. Feel free to contact us using Github issues or directly on Telegram (@sostrovskyi, @renatSK, @azavodovskyi).

This guide contains instructions on how to build and configure a RUST validator node in the Free TON blockchain. The instructions and scripts can be executed on any Debian based Linux distributions but were verified on Ubuntu 18.04 and Ubuntu 20.04.


## System requirements


### TON Rust node


<table>
  <tr>
   <td><strong>Configuration</strong>
   </td>
   <td><strong>CPU (threads)</strong>
   </td>
   <td><strong>RAM (GiB)</strong>
   </td>
   <td><strong>Storage (GiB)</strong>
   </td>
   <td><strong>Network (Gbit/s)</strong>
   </td>
   <td><strong>Operating system</strong>
   </td>
  </tr>
  <tr>
   <td>Minimum
   </td>
   <td>48
   </td>
   <td>64
   </td>
   <td>1000
   </td>
   <td>1
   </td>
   <td>Ubuntu 20.04 \
Ubuntu 18.04
   </td>
  </tr>
</table>


SSD/NVMe disks are obligatory.


### Monitoring server


<table>
  <tr>
   <td><strong>Configuration</strong>
   </td>
   <td><strong>CPU (threads)</strong>
   </td>
   <td><strong>RAM (GiB)</strong>
   </td>
   <td><strong>Storage (GiB)</strong>
   </td>
   <td><strong>Network (Mbit/s)</strong>
   </td>
   <td><strong>Operating system</strong>
   </td>
  </tr>
  <tr>
   <td>Minimum
   </td>
   <td>4
   </td>
   <td>4
   </td>
   <td>500
   </td>
   <td>100
   </td>
   <td>Ubuntu 20.04 \
Ubuntu 18.04
   </td>
  </tr>
</table>

## Prerequisites

1. Free TON Rust node server with public IP and system requirements described above.
2. **Optional** monitoring server with public IP and system requirements described above.
3. Ansible installed. Recommended version 2.9.9. (Can be skipped in case of Quick start)
4. Depool or multisig with enough funds to stake:

    1. **Preferable**. For a depool validator it is necessary to create and deploy a validator [SafeMultisig](https://github.com/tonlabs/ton-labs-contracts/tree/master/solidity/safemultisig) wallet in 0 chain, a depool in 0 chain, put files msig.keys.json and helper.keys.json to keys directory and configure msig_addr and helper_addr in ansible/group_vars/rustnode env file.
        Documentation: [Run DePool v3](https://docs.ton.dev/86757ecb2/p/04040b-run-depool-v3)

    2. For direct staking validator it is necessary to create and deploy a validator [SafeMultisig](https://github.com/tonlabs/ton-labs-contracts/tree/master/solidity/safemultisig) wallet in -1 chain, put file msig.keys.json to keys directory and configure msig_addr in ansible/group_vars/rustnode env file.
        Documentation: [Multisignature Wallet Management in TONOS-CLI](https://docs.ton.dev/86757ecb2/p/94921e-multisignature-wallet-management-in-tonos-cli)

## Quick start

1. Clone project repository 
```
git clone https://github.com/INTONNATION/FreeTON-Rust-Node.git
cd FreeTON-Rust-Node
```
2. Configure variables in ansible/group_vars (refer to Variables section)
3. Execute start scripts
```
./start.sh
```
4. Follow prompts

## 
Advanced start 

1. Configure variables in ansible/group_vars (refer to Variables section)
2. Configure hosts in hosts file
3. Configure execution flow in run.yml
4. Run playbook
```
ansible-playbook -u root --private-key &lt;ssh key> -i hosts run.yml -t install
```

## Manage node

1. Restart. With this tag ansible playbook will be reinstalled from scratch with all databases and configs cleanup.
```
ansible-playbook -u root --private-key &lt;ssh key> -i hosts run.yml -t restart
```
2. Upgrade. With this tag ansible playbook will download the latest release of Rust node and Rust console from project github or build source code on remote VM dependinf on vars in ansible/group_vars/rustnode, install it and restart systemd services.  
```
ansible-playbook -u root --private-key &lt;ssh key> -i hosts run.yml -t upgrade
```

## Variables

All variables are described inside env files under ansible/group_vars/ directory.

## Features

*   Easy install with help of _start.sh_
*   Validator script written on Python (supports Singe and Depool validation(**Preferable**))
*   Validator script controlled by systemd (Cron job failures can be disastrous! **NO CRON** anymore!)
*   No need to have additional tick tock script (all validator logic in one place)
*   Embedded RUST validator node release management or remote build from any commit
*   Upgrade RUST validator node and restart (from scratch) capability
*   Easy to understand and sequential installation procedure (without node start/stop/start manipulation with configs)
*   Configurable logging levels
*   Support of remote log shipping (syslog compatible) (to optimize IOPS)
*   Grafana/loki monitoring
*   Alerting to Telegram channel based on metrics
*   Alerting to Telegram channel based on validator script logs and Rust node logs

## Technology stack

*   **Ansible** - tool which automates all the configuration
*   **Python** - used for validator service
*   **BASH** - used for reusable scripts which can be run on remote VM.
*   **Prometheus** - scrapes metrics from TON-OS-DApp-Server components
*   **Promtail** - logs aggregator/parser
*   **Loki** - log storage 
*   **Grafana** - metrics and logs viewer
*   **Alertmanager** - responsible for alerts and notifications
*   **Alertgram** - Telegram alerts
*   **Node-exporter** - linux VMs metrics agent
*   **Statsd-exporter** - stastd metrics agent

## Build

Installation scripts support remote source code build of the [tonlabs-rust-node](https://github.com/tonlabs/ton-labs-node) and [ton-labs-node-tools](https://github.com/tonlabs/ton-labs-node-tools) or alternatively downloading already compiled binaries from Github releases inside this repository. By skipping remote builds you will be able to automatically upgrade validator nodes without performance degradation on remote nodes. INTONNATION team will take responsibility to build and release compiled binaries for each [tonlabs-rust-node](https://github.com/tonlabs/ton-labs-node) stable release. We recommend to star this project to receive notification about new rustnode releases.
It’s possible to set a specific version or use the latest available code from the master branch. To choose scripts behaviour you can use _build: true/false _variable (refer to Variables section)
Build procedure described in scripts/build.sh. Release procedure described in .github/workflows/[main.yml](https://github.com/INTONNATION/FreeTON-Rust-Node/blob/main/.github/workflows/main.yml).

## Validator scripts

All validator scripts are rewritten on Python. To run validator with our scripts you just need to run one systemd service. All validator logic executes as one process. No need to use several cron jobs. Validator script is running and controlled by systemd service with centralized logging / monitoring and management out of the box. Validator script handles all Tik Tok messages under the hood and sends messages only twice per validation cycle to optimize gas consumption. Python scripts written using tonos-cli but we already started reworking this to use SDK directly, this will provide ability to deeply debug and handle any issue.  See _scripts/sdkvalidator.py _(we have plans to finish it during next months).


## Monitoring

Monitoring server includes metrics and logs. Metrics aggregation is based on Prometheus, Promtail, Grafana, Alertmanager and Alertgram installed on a separate server using docker-compose. TON node server  installation includes node and statsd metrics exporters which send metrics to monitoring server. Alert stack notifies you in Telegram.

**NEED TO ADD MORE INFO HERE**

##  Logging

Specially for TON Rust validator nodes we implement a log shipping approach without storing and even writing logs to the disk. It was specially done to optimize performance during Rust Cap competition. Rust node sends logs directly to remote monitoring server without writing them to syslog or any file. It was done with help of piping stdout/stderr output to _logger _utility.

**NEED TO ADD MORE INFO HERE**
