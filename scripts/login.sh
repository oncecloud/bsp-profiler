#!/bin/bash
#####################################################################################
#Author      : LHearen
#E-mail      : LHearen@gmail.com
#Time        : Thu, 2016-05-05 11:12
#Description : When using DHCP login process is quite essential to access external network
#####################################################################################

function login_network {
    userName="luosonglei14"
    password=${2-111111}
    while [ 1 ]
    do
        tmp=$(mktemp curlTmp.XXX)
        echo "curl -d 'username=$userName&password=$password&pwd=$password&secret=true' http://133.133.133.150/webAuth/ >$tmp 2>/dev/null"
        curl -d "username=$userName&password=$password&pwd=$password&secret=true" http://133.133.133.150/webAuth/ >$tmp 2>/dev/null
        result=$(cat $tmp | sed -n '/authfailed/p')
        if [ ! -s "$tmp" ]
        then
            echo "NoResponse!"
            rm -f $tmp
            sleep 3s
            continue
        else
            rm -f $tmp
            if [ -n "$result" ]
            then
                echo "AuthFailed!"
                echo "Hint: in this case, you either have already logged in or you are using a wrong account."
                break
            else
                echo "Successfully log in!!"
                break
            fi
        fi
    done
}

#clear
#echo "Using a fixed account to login - simulating browser login process."
#tput setaf 6
#echo "[Usage: UserName, Password[default: 111111]]"
#tput sgr0
#echo
#read -p "UserName:" userName
#tput setaf 6
#echo "Press Enter to use default password 111111"
#tput sgr0
#read -p "Password:" password
#login_network $userName $password
