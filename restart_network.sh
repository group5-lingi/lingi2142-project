#!/bin/bash

# clean up
./cleanup.sh

# recreate conf
./templates/auto/create.py ./templates/auto/auto_topo > ./templates/auto/conf.json

# templates
./templates/create_config.py

# start netwwork
./create_network ./templates/auto/isp_topo
