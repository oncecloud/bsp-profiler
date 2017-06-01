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
master_stop_cmd="$del_loopback"
master_start_cmd="$del_loopback"
worker_stop_cmd="$del_loopback"
worker_start_cmd="$del_loopback"

for restart_service in ${restart_services_array[@]}
do
	if [[ $restart_service == "resourcemanager" ]];then
		master_stop_cmd=$master_stop_cmd" && $resourcemanager_stop"
		master_start_cmd=$master_start_cmd" && $resourcemanager_start"
	elif [[ $restart_service == "namenode" ]];then
		master_stop_cmd=$master_stop_cmd" && $namenode_stop"
		master_start_cmd=$master_start_cmd" && $namenode_start"
	elif [[ $restart_service == "historyserver" ]];then
		master_stop_cmd=$master_stop_cmd" && $historyserver_stop"
		master_start_cmd=$master_start_cmd" && $historyserver_start"
	elif [[ $restart_service == "nodemanager" ]];then
		worker_stop_cmd=$worker_stop_cmd" && $nodemanager_stop"
		worker_start_cmd=$worker_start_cmd" && $nodemanager_start"
	elif [[ $restart_service == "datanode" ]];then
		worker_stop_cmd=$worker_stop_cmd" && $datanode_stop"
		worker_start_cmd=$worker_start_cmd" && $datanode_start"
	fi
done

#yarn_stop="sudo su - -c \"/opt/hadoop/sbin/stop-yarn.sh\" hadoop"
#yarn_start="sudo su - -c \"/opt/hadoop/sbin/start-yarn.sh\" hadoop"

replace_yarn_config()
{
    echo "sudo su - -c \"sed -i 's/$1/$2/g' /opt/hadoop/etc/hadoop/yarn-site.xml\" hadoop"
}

stop_yarn()
{
    ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "$master_stop_cmd"
    for slave_ip in ${slave_ip_array[@]}
    do
        ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "$worker_stop_cmd"
    done
}

start_yarn()
{
    ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "$master_start_cmd"
    for slave_ip in ${slave_ip_array[@]}
    do
        ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "$worker_start_cmd"
    done
}

restart_yarn()
{
    stop_yarn
    start_yarn
}

reconfigure_yarn()
{
    yarn_vcpu_value=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "$yarn_vcpu_old_value"`
    yarn_mem_value=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "$yarn_mem_old_value"`
    if [ -z "$yarn_vcpu_value" ];then
        echo "Add default vcpu settings in Yarn configure file."
        `ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "$extend_yarn_default_vcpu_setting"`
        yarn_vcpu_value=$yarn_vcpu_new_value
    else
        yarn_vcpu_value=${yarn_vcpu_value/\//\\/}
    fi
    yarn_mem_value=${yarn_mem_value/\//\\/}
    edit_yarn_vcpu_config=`replace_yarn_config $yarn_vcpu_value $yarn_vcpu_new_value`
    edit_yarn_mem_config=`replace_yarn_config $yarn_mem_value $yarn_mem_new_value`
    ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "$edit_yarn_vcpu_config && $edit_yarn_mem_config"
    
    for slave_ip in ${slave_ip_array[@]}
    do
        yarn_vcpu_value=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "$yarn_vcpu_old_value"`
        yarn_mem_value=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "$yarn_mem_old_value"`
        if [ -z "$yarn_vcpu_value" ];then
            echo "Add default vcpu settings in Yarn configure file."
            `ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "$extend_yarn_default_vcpu_setting"`
            yarn_vcpu_value=$yarn_vcpu_new_value
        else
            yarn_vcpu_value=${yarn_vcpu_value/\//\\/}
        fi
        yarn_mem_value=${yarn_mem_value/\//\\/}
        edit_yarn_vcpu_config=`replace_yarn_config $yarn_vcpu_value $yarn_vcpu_new_value`
        edit_yarn_mem_config=`replace_yarn_config $yarn_mem_value $yarn_mem_new_value`
        ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "$edit_yarn_vcpu_config && $edit_yarn_mem_config"
    done
    restart_yarn
}

install_ganglia()
{
	if [ -n "$1" ];then
		echo "Restarting ganglia services in cluster $cluster_name."
	else
		echo "Installing ganglia services in cluster $cluster_name."
		scp_rpms=`scp -i $ssh_key -o StrictHostKeyChecking=no -r $ganglia_rpms $user@$master_ip:~`
		if [[ $? -eq 0 ]];then
			echo -e "Scp rpms to Master status: \033[42;37m Success \033[0m"
		else
			echo -e "Scp rpms to Master status: \033[41;37m Failed \033[0m"
			exit 1
		fi
		install_rpms=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo rpm -Uvh --force ~/ganglia-rpms/master/*.rpm"`
		if [[ $? -eq 0 ]];then
			echo -e "Install rpms on Master status: \033[42;37m Success \033[0m"
		else
			echo -e "Install rpms on Master status: \033[41;37m Failed \033[0m"
			exit 1
		fi
	fi
	echo "Now working on Master."
	echo "Changing authorization of (web, rrd, dwoo) directories."
	ln_ganglia_web=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo ln -sf /usr/share/ganglia /var/www/html"`
	chown_ganglia_web=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo chown -R apache:apache /var/www/html/ganglia"`
	chmod_ganglia_web=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo chmod -R 755 /var/www/html/ganglia"`
	chown_ganglia_rrd=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo chown -R nobody:nobody /var/lib/ganglia/rrds"`
	chmod_ganglia_dwoo1=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo chmod 777 /var/lib/ganglia/dwoo/compiled"`
	chmod_ganglia_dwoo2=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo chmod 777 /var/lib/ganglia/dwoo/cache"`
	master_hostname=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "hostname"`
	echo "Backing up configuration files."
	test_backup_files=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo test -f /etc/ganglia/gmond.conf.bak"`
	if [[ $? -eq 0 ]];then
		init_ganglia_configure_file=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo cp /etc/httpd/conf.d/ganglia.conf.bak /etc/httpd/conf.d/ganglia.conf && sudo cp /etc/ganglia/gmetad.conf.bak /etc/ganglia/gmetad.conf && sudo cp /etc/ganglia/gmond.conf.bak /etc/ganglia/gmond.conf"`
	fi
	backup_ganglia_configure_file=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo cp /etc/httpd/conf.d/ganglia.conf /etc/httpd/conf.d/ganglia.conf.bak && sudo cp /etc/ganglia/gmetad.conf /etc/ganglia/gmetad.conf.bak && sudo cp /etc/ganglia/gmond.conf /etc/ganglia/gmond.conf.bak"`
	echo "Changing configurations in (/etc/httpd/conf.d/ganglia.conf, /etc/ganglia/gmetad.conf, /etc/ganglia/gmond.conf)."
	replace_settings_in_ganglia_dot_conf=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/  Require local/  Require all granted/g' /etc/httpd/conf.d/ganglia.conf"`
	gmeted_replace_str="$master_hostname:8649 "
	for slave_ip in ${slave_ip_array[@]}
	do
		slave_hostname=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "hostname"`
		append_string="$slave_hostname:8649 "
		gmeted_replace_str=$gmeted_replace_str$append_string
	done
	replace_settings_in_gmeted_dot_conf1=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/data_source \"my cluster\" localhost/data_source  \"$cluster_name\" $gmeted_replace_str/g' /etc/ganglia/gmetad.conf"`
	replace_settings_in_gmeted_dot_conf2=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/setuid_username ganglia/setuid_username nobody/g' /etc/ganglia/gmetad.conf"`
	replace_settings_in_gmond_dot_conf1=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/  name = \"unspecified\"/  name = \"$cluster_name\"/g' /etc/ganglia/gmond.conf"`
	replace_settings_in_gmond_dot_conf2=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/  mcast_join = 239.2.11.71/  #mcast_join = 239.2.11.71/g' /etc/ganglia/gmond.conf"`
	replace_settings_in_gmond_dot_conf3=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/  bind = 239.2.11.71/  #bind = 239.2.11.71/g' /etc/ganglia/gmond.conf"`
	replace_settings_in_gmond_dot_conf4=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i 's/  retry_bind = true/  #retry_bind = true/g' /etc/ganglia/gmond.conf"`
	get_master_ip_settings_in_gmond_dot_conf=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo grep -i \"  host = \" /etc/ganglia/gmond.conf"`
	if [ -n $get_master_ip_settings_in_gmond_dot_conf ]
	then
		replace_settings_in_gmond_dot_conf5=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo sed -i '/udp_send_channel {/a\  host = $master_hostname' /etc/ganglia/gmond.conf"`
	fi
	echo "Starting & enabling services (httpd, gmetad, gmond)."
	restart_and_enable_http_service=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo systemctl restart httpd.service && sudo systemctl enable httpd.service"`
	if [[ $? -eq 0 ]];then
		echo -e "Restart service httpd status: \033[42;37m Success \033[0m"
	else
		echo -e "Restart service httpd status: \033[41;37m Failed \033[0m"
	fi
	restart_and_enable_gmetad_service=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo systemctl restart gmetad.service && sudo systemctl enable gmetad.service"`
	if [[ $? -eq 0 ]];then
		echo -e "Restart service gmetad status: \033[42;37m Success \033[0m"
	else
		echo -e "Restart service gmetad status: \033[41;37m Failed \033[0m"
	fi
	restart_and_enable_gmond_service=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$master_ip "sudo systemctl restart gmond.service && sudo systemctl enable gmond.service"`
	if [[ $? -eq 0 ]];then
		echo -e "Restart service gmond status: \033[42;37m Success \033[0m"
	else
		echo -e "Restart service gmond status: \033[41;37m Failed \033[0m"
	fi
	echo "-----------------------------------"
	echo "Now working on Slaves."
	for slave_ip in ${slave_ip_array[@]}
    do
    	if [ ! -n "$1" ];then
	    	scp_rpms=`scp -i $ssh_key -o StrictHostKeyChecking=no -r $ganglia_rpms $user@$slave_ip:~`
			if [[ $? -eq 0 ]];then
				echo -e "Scp rpms to Slave status: \033[42;37m Success \033[0m"
			else
				echo -e "Scp rpms to Slave status: \033[41;37m Failed \033[0m"
				exit 1
			fi
			install_rpms=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo rpm -Uvh --force ~/ganglia-rpms/slave/*.rpm"`
			if [[ $? -eq 0 ]];then
				echo -e "Install rpms on Slave status: \033[42;37m Success \033[0m"
			else
				echo -e "Install rpms on Slave status: \033[41;37m Failed \033[0m"
				exit 1
			fi
		fi
		echo "Backing up configuration files."
		test_backup_files=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo test -f /etc/ganglia/gmond.conf.bak"`
		if [[ $? -eq 0 ]];then
			init_ganglia_configure_file=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo cp /etc/ganglia/gmond.conf.bak /etc/ganglia/gmond.conf"`
		fi
		backup_ganglia_configure_file=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo cp /etc/ganglia/gmond.conf /etc/ganglia/gmond.conf.bak"`
		echo "Changing configurations in (/etc/ganglia/gmond.conf)."
		replace_settings_in_gmond_dot_conf1=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo sed -i 's/  name = \"unspecified\"/  name = \"$cluster_name\"/g' /etc/ganglia/gmond.conf"`
		replace_settings_in_gmond_dot_conf2=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo sed -i 's/  mcast_join = 239.2.11.71/  #mcast_join = 239.2.11.71/g' /etc/ganglia/gmond.conf"`
		replace_settings_in_gmond_dot_conf3=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo sed -i 's/  bind = 239.2.11.71/  #bind = 239.2.11.71/g' /etc/ganglia/gmond.conf"`
		replace_settings_in_gmond_dot_conf4=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo sed -i 's/  retry_bind = true/  #retry_bind = true/g' /etc/ganglia/gmond.conf"`
		get_master_ip_settings_in_gmond_dot_conf=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo grep -i \"  host = \" /etc/ganglia/gmond.conf"`
		if [ -n $get_master_ip_settings_in_gmond_dot_conf ]
		then
			replace_settings_in_gmond_dot_conf5=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo sed -i '/udp_send_channel {/a\  host = $master_hostname' /etc/ganglia/gmond.conf"`
		fi		
		echo "Starting & enabling services (gmond)."
		restart_and_enable_gmond_service=`ssh -i $ssh_key -o StrictHostKeyChecking=no $user@$slave_ip "sudo systemctl restart gmond.service && sudo systemctl enable gmond.service"`
		if [[ $? -eq 0 ]];then
			echo -e "Restart service gmond status: \033[42;37m Success \033[0m"
		else
			echo -e "Restart service gmond status: \033[41;37m Failed \033[0m"
		fi
	done
	echo "All done!"
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
    install-ganglia)
    	install_ganglia
    ;;
    restart-ganglia)
    	install_ganglia "without-install-RPMs"
    ;;
*)
    echo "Usage: bash cluster-yarn.sh {start|stop|restart|reconfigure|install-ganglia|restart-ganglia}"
    exit 1
    ;;
esac
exit 0
