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
    *  


### 说明
* 执行Hadoop自动部署时需要在每个节点上运行deploy-agent。
