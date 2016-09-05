#!/bin/bash
#####################################################################################
#Author      : LHearen
#E-mail      : LHearen@gmail.com
#Time        : Wed, 2016-05-25 19:16
#Description : Used to check the network distance among hosts;
#####################################################################################

function distance_checker {
    ips_file=$1
    count=$2
    for localhost in $(cat $ips_file)
    do
        tput setaf 1
        echo "Source IP address is [$localhost]"
        tput sgr0
        for ip in $(cat $ips_file)
        do
            if [[ $localhost != $ip ]]
            then
                tput setaf 6
                echo "[$localhost] pinging [$ip]..."
                tput sgr0
                ssh $localhost "ping -c$count $ip"
            fi
        done
    done
}

distance_checker "etc/ip_addresses" 5

