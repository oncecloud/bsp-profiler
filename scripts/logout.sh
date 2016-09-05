#!/bin/bash
#####################################################################################
#Author      : LHearen
#E-mail      : LHearen@gmail.com
#Time        : Thu, 2016-05-05 14:46
#Description : Used to logout from ISCAS network;
#####################################################################################

#############################
#Using a given test site to
#Check the network and return
#Http code 200 - okay
#############################
function check_network {
   test_site=$1
   timeout_max=2    #seconds before time out
   return_code=`curl -o /dev/null/ --connect-timeout $timeout_max -s -w %{http_code} $test_site`
   echo $return_code
}

function send_logout_request {
    tmp=$(mktemp tmp_logout.XXX)
    t=$(date +%s)
    echo "curl http://133.133.133.150/ajaxlogout?_t=$t >$tmp"
    curl http://133.133.133.150/ajaxlogout?_t=$t >$tmp
    echo "Logout request sent successfully!"
    echo
    rm -f $tmp
}

function logout_network {
    send_logout_request
    return_code=`check_network "cn.bing.com"`
    if [ $return_code -eq 200 ]
    then 
        echo "Failed logging out!"
        echo "Try again later"
    else
        echo "Log out successfully!"
    fi
}

logout_network

