# Hadoop部署工具 deploy-host
## 简介
Hadoop部署工具用于协调各节点上的deploy-agent完成Hadoop集群的配置。

## 执行环境需求
* deploy-host基于Java语言开发。

## API
Hadoop部署工具提供了RESTful API。
默认端口为10011。

### 配置Hadoop集群
* URL  
POST /Api/Deploy/Hadoop  
配置Hadoop集群。
* HTTP头中传入参数  
x-ocme-hadoop-location：Hadoop实例位置  
x-ocme-hadoop-master-ip：HDFS NameNode以及YARN ResourceManager的IP地址  
x-ocme-hadoop-slave-ips：HDFS DataNode以及YARN NodeManager的IP地址列表，以空格分隔
* 返回值  
一个Boolean值，指示操作成功与否。  
* 说明  
这一API会完成Hadoop集群的基本配置。
默认应用如下参数：
    * \{location\}/etc/hadoop/core-site.xml
        * fs.defaultFS = hdfs://\{master-ip\}:9000
        * hadoop.tmp.dir = file:\{location\}/tmp
        * io.file.buffer.size = 131072
    *  \{location\}/etc/hadoop/hdfs-site.xml
        * dfs.namenode.name.dir = file:\{location\}/hdfs/name
        * dfs.datanode.data.dir = file:\{location\}/hdfs/data
        * dfs.replication = 2
        * dfs.namenode.secondary.http-address = \{master-ip\}:9001
        * dfs.webhdfs.enabled = true
    * \{location\}/etc/hadoop/mapred-site.xml
        * mapreduce.framework.name = yarn
        * mapreduce.jobhistory.address = \{master-ip\}:10020
        * mapreduce.jobhistory.webapp.address = \{master-ip\}:19888
    * \{location\}/etc/hadoop/yarn-site.xml
        * yarn.nodemanager.aux-services = mapreduce_shuffle
        * yarn.nodemanager.auxservices.mapreduce.shuffle.class = org.apache.hadoop.mapred.ShuffleHandler
        * yarn.resourcemanager.address = \{master-ip\}:8032
        * yarn.resourcemanager.scheduler.address = \{master-ip\}:8030
        * yarn.resourcemanager.resource-tracker.address = \{master-ip\}:8031
        * yarn.resourcemanager.admin.address = \{master-ip\}:8033
        * yarn.resourcemanager.webapp.address = \{master-ip\}:8088

### 说明
* 执行Hadoop自动部署时需要在每个节点上运行deploy-agent。
* 需要在虚拟机模板中完成如下操作：
    * 虚拟机内存至少为2GB，以支持YARN计算节点运行
    * 配置SSH免密码登录
    * 配置SSH Known Host
    * 配置IP地址
    * 安装JDK
    * 解压Hadoop安装包，tmp，hdfs/name，hdfs/data文件夹
    * 设置hadoop-env.sh和yarn-env.sh中的Java Home
