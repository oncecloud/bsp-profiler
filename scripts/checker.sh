#!/bin/bash
#####################################################################################
#Author      : LHearen
#E-mail      : LHearen@gmail.com
#Time        : Thu, 2016-05-05 11:12
#Description : This script is used to check the network and commands 
#              It will try to fix it first but prompt a warning when failed
#####################################################################################

#exec 1>>output.log
#exec 2>>err.log


. ./login.sh
###############################################################
#Used to restore and backup ks.cfg isolinux.cfg for iso-making
###############################################################
function check_cfgs {
    local exit_code=0
    check_cfg "ks.cfg"
    if [ $? -gt 0 ]
    then
        ((exit_code++))
    fi
    check_cfg "isolinux.cfg"
    if [ $? -gt 0 ]
    then
        ((exit_code++))
    fi
    if [ $exit_code -gt 0 ]
    then
        return 1
    else
        return 0
    fi
}

#####################################################
#Make a certain file has backup and at the same time 
#When there is a backup, use it to restore the file
#####################################################
function check_cfg {
    file=$1
    if [ -e $file".bak" ]
    then
        echo "Using $file".bak" to reset $file."
        cp -f $file".bak" $file
        return 0
    else
        echo "$file".bak" does not exist!"
        if [ -e $file ]
        then
            echo "Backing up $file ..."
            cp $file $file".bak"
            if [ $? -eq 0 ]
            then
                echo "Backing up $file successfully!"
                return 0
            else
                echo "Failed backing up $file!"
                echo "Please back it up manually."
                return 1
            fi
        else
            echo
            echo "$file does not exist in the current directory!"
            return 1
        fi
    fi    
}


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


####################################
#Check the network and try to fix it
####################################
function check_fix_network {
    return_code=`check_network "baidu.com"`
    if [ $return_code -eq 200 ]
    then
        echo "Network available"
    else
        echo "Connection error!"
        echo "Trying to fix the network..."
        service network restart > /dev/null  
        login_network
        return_code=`check_network "baidu.com"`
        if [ $return_code -eq 200 ]
        then
            echo "Network available now."
            return 0
        else
            echo "Failed to fix the connection."
            echo "When you are using ISCAS Network, you might have to run login.sh first, enclosed with this program"
            echo "To login in to access network."
            echo "If you are using other networks, you should try to use browser to login or rewrite the login.sh to login."
            echo "Remember sometimes 'ping works' does not mean you can access network normally and install online packages."
            echo "You have to fix the network by yourself now."
            echo "Leaving the script..."
            return 1
        fi 
    fi
}

#check_fix_network

####################################################
#Ensure the root privelege is granted to the script
####################################################
function check_permission {
    if [ $UID -ne 0 ]
    then
        echo
        echo "Pemission denied!"
        echo "To run this program successfully "
        echo "Try to use root account or sudo command."
        return 1
    else
	return 0
    fi
}


##############################################
#Check the existence of a certain package 
#And try to install it if it was not installed
##############################################
function check_package {
    package=$1
    check=`rpm -qa | grep $package`
    if [ -z "$check" ]
    then
        echo
        echo "Tool - $package is not installed."
        echo "To run the program properly, we have to install it first."
        echo "Installing $package ..."
        echo
        yum install -y $package $1>/dev/null $2>/dev/null
        if [ $? -eq 0 ]
        then
            echo "$package installed successfully!"
            return 0
        else
            echo "Failed installing $package ."
            echo "Make sure your internet is connected and re-try later."
            echo
            return 1
        fi
    else
        echo "$package has been installed!"
        return 0
    fi
}

##############################################
#Ensure the whole program to run as expected,
#Some essential packages should be installed 
#Before running this program; this function 
#Is used to check their existence and install 
#Them if they are not installed so far
##############################################
function check_essential_packages {
    exit_code=0
    check_package "openssh" 
    if [ $? -gt 0 ]
    then 
        exit_code=1
    fi
    return $exit_code
}

#check_essential_packages 

function ip_checker {
    local ip=$1
    result=`echo $ip | gawk --re-interval '/^([0-9]{1,3}|\*)\.([0-9]{1,3}|\*)\.([0-9]{1,3}|\*)\.([0-9]{1,3}|\*)$/'`
    #echo $result
    if [ -z "$result" ]
    then
        return 1
    fi

    tmp=`echo $ip | sed "s/\./ /g; s/\*/a/g"`
    #echo ${tmp[*]}
    for a in $tmp
    do
        #echo $a
        if [ $a != "a" ] && [ $a -gt 255 ] 
        then
            return 1
        fi
    done
    return 0
}
#while true
#do
    #read -p "Input the ip to test: " ip
    #ip_checker $ip
    #if [ $? -eq 0 ]
    #then
        #echo "Correct!"
    #else
        #echo "Wrong!"
    #fi
#done

#Check whether jdk 1.8 installed or not
#return 1 if not installed otherwise return 0;
function java_checker {
    ret=$(java -version 2>&1 | sed -n "/1.8/p")
    if [ "$ret" == "" ]
    then
        echo "java 1.8 not installed"
        return 1
    else
        echo "java 1.8 already installed"
        echo "You may check its version by 'java -version'"
        return 0
    fi
}

#Used to center the text in bash;
function display_center {
    COLUMNS=$( tput cols )
    title=$1
    printf "%*s\n" $(((${#title}+$COLUMNS)/2)) "$title"
}
