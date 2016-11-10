# 缓存分配工具 cache-allocator
## 简介
缓存分配工具部署在物理机上，用于为特定的磁盘镜像文件分配指定大小的缓存。
缓存类型取决于缓存镜像文件所处的位置。

## 执行环境需求
* 缓存分配工具基于Java语言开发，底层使用到了dm-cache。
* 操作系统需求：Linux，内核版本大于3.10
* 各个内核版本的dm-cache返回的状态信息格式不同，目前基于最新版本进行解析（CentOS 7-1511）

## API
缓存分配工具提供了一组RESTful API。
默认端口为10010。

### 创建缓存
* URL  
POST /Api/Cache/\{name\}  
创建名为name的缓存设备。
* HTTP头中传入参数  
x-ocme-cache-size：缓存大小，以MB为单位  
x-ocme-cache-cache-image-file：缓存镜像文件位置  
x-ocme-cache-disk-image-file：磁盘镜像文件位置
* 返回值  
一个Boolean值，指示操作成功与否。  
* 说明  
这一API执行后会在/dev/mapper目录下生成cached-\{name\}的块设备，可以直接挂载使用或作为虚拟机的磁盘使用。  

### 删除缓存
* URL
DELETE /Api/Cache/\{name\}  
删除名为name的缓存设备。  
* HTTP头中传入参数  
x-ocme-cache-cache-image-file：缓存镜像文件位置  
x-ocme-cache-disk-image-file：磁盘镜像文件位置
* 返回值  
一个Boolean值，指示操作成功与否。  
* 说明  
这一API执行后会将缓存中的数据写回磁盘镜像并安全删除缓存。

### 获取缓存状态
* URL
GET /Api/Cache/\{name\}  
获取名为name的缓存的详细状态。
* 返回值  
一个JSON对象。
    * start
    * end
    * policy
    * metadataBlockSize
    * usedMetadataBlocks
    * totalMetadataBlocks
    * cacheBlockSize
    * usedCacheBlocks
    * totalCacheBlocks
    * readHits
    * readMisses
    * writeHits
    * writeMisses
    * demotions
    * promotions
    * dirty
    * featureList
    * coreArgumentList
    * policyName
    * policyArgumentList
    * cacheMetadataMode

### 说明
* 如果需要创建内存缓存，请将cache-image-file指定为/dev/shm/目录下的文件。类似地，将cache-image-file指定为SSD上的文件即可创建SSD缓存。
* 在删除缓存前需要确保块设备（/dev/mapper/cached-\{name\}）可以被正确umount。
