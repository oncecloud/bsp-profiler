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
### Get master IP

```GET /v1.0/sahara-cluster/<string:cluster_name>/masterIP/json```

Get master IP of specific Sahara cluster.

**Status Codes:**

- 204 - no error
- 304 - domain already stopped
- 404 - no such domain
- 500 - server error

**Example request:**
```
POST /v1.0/sahara-cluster/my-cluster-1/masterIP/json HTTP/1.1
```

**Example response:**

```
HTTP/1.1 200 "{'masterIP': '10.100.217.36'}"
```
