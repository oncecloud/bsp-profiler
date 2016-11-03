#!/bin/bash
set -o nounset
set -o errexit

# SCRIPT: hadoop-install.sh
# AUTHOR: Heng.WU
# DATE: 2016.7.13
# REV: 3.0
# PLATFORM: Linux
# PURPOSE: hadoop install

source /nfs/install/scripts/env.sh
basedir=$(cd "$(dirname "$0")"; pwd)
cd $basedir

# system login user and password
sys_user=$SYS_USER
sys_user_passwd=$SYS_USER_PASSWD

# hadoop version
hadoop_version=$HADOOP_VERSION

# hadoop install dir 
hadoop_install_dir=$SYS_USER_HOME

# hadoop nameNode,nameNodeStandBy,dataNode
hadoop_namenode_host=$HADOOP_NAMENODE_HOST
#hadoop_namenode_standby_host=$HADOOP_NAMENODE_STANDBY_HOST
hadoop_datanode_host=$HADOOP_DATANODE_HOST

# hadoop fs.defaultFS
hadoop_fs_defaultFS=$HADOOP_FS_DEFAULTFS

# hadoop zk connection
# hadoop_zk_connection=$HADOOP_ZK_CONNECTION

# hadoop dfs 
dfs_nameservices=$DFS_NAMESERVICES
dfs_namenode_name_dir=$DFS_NAMENODE_NAME_DIR
dfs_datanode_data_dir=$DFS_DATANODE_DATA_DIR

# hadoop jobhistory
mapred_jobhistory_address=$MAPRED_JOBHISTORY_ADDRESS
mapred_jobhistory_webapp_address=$MAPRED_JOBHISTORY_WEBAPP_ADDRESS

# hadoop reourcemanager
yarn_resourcemanager_hostname=$YARN_RESOURCEMANAGER_HOSTNAME

dfs_replication=$DFS_REPLICATION
dfs_blocksize=$DFS_BLOCKSIZE

test -f $SOFTS_DIR/hadoop-$hadoop_version.tar.gz || (echo "hadoop-$hadoop_version.tar.gz file not found" ; exit 1)
test $? -eq 1 && exit 1

tar -zxf $SOFTS_DIR/hadoop-$hadoop_version.tar.gz

# 增加hadoop datanode 主机到slaves
sed -i '1d' ./hadoop-$hadoop_version/etc/hadoop/slaves
for datanode in ${hadoop_datanode_host//,/ }
do
  echo $datanode >> ./hadoop-$hadoop_version/etc/hadoop/slaves
done

# core-site.xml
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>$hadoop_fs_defaultFS</value>
  </property>
  <property>
    <name>ha.zookeeper.quorum</name>
    <value>$hadoop_zk_connection</value>
  </property>
</configuration>" > ./hadoop-$hadoop_version/etc/hadoop/core-site.xml

# hdfs-site.xml
ha_namenodes=nn1
ha_address_nn2=
if [[ -n $hadoop_namenode_standby_host ]]
then
  ha_namenodes=$ha_namenodes,nn2
  ha_address_nn2="<property>
    <name>dfs.namenode.rpc-address.$dfs_nameservices.nn2</name>
    <value>$hadoop_namenode_standby_host:8020</value>
  </property>
  <property>
    <name>dfs.namenode.http-address.$dfs_nameservices.nn2</name>
    <value>$hadoop_namenode_standby_host:50070</value>
  </property>"
fi

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>
<configuration>
  <property>
    <name>dfs.nameservices</name>
    <value>$dfs_nameservices</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>$dfs_namenode_name_dir</value>
  </property>
  <property>
    <name>dfs.ha.namenodes.$dfs_nameservices</name>
    <value>$ha_namenodes</value>
  </property>
  <property>
    <name>dfs.namenode.rpc-address.$dfs_nameservices.nn1</name>
    <value>$hadoop_namenode_host:8020</value>
  </property>
  <property>
    <name>dfs.namenode.http-address.$dfs_nameservices.nn1</name>
    <value>$hadoop_namenode_host:50070</value>
  </property>
  $ha_address_nn2
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>$dfs_datanode_data_dir</value>
  </property>
  <property>
    <name>dfs.replication</name>
    <value>$dfs_replication</value>
  </property>
  <property>
    <name>dfs.blocksize</name>
    <value>$dfs_blocksize</value>
  </property>
</configuration>" > ./hadoop-$hadoop_version/etc/hadoop/hdfs-site.xml

# mapred-site.xml
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
  <property>
    <name>mapreduce.jobhistory.address</name>
    <value>$mapred_jobhistory_address</value>
  </property>
  <property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>$mapred_jobhistory_webapp_address</value>
  </property>
  <property>
    <name>yarn.app.mapreduce.am.staging-dir</name>
    <value>/jobhistory</value>
  </property>
  <property>
    <name>mapreduce.jobhistory.intermediate-done-dir</name>
    <value>\${yarn.app.mapreduce.am.staging-dir}/done_intermediate</value>
  </property>
  <property>
    <name>mapreduce.jobhistory.done-dir</name>
    <value>\${yarn.app.mapreduce.am.staging-dir}/done</value>
  </property>
</configuration>" > ./hadoop-$hadoop_version/etc/hadoop/mapred-site.xml

# yarn-site.xml
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>
<configuration>
  <property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>$yarn_resourcemanager_hostname</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.log-aggregation.retain-seconds</name>
    <value>604800</value>
  </property>
</configuration>" > ./hadoop-$hadoop_version/etc/hadoop/yarn-site.xml

function scp_hadoop() {
  target_host=$1
  echo $target_host
  scp -r ./hadoop-$hadoop_version $sys_user@$target_host:$hadoop_install_dir > /dev/null
  ssh $sys_user@$target_host "mkdir -p $dfs_datanode_data_dir"
  ssh $sys_user@$target_host "mkdir -p $dfs_namenode_name_dir"
}

function install_hadoop() {

  scp_hadoop $hadoop_namenode_host
  awk 'BEGIN{printf "%-20s \033[32m%-20s\033[0m\n","'$hadoop_namenode_host'", "安装成功"}'

  if [[ -n $hadoop_namenode_standby_host ]]
  then
    scp_hadoop $hadoop_namenode_standby_host
    awk 'BEGIN{printf "%-20s \033[32m%-20s\033[0m\n","'$hadoop_namenode_standby_host'", "安装成功"}'
  fi
  # 分发包到各台slaves主机
  for datanode in ${hadoop_datanode_host//,/ } 
  do
    scp_hadoop $datanode
    awk 'BEGIN{printf "%-20s \033[32m%-20s\033[0m\n","'$datanode'", "安装成功"}'
  done
}

install_hadoop
rm -rf ./hadoop-$hadoop_version
