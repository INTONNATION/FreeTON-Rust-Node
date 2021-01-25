#!/bin/bash

# Prometheus statsd version specification. Defaults to 0.19.0. Versions can be found here: https://github.com/prometheus/statsd_exporter/releases
version=${1:-0.19.0}

#Downloading and installing to PATH

wget https://github.com/prometheus/statsd_exporter/releases/download/v$version/statsd_exporter-$version.linux-amd64.tar.gz
tar xf statsd_exporter-$version.linux-amd64.tar.gz
chmod +x statsd_exporter-$version.linux-amd64/statsd_exporter
mv statsd_exporter-$version.linux-amd64/statsd_exporter /usr/bin/statsd_exporter

# Cleanup
rm -f statsd_exporter-$version.linux-amd64.tar.gz
rm -rf statsd_exporter-$version.linux-amd64/
