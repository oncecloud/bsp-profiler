#!/bin/bash

#####################################################################################
#Author      : LHearen
#E-mail      : LHearen@gmail.com
#Time        : Thu, 2016-05-05 11:14
#Description : USER_NAME is defaulted to "hadoop"
#           add user and enable sudo command;
#           enable ssh login without password among hosts;
#           update hostname and reset /etc/hosts for each host in the cluster;
#           download and configure java locally;
#           download and configure hadoop locally;
#           install and configure java and hadoop for all the hosts in the cluster;
#####################################################################################

. ./checker.sh

#Default user name shared by the cluster;
USER_NAME="luo"

LOCAL_IP_ADDRESS=$(hostname --ip-address) #get the ip address of the current machine;

#Basic configuration file of the program;
ENV_CONF_FILE="etc/env.conf"
IPS_FILE="etc/ip_addresses"
HOSTS_FILE="etc/hosts"

#Default location where java installed;
JDK_ORIGINAL_FILE="/opt/jdk-8u77-linux-x64.tar.gz"
JDK_UNZIPPED_DIR="/opt"
JDK_FILE="/opt/jdk1.8.0_77"

#Default location where hadoop installed;
HADOOP_ORIGINAL_FILE="/home/$USER_NAME/hadoop-2.7.1.tar.gz"
HADOOP_UNZIPPED_FILE="/home/$USER_NAME/hadoop-2.7.1"
HADOOP_UNZIPPED_DIR="/home/$USER_NAME/"
HADOOP_FILE="/home/$USER_NAME/hadoop"


#Used to update the env.conf of the program according to the user
function update_env {
    echo "#configure jdk environment" > $ENV_CONF_FILE
    echo "export JAVA_HOME=/opt/jdk1.8.0_77" >> $ENV_CONF_FILE
    echo "export JRE_HOME=/opt/jdk1.8.0_77/jre" >> $ENV_CONF_FILE
    echo "export CLASSPATH=.:$CLASSPATH:$JAVA_HOME/lib:$JRE_HOME/lib" >> $ENV_CONF_FILE
    echo "export PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin" >> $ENV_CONF_FILE

    echo "#configure hadoop environment" >> $ENV_CONF_FILE
    echo "export HADOOP_HOME=/home/$USER_NAME/hadoop" >> $ENV_CONF_FILE
    echo "export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin" >> $ENV_CONF_FILE
    echo "export HADOOP_HOME_WARN_SUPPRESS=1" >> $ENV_CONF_FILE
    echo "export CLASSPATH=$CLASSPATH:$HADOOP_HOME/share/hadoop/tools/lib/hadoop-core-1.2.1.jar" >> $ENV_CONF_FILE
}

#Root privilege required
#Add a new user and enable sudo command for each host in the cluster;
function add_user {
    user_name=$1
    ips_file=$2
    for ip in $(cat $ips_file)
    do
        ip_checker $ip
        if [ $? -gt 0 ]
        then
            echo "Wrong IP, check the $ip in $ips_file"
            return 1
        fi
        echo "Adding user [$user_name] for $ip"
        ssh $ip "useradd $user_name &&  passwd $user_name && usermod -aG wheel $user_name"
        echo "User [$user_name] added to $ip group wheel successfully!"
        echo "Now you can use sudo to run root commands in $ip." #if till now the sudo command is not available, you might check /etc/sudoers and uncomment wheel group;
    done
}

#add_user $USER_NAME $IPS_FILE


#Root privilege required
#Converting all the ips in the etc/ip_addresses file to hostnames
#The first will be hadoop-master while all the rest will be hadoop-slavex; x ranges from 1 to n-1
#Then update all the hosts accordingly overwriting the /etc/hosts file
function edit_hosts {
    ips_file=$1
    hosts_file=$2
    count=0
    rm -rf $hosts_file 
    for ip in $(cat $ips_file)
    do
        ip_checker $ip
        if [ $? -gt 0 ]
        then
            echo "Wrong ip, check the [$ip] in $ips_file";
            return 1
        fi
        if [ $count -eq 0 ]
        then
            hostname="hadoop-master"
        else
            hostname="hadoop-slave$count"
        fi
        count=$[count+1]
        echo "$ip $hostname" >> $hosts_file
        echo "Update the hostname of [$ip] to $hostname"
        ssh $ip hostnamectl set-hostname $hostname --static
    done
    echo
    tput setaf 6
    echo "Start to replace /etc/hosts for each host in the cluster..."
    tput sgr0
    for ip in $(cat $ips_file)
    do 
        echo "Updating the /etc/hosts for [$ip"]
        cat $hosts_file | ssh $ip "cat > /etc/hosts"
    done
}

#edit_hosts $IPS_FILE $HOSTS_FILE

#Hadoop user required;
#Used to enable ssh-login to one another among hosts without password
#IP addresses are provided in a file
function enable_ssh_without_pwd {
    user_name=$1
    ips_file=$2
    if [ $user_name != `echo "$USER"` ] || [ `id -u` -eq 0 ] #ensure the current user is the user specified by parameter echo $USER is not enough we need id -u to filter further;
    then 
        echo "The current user should be the working user [$USER_NAME]."
        echo -n "You can use"
        tput setaf 4 
        echo -n " su $USER_NAME "
        tput sgr0
        echo "to achieve this and then re-try."
        return 1
    fi
    for localhost in $(cat $ips_file) #traverse each line of the file - each IP address;
    do
        ip_checker $localhost
        if [ $? -gt 0 ]
        then
            echo "Wrong IP, check the [$localhost] in $ips_file";
            return 1
        fi
        tput setaf 6
        echo "Generating rsa keys for [$localhost"]
        tput sgr0
        ssh -t $localhost "rm -rf ~/.ssh && ssh-keygen -t rsa && touch /home/$user_name/.ssh/authorized_keys && chmod 600 /home/$user_name/.ssh/authorized_keys" #-t is to force sudo command;
    done
    for localhost in $(cat $ips_file)
    do
        for ip in $(cat $ips_file)
        do
            tput setaf 6
            echo "Copy rsa public key from [$localhost] to [$ip"]
            tput sgr0
            ssh -t $localhost "ssh-copy-id -i ~/.ssh/id_rsa.pub $ip " ##enable the remote-host-ssh-login-local-without-password #option -t here is used to enable password required command;
            if [ $? -eq 0 ]
            then
                tput setaf 1
                echo "You can ssh login [$ip] from [$localhost] without password now!"
                tput sgr0
            fi
        done
    done
    return 0
}

#enable_ssh_without_pwd $USER_NAME $IPS_FILE


#Root privilege required - stay in the working directory;
#Download jdk1.8 and configure java, javac and jre;
function install_jdk_local {
    java_checker
    if [ $? -gt 0 ]
    then
        if [ -f $JDK_ORIGINAL_FILE ]
        then
            echo "$JDK_ORIGINAL_FILE already exists, needless to download."
        else
            echo "Start to download jdk 1.8 for 64-bit machine..."
            wget -O $JDK_ORIGINAL_FILE --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u77-b03/jdk-8u77-linux-x64.tar.gz"
            if [ $? -gt 0 ]
            then 
                return 1
            fi
        fi
        tar xzf $JDK_ORIGINAL_FILE -C $JDK_UNZIPPED_DIR
        echo "Configuring jdk now..."
        alternatives --install /usr/bin/java java /opt/jdk1.8.0_77/bin/java 2
        alternatives --config java
        echo "Configuring jar and javac now..."
        alternatives --install /usr/bin/jar jar /opt/jdk1.8.0_77/bin/jar 2
        alternatives --install /usr/bin/javac javac /opt/jdk1.8.0_77/bin/javac 2
        alternatives --set jar /opt/jdk1.8.0_77/bin/jar
        alternatives --set javac /opt/jdk1.8.0_77/bin/javac
        echo
        echo "Java installation completed!"
        echo "Now, you may check by 'java -version'"
        return 0
    fi
}

#install_jdk_local

#Root privilege required - stay in the working directory;
#Install hadoop by unzipping the compressed file and rename the folder;
function install_hadoop_local {
    if [ -f "$HADOOP_ORIGINAL_FILE" ] #check whether hadoop-2.7.1.tar.gz exists or not;
    then 
        echo "$HADOOP_ORIGINAL_FILE already exists, needless to download."
    else
        echo "Start to download $HADOOP_ORIGINAL_FILE ..."
        wget -O $HADOOP_ORIGINAL_FILE http://apache.claz.org/hadoop/common/hadoop-2.7.1/hadoop-2.7.1.tar.gz
        if [ $? -gt 0 ]
        then
            return 1
        fi
    fi
    if [ -d "$HADOOP_FILE" ] #check whether hadoop-2.7.1.tar.gz unzipped or not;
    then
        echo "directory $HADOOP_FILE already exists, needless to install."
    else
        rm -rf $HADOOP_UNZIPPED_FILE
        tar xzf $HADOOP_ORIGINAL_FILE -C $HADOOP_UNZIPPED_DIR 
        mv -f $HADOOP_UNZIPPED_FILE $HADOOP_FILE
    fi
    return 0
}

#install_hadoop_local

#Root privilege required
#Copy all the essential jdk and hadoop files to remotes and configure its environment variables;
function install_for_all_hosts {
    user_name=$1
    env_conf_dir=$2
    ips_file=$3
    java_checker
    if [ $? -gt 0 ] || ! [ -d "$HADOOP_FILE" ] || ! [ -d "$JDK_FILE" ]
    then
        echo "Java or hadoop installed or configured abnormally!"
        echo "Please re-check their installation and re-try."
        return 1
    fi
    #Copy jdk and hadoop files, append environment variables for hosts;
    tput setaf 6
    echo
    echo
    echo "Start to copy related files to other hosts..."
    tput sgr0
    for ip in $(cat $ips_file)
    do
        echo  "[$LOCAL_IP_ADDRESS] connected to [$ip]"
        if [[ $ip != $LOCAL_IP_ADDRESS ]]
        then
            tput setaf 6
            echo "Copy all the essential jdk files to $ip  ..."
            tput sgr0
            ssh $ip "rm -rf $JDK_FILE"
            scp -r $JDK_FILE $ip:/opt/
            tput setaf 6
            echo "Copy all the essential hadoop files to $ip ..."
            tput sgr0
            ssh $ip "rm -rf $HADOOP_FILE"
            scp -r $HADOOP_FILE $user_name@$ip:/home/$user_name/
        fi
        tput setaf 6
        echo "Trying to append environment variables to /home/$user_name/.bashrc for $ip"
        tput sgr0
        cat $env_conf_dir | ssh $ip "cat >> /home/$user_name/.bashrc" 
    done
    echo "You must have configured the *xml files properly according to the cluster."
    while [ 1 ]
    do
        read -p "If not, you need to configure it now, input [ 1|y|Y ] to quit to configure it right now: " flag
        echo
        if [ "$flag" == "1" ] || [ "$flag" == "y" ] || [ "$flag" == "Y" ]
        then
            return 1
        else
            copy_hadoop_configuration_files $ips_file
            break
        fi
    done
    return 0
}

#install_for_all_hosts $USER_NAME $ENV_CONF_FILE $IPS_FILE 

#Used to configure the cluster via the hadoop xml configuration files
function copy_hadoop_configuration_files {
    ips_file=$1
    tput setaf 6
    echo "Start to copy hadoop configuration files to all hosts." 
    tput sgr0 
    for ip in $(cat $ips_file)
    do
        echo "Copy to [$ip]"
        scp hadoop/* root@$ip:/home/$USER_NAME/hadoop/etc/hadoop/ #copy the hadoop configuration files to all the hosts in the cluster;
        echo "Change the owner of the hadoop directory in [$ip]"
        ssh $ip "chown -R $USER_NAME:$USER_NAME /home/$USER_NAME/hadoop" #change the owner and group of the hadoop directory;
    done
}
 
#Last step testing the hadoop installation
function test_hadoop {
    user_name=$1
    if [ $user_name != `echo "$USER"` ] || [ `id -u` -eq 0 ] #ensure the current user is the user specified by parameter echo $USER is not enough we need id -u to filter further;
    then 
        echo "The current user should be the working user [$USER_NAME]."
        echo -n "You can use"
        tput setaf 4 
        echo -n " su $USER_NAME "
        tput sgr0
        echo "to achieve this and then re-try."
        return 1
    fi
    tput setaf 6
    echo "Trying to start the hadoop..."
    tput sgr0
    start-all.sh
    tput setaf 6
    echo "Checking the service..."
    jps
    tput sgr0
}

#test_hadoop $USER_NAME
