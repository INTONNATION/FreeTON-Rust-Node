#!/bin/bash

set -e

. ./env.sh

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

if [ $1 = "--release-tar" ]; then
    tar --transform 's/.*\///g' -cvzf rust-node-tools.tar.gz \
        build/ton-node/target/release/ton_node \
        build/ton-labs-node-tools/target/release/console \
        build/ton-labs-node-tools/target/release/dhtscan \
        build/ton-labs-node-tools/target/release/gendht \
        build/ton-labs-node-tools/target/release/keygen \
        build/ton-labs-node-tools/target/release/print \
        build/ton-labs-node-tools/target/release/zerostate \
        build/tonos-cli/target/release/tonos-cli
fi
