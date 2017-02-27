#!/bin/bash

# master_ip=10.100.217.26
# slave_ip_array=(
#       10.100.217.27
#       10.100.217.28
#       10.100.217.200)
# user=centos
# ssh_key="/root/test.key"
# yarn_vcpu_new_value="<value>8<\/value>"
# yarn_mem_new_value="<value>8192<\/value>"
while read line;do
    eval "$line"
done < cluster_yarn.conf

yarn_vcpu_new_value=${yarn_vcpu_new_value/\//\\/}
yarn_mem_new_value=${yarn_mem_new_value/\//\\/}

extend_yarn_default_vcpu_setting="sudo su - -c \"sed -i '\\\$!N;\\\$!P;\\\$!D;s/\(\n\)/\n  <property>\n    <name>yarn.nodemanager.resource.cpu-vcores<\/name>\n    $yarn_vcpu_new_value\n  <\/property>\n  <property>\n    <name>yarn.scheduler.maximum-allocation-vcores<\/name>\n    $yarn_vcpu_new_value\n  <\/property>\n/' /opt/hadoop/etc/hadoop/yarn-site.xml\" hadoop"

del_loopback="sudo sed -i '/^127.0.0.1/d' /etc/hosts"
yarn_vcpu_old_value="sudo grep -A 1 \"yarn.nodemanager.resource.cpu-vcores\" /opt/hadoop/etc/hadoop/yarn-site.xml | tail -1"
yarn_mem_old_value="sudo grep -A 1 \"yarn.nodemanager.resource.memory-mb\" /opt/hadoop/etc/hadoop/yarn-site.xml | tail -1"
datanode_start="sudo su - -c \"hadoop-daemon.sh start datanode\" hadoop"
nodemanager_start="sudo su - -c  \"yarn-daemon.sh start nodemanager\" hadoop"
historyserver_start="sudo su - -c \"mr-jobhistory-daemon.sh start historyserver\" hadoop"
namenode_start="sudo su - -c \"hadoop-daemon.sh start namenode\" hadoop"
resourcemanager_start="sudo su - -c  \"yarn-daemon.sh start resourcemanager\" hadoop"
datanode_stop="sudo su - -c \"hadoop-daemon.sh stop datanode\" hadoop"
nodemanager_stop="sudo su - -c  \"yarn-daemon.sh stop nodemanager\" hadoop"
historyserver_stop="sudo su - -c \"mr-jobhistory-daemon.sh stop historyserver\" hadoop"
namenode_stop="sudo su - -c \"hadoop-daemon.sh stop namenode\" hadoop"
resourcemanager_stop="sudo su - -c  \"yarn-daemon.sh stop resourcemanager\" hadoop"

#yarn_stop="sudo su - -c \"/opt/hadoop/sbin/stop-yarn.sh\" hadoop"
#yarn_start="sudo su - -c \"/opt/hadoop/sbin/start-yarn.sh\" hadoop"

replace_yarn_config()
{
    echo "sudo su - -c \"sed -i 's/$1/$2/g' /opt/hadoop/etc/hadoop/yarn-site.xml\" hadoop"
}

stop_yarn()
{
    ssh -i $ssh_key $user@$master_ip "$del_loopback && $historyserver_stop && $namenode_stop && $resourcemanager_stop"
    for slave_ip in ${slave_ip_array[@]}
    do
        ssh -i $ssh_key $user@$slave_ip "$del_loopback && $datanode_stop && $nodemanager_stop"
    done
}

start_yarn()
{
    ssh -i $ssh_key $user@$master_ip "$del_loopback && $historyserver_start && $namenode_start && $resourcemanager_start"
    for slave_ip in ${slave_ip_array[@]}
    do
        ssh -i $ssh_key $user@$slave_ip "$del_loopback && $datanode_start && $nodemanager_start"
    done
}

restart_yarn()
{
    stop_yarn
    start_yarn
}

reconfigure_yarn()
{
    yarn_vcpu_value=`ssh -i $ssh_key $user@$master_ip "$yarn_vcpu_old_value"`
    yarn_mem_value=`ssh -i $ssh_key $user@$master_ip "$yarn_mem_old_value"`
    if [ -z "$yarn_vcpu_value" ];then
        echo "Add default vcpu settings in Yarn configure file."
        `ssh -i $ssh_key $user@$master_ip "$extend_yarn_default_vcpu_setting"`
        yarn_vcpu_value=$yarn_vcpu_new_value
    else
        yarn_vcpu_value=${yarn_vcpu_value/\//\\/}
    fi
    yarn_mem_value=${yarn_mem_value/\//\\/}
    edit_yarn_vcpu_config=`replace_yarn_config $yarn_vcpu_value $yarn_vcpu_new_value`
    edit_yarn_mem_config=`replace_yarn_config $yarn_mem_value $yarn_mem_new_value`
    ssh -i $ssh_key $user@$master_ip "$edit_yarn_vcpu_config && $edit_yarn_mem_config"
    
    for slave_ip in ${slave_ip_array[@]}
    do
        yarn_vcpu_value=`ssh -i $ssh_key $user@$slave_ip "$yarn_vcpu_old_value"`
        yarn_mem_value=`ssh -i $ssh_key $user@$slave_ip "$yarn_mem_old_value"`
        if [ -z "$yarn_vcpu_value" ];then
            echo "Add default vcpu settings in Yarn configure file."
            `ssh -i $ssh_key $user@$slave_ip "$extend_yarn_default_vcpu_setting"`
            yarn_vcpu_value=$yarn_vcpu_new_value
        else
            yarn_vcpu_value=${yarn_vcpu_value/\//\\/}
        fi
        yarn_mem_value=${yarn_mem_value/\//\\/}
        edit_yarn_vcpu_config=`replace_yarn_config $yarn_vcpu_value $yarn_vcpu_new_value`
        edit_yarn_mem_config=`replace_yarn_config $yarn_mem_value $yarn_mem_new_value`
        ssh -i $ssh_key $user@$slave_ip "$edit_yarn_vcpu_config && $edit_yarn_mem_config"
    done
    restart_yarn
}

case "$1" in
    start)
        start_yarn
    	;;
    stop)
        stop_yarn
    	;;
    restart)
        restart_yarn
    ;;
    reconfigure)
        reconfigure_yarn
    ;;
*)
    echo "Usage: bash cluster-yarn.sh {start|stop|restart|reconfigure}"
    exit 1
    ;;
esac
exit 0
