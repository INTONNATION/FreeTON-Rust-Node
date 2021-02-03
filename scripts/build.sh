#!/bin/bash

set -e

. ./env.sh
source ~/.cargo/env

mkdir -p build
cd build

#clone_and_build 1pkg_name 2repo 3commit 4cargo_args

clone_and_build () {
    rm -rf $1
    git clone --recursive $2 $1
    cd $1 && git checkout $3
    cargo build $4
    cd ..
}

clone_and_build ton-node ${TON_NODE_GITHUB_REPO} ${TON_NODE_GITHUB_COMMIT_ID} "--release --features metrics"
clone_and_build ton-labs-node-tools ${TON_NODE_TOOLS_GITHUB_REPO} ${TON_NODE_TOOLS_GITHUB_COMMIT_ID} "--release"
clone_and_build tonos-cli ${TONOS_CLI_GITHUB_REPO} ${TONOS_CLI_GITHUB_COMMIT_ID} "--release"

bins="ton-node/target/release/ton_node \
    ton-labs-node-tools/target/release/console \
    ton-labs-node-tools/target/release/dhtscan \
    ton-labs-node-tools/target/release/gendht \
    ton-labs-node-tools/target/release/keygen \
    ton-labs-node-tools/target/release/print \
    ton-labs-node-tools/target/release/zerostate \
    tonos-cli/target/release/tonos-cli"

if [ ! -z $1 ]; then
    if [ $1 = "--release-tar" ]; then
        tar --transform 's/.*\///g' -cvzf rust-node-tools.tar.gz $bins
    fi
else
    cp -r $bins /usr/local/bin/
fi
