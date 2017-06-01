# Name: Hadoop Optimizer
A project analysis MapReduce v2 Jobs and recommends cluster configuration, now supports Openstack(Mitaka) Sahara cluster. Written in Python2. Providing a RESTful API for end users.

**Copyright: Institute of Software, Chinese Academy of Sciences**

**Authors: wuyuewen@otcaix.iscas.ac.cn, wuheng09@otcaix.iscas.ac.cn**

## Preparation

- A Openstack Mitaka system.
- A Openstack Sahara cluster with Vanilla-2.7.1 plugin.
- A python2 running environment with flask-restful module.

## Installation

**Step 1:** Clone this project in github.

**Step 2:** Execute installation script.
- cd hadoop-optimizer
- bash install.sh

**Step 3:** Run service automatically on startup, check status using command below.
- lenovo-hadoop-optimizer status

## Commandlines

**Start service:**
- lenovo-hadoop-optimizer start

**Stop service:**
- lenovo-hadoop-optimizer stop

**Restart service:**
- lenovo-hadoop-optimizer restart

**Get service status:**
- lenovo-hadoop-optimizer status

## RESTful APIs
### Create Sahara cluster template

```POST /v1.0/sahara-cluster/template/create```

Create Sahara cluster template.

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
POST http://<ip>:8848/v1.0/sahara-cluster/template/create HTTP/1.1
Content-Type: application/json
{
  "masterNodeTemplateName": "master-8G8U-40",
  "masterNodeTemplatePlugin": "vanilla",
  "masterNodeTemplatePluginVersion": "2.7.1",
  "masterNodeTemplateProcesses": "namenode resourcemanager historyserver oozie",
  "masterNodeTemplateFlavor": 86,
  "masterNodeTemplateFloatingIpPool": "95f72657-c25c-499b-96ce-0106d162365d",
  "workerNodeTemplateName": "worker-8G8U-40",
  "workerNodeTemplatePlugin": "vanilla",
  "workerNodeTemplatePluginVersion": "2.7.1",
  "workerNodeTemplateProcesses": "datanode nodemanager",
  "workerNodeTemplateFlavor": 86,
  "workerNodeTemplateFloatingIpPool": "95f72657-c25c-499b-96ce-0106d162365d",
  "clusterTemplateName": "cluster-8G8U-40G-3",
  "clusterWorkerCount": 3
}
```

**Example response:**

```
HTTP/1.1 200
```
### Create Sahara cluster

```POST /v1.0/sahara-cluster/create```

Create Sahara cluster from template.

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
POST http://<ip>:8848/v1.0/sahara-cluster/create HTTP/1.1
Content-Type: application/json
{
  "clusterName": "pin-test",
  "template": "cluster-20G20U-pin",
  "keyPair": "hadoop_cluster_1",
  "privateNetwork": "share_net",
  "image": "sahara-vanilla-latest-centos7"
}
```

**Example response:**

```
HTTP/1.1 200
```
### Get master IP

```GET /v1.0/sahara-cluster/<string:cluster_name>/masterIP/json```

Get master IP of specific Sahara cluster.

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
GET http://<ip>:8848/v1.0/sahara-cluster/my-cluster-1/masterIP/json HTTP/1.1
```

**Example response:**

```
HTTP/1.1 200 "{'masterIP': '10.100.217.36'}"
```
### Submit job

```POST /v1.0/sahara-cluster/<string:cluster_name>/job/submit```

Submit job to Sahara master.

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
POST http://<ip>:8848/v1.0/sahara-cluster/<string:cluster_name>/job/submit HTTP/1.1
Content-Type: application/json
{
  "sshKeyPath": "/root/test.key",
  "jarDir": "/root/jars",
  "jarName": "hadoop-mapreduce-client-jobclient-2.7.1-tests.jar",
  "jarClass": "TestDFSIO",
  "jarParams": "-write -nrFiles 10 -fileSize 10GB"
}
```

**Example response:**

```
HTTP/1.1 200
```
### Analysis job history

```POST /v1.0/sahara-cluster/<string:cluster_name>/rumen/analysis```

Analysis job history log.

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
POST http://<ip>:8848/v1.0/sahara-cluster/<string:cluster_name>/rumen/analysis HTTP/1.1
Content-Type: application/json
{
  "workDir": "/home/optimizer",
  "jobID": "job_1492744792305_0018",
  "scriptName": "analysis.sh",
  "sshKeyPath": "/root/test.key",
  "computeNodeMaxCpuCore": 20,
  "computeNodeMaxMemoryGb": 20
}
```

**Example response:**

```
HTTP/1.1 200
```
### Live scale out Sahara cluster

```POST /v1.0/sahara-cluster/<string:cluster_name>/scale```

Live scale out Sahara cluster.

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
POST http://<ip>:8848/v1.0/sahara-cluster/<string:cluster_name>/scale HTTP/1.1
Content-Type: application/json
{
  "workerTemplateName": "worker-20G20U",
  "size": 7
}
```

**Example response:**

```
HTTP/1.1 200
```

### Scale up Sahara cluster

```POST /v1.0/sahara-cluster/<string:cluster_name>/yarn/reconfigure```

Scale up Sahara cluster. *Note*: Please resize Virtual Machine first!

**Status Codes:**

- 200 - no error
- 400 - bad request
- 500 - server error

**Example request:**
```
POST http://<ip>:8848/v1.0/sahara-cluster/<string:cluster_name>/yarn/reconfigure HTTP/1.1
Content-Type: application/json
{
  "sshKeyPath": "/root/test.key",
  "restartNodeManager": true,
  "restartDataNode": true,
  "restartNameNode": true,
  "restartHistoryServer": true,
  "vcpuNum": 14,
  "memMB" : 14336
}
```

**Example response:**

```
HTTP/1.1 200
```