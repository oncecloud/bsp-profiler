# Hadoop部署Agent deploy-agent
## 简介
Agent部署在每台虚拟机上，用于执行基本的维护任务。

## 执行环境需求
* Agent基于Java语言开发。
* 部分API使用到了Linux Shell。

## API
缓存分配工具提供了一组RESTful API。
默认端口为10012。

### 执行命令
* URL  
POST /Api/Agent/Run  
执行指定命令。
* HTTP头中传入参数  
x-ocme-agent-command：要执行的命令  
* 返回值  
一个JSON对象，指示命令的执行结果。  
    * exitValue：返回值
    * standardOutput：标准输出流的数据
    * standError：标准错误流的数据
* 说明  
这一API会调用Linux Shell执行指定命令。  

### 上传文本文件
* URL
POST /Api/Agent/Upload  
在指定位置创建指定内容的文本文件。  
* HTTP请求体格式  
一个JSON对象，代表文件的位置和内容。  
    * location：文件位置
    * content：文件内容
* 返回值  
一个Boolean值，指示操作成功与否。  
* 说明  
这一API执行后会在指定位置写入文件，已存在的文件会被覆盖。

### 说明
* 执行Hadoop自动部署时需要在每个节点上运行deploy-agent。
