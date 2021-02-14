# **FreeTON Rust Node Installation guide**

All scripts are in the active development stage and will be updated regularly. Feel free to contact as on github thought issues or directly on Telegram. Scripts done by validators for validators. 

This guide contains instructions on how to build and configure a RUST validator node in TON blockchain. The instructions and scripts can be executed on any Debian based Linux distributions but were verified on Ubuntu 18.04 and Ubuntu 20.04.

**Repo**: [https://github.com/INTONNATION/FreeTON-Rust-Node](https://github.com/INTONNATION/FreeTON-Rust-Node) 

**Note**: more info can be found in the README file inside a repository.


## Features



*   Easy install with help of _start.sh_
*   Validator script written on Python (supports Singe and Depool validation)
*   Validator script controlled by systemd (Cron job failures can be disastrous! no cron anymore!)
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
*   **Loki **- log storage 
*   **Grafana **- metrics and logs viewer
*   **Alertmanager **- responsible for alerts and notifications
*   **Alertgram **- Telegram alerts
*   **Node-exporter** - linux VMs metrics agent
*   **Statsd-exporter** - stastd metrics agent


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
   <td>Ubuntu 20.04/ \
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



1. Server for TON Rust node with system requirements described above with public IP and 30303 udp port opened.
2. Monitoring server system requirements described above with public IP and 1514 and 3000 tcp ports opened (Optional)
3. Ansible installed. Recommended version 2.9.9. (Can be skipped in case of Quick start)
4. Depool or multisig with enough funds to stake:
    1. For direct staking validator it is necessary to create and deploy a validator [SafeMultisig](https://github.com/tonlabs/ton-labs-contracts/tree/master/solidity/safemultisig) wallet in -1 chain and place file on the validator node: /etc/rust-validator/msig.keys.json (validator multisignature custodian's keypair). If there are more than 1 custodian make sure each transaction sent by the validator is confirmed by the required amount of custodians. And put validator multisignature wallet address in form -1:XXX...XXX) to FreeTON-Rust-Node/ansible/group_vars/rustnode: `wallet_addr` \
Documentation: [Multisignature Wallet Management in TONOS-CLI](https://docs.ton.dev/86757ecb2/p/94921e-multisignature-wallet-management-in-tonos-cli)
    2. For a depool validator it is necessary to create and deploy a validator [SafeMultisig](https://github.com/tonlabs/ton-labs-contracts/tree/master/solidity/safemultisig) wallet in 0 chain, a depool in 0 chain and place 2 files on the validator node: /etc/rust-validator/msig.keys.json (validator multisignature custodian's keypair) and /etc/rust-validator/helper.keys.json and also add validator multisignature wallet address in form 0:XXX...XXX) and depool address in form 0:XXX...XXX to FreeTON-Rust-Node/ansible/group_vars/rustnode: `wallet_addr/depool_addr` \
Documentation: [Run DePool v3](https://docs.ton.dev/86757ecb2/p/04040b-run-depool-v3)


## Quick start



1. Clone project repository \
_git clone [https://github.com/INTONNATION/FreeTON-Rust-Node.git](https://github.com/INTONNATION/FreeTON-Rust-Node.git)_

    _cd FreeTON-Rust-Node_

2. Execute start scripts

    _./start.sh_

3. Follow prompts

## 
Advanced start 

1. Configure variables in ansible/group_vars (refer to Variables section)
2. Configure hosts in hosts file
3. Configure execution flow in run.yml
4. ansible-playbook -u root --private-key &lt;ssh key> -i hosts run.yml -t install


## Manage node



1. Restart

    _ansible-playbook -u root --private-key &lt;ssh key> -i hosts run.yml -t restart_


    With this tag ansible playbook will reinstall node from scratch with all databases and configs cleanup.

2. Upgrade

    _ansible-playbook -u root --private-key &lt;ssh key> -i hosts run.yml -t upgrade_


    This tag will download the latest release of Rust node and Rust console from project github or build source code on remote VM, install it and restart systemd services.  



## Variables


### TON node


<table>
  <tr>
   <td><strong>Parameter</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Default</strong>
   </td>
  </tr>
  <tr>
   <td>statsd_version
   </td>
   <td>Version of statsd binary
   </td>
   <td>0.19.0
   </td>
  </tr>
  <tr>
   <td>statsd_dir
   </td>
   <td>Directory where located statsd config
   </td>
   <td>/etc/statsd
   </td>
  </tr>
  <tr>
   <td>git_repo
   </td>
   <td>Current project repository
   </td>
   <td>INTONNATION/FreeTON-Rust-Node
   </td>
  </tr>
  <tr>
   <td>scripts_dir
   </td>
   <td>Remote directory to which installation scripts will put scripts
   </td>
   <td>/opt/FreeTON-Rust-Node
   </td>
  </tr>
  <tr>
   <td>release_version
   </td>
   <td>Version of RUST Node (https://github.com/INTONNATION/FreeTON-Rust-Node/releases)
   </td>
   <td>7a091cc
   </td>
  </tr>
  <tr>
   <td>wallet_addr
   </td>
   <td>Multisig address for validator
   </td>
   <td>0:5dcaaa93f50d148e66d4504457d008528b5ca0d1365146816a80b656520f748d
   </td>
  </tr>
  <tr>
   <td>build
   </td>
   <td>If true, it will be built on a remote server. If not, download from github releases.
   </td>
   <td>true
   </td>
  </tr>
  <tr>
   <td>ipdiscovery
   </td>
   <td> local, auto, or IP_ADDR
   </td>
   <td>local
   </td>
  </tr>
  <tr>
   <td>ton_network_global_conf_url
   </td>
   <td>Raw URL to TON network global config (any TON network supported)
   </td>
   <td>https://raw.githubusercontent.com/FreeTON-Network/fld.ton.dev/main/configs/fld.ton.dev/ton-global.config.json
   </td>
  </tr>
  <tr>
   <td>database_path
   </td>
   <td>Remote path for RUST Node rocksdb databases
   </td>
   <td>/opt/node_db
   </td>
  </tr>
  <tr>
   <td>rustnode_conf_dir
   </td>
   <td>Remote path to configuration files (config.json,console.json)
   </td>
   <td>/etc/rustnode
   </td>
  </tr>
  <tr>
   <td>logging
   </td>
   <td>Logging configuration
   </td>
   <td>remote.enabled: true
<p>
level.root: debug
   </td>
  </tr>
</table>



### Monitoring server


<table>
  <tr>
   <td><strong>Parameter</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Default</strong>
   </td>
  </tr>
  <tr>
   <td>telegram_api_token
   </td>
   <td>Telegram token for alerts
   </td>
   <td>-
   </td>
  </tr>
  <tr>
   <td>telegram_chat_id
   </td>
   <td>Telegram channel for alerts
   </td>
   <td>-
   </td>
  </tr>
  <tr>
   <td>grafana_username
   </td>
   <td>Username for monitoring server UI
   </td>
   <td>-
   </td>
  </tr>
  <tr>
   <td>grafana_password
   </td>
   <td>Password for monitoring server UI
   </td>
   <td>-
   </td>
  </tr>
</table>



## Build

Installation scripts support remote building source code of the [tonlabs-rust-node](https://github.com/tonlabs/ton-labs-node) and [ton-labs-node-tools](https://github.com/tonlabs/ton-labs-node-tools) or alternatively downloading already compiled binaries (**recommended!**) from current github releases.

By skipping remote builds you will be able to automatically upgrade validator nodes without performance degradation on remote nodes. INTONNATION team will take responsibility to build and release compiled binaries for each [tonlabs-rust-node](https://github.com/tonlabs/ton-labs-node) stable release. 

We recommend to star this project to receive notification about a new rustnode release.

It’s possible to set a specific version or use the latest available code from the master branch. To choose scripts behaviour you can use _build: true/false _variable (refer to Variables section)

Build procedure described in scripts/build.sh. Release procedure described in .github/workflows/[main.yml](https://github.com/INTONNATION/FreeTON-Rust-Node/blob/main/.github/workflows/main.yml). Variables for build described in scripts/env.sh


## Validator scripts

All validator scripts were rewritten on Python. To run validator with our scripts you just need to run one systemd service. All validator logic executes as one process. No need to use several cron jobs. Validator script is running and controlled by systemd service with centralized logging / monitoring and management out of the box. Validator script handles all Tik Tok messages under the hood and sends messages only twice per validation cycle to optimize gas consumption. Python scripts written using tonos-cli but we already started reworking this to use SDK directly, this will provide ability to deeply debug and handle any issue.  See _scripts/sdkvalidator.py _(we have plane to finish it during next months)


## Monitoring

Monitoring server is based on Prometheus, Promtail, Grafana, Alertmanager and Alertgram installed on a separate server using docker-compose. TON node server  installation includes node and statsd metrics exporters which send metrics to monitoring server. 



<p id="gdcalert1" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image1.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert2">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image1.png "image_tooltip")



##  Logging

Specially for TON Rust validator nodes we implement a log shipping approach without storing and even writing logs to the disk. It was specially done to optimize performance during Rust Cap competition. Rust node sends logs directly to remote monitoring server without writing them to syslog or any file. It was done with help of piping stdout/stderr output to _logger _utility.



<p id="gdcalert2" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image2.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert3">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image2.png "image_tooltip")

