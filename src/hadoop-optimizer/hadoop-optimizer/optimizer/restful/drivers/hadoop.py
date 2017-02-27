#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2016/05/25

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import traceback
import json
from json import JSONDecoder

from flask_restful.representations.json import output_json
from flask import request
from flask_restful import Resource, abort

from optimizer.restful.types import *
from optimizer.restful.openstack_cmd import *
from optimizer.utils import shell
from optimizer import app

log = app.logger

__all__ = [
        "Prepare",
        "Deploy",
        "Setup",
        "Distribute",
        "Reconfigure",
           ]
            
class Prepare(Resource):
    
    def get(self, cluster_name):
        try:
            retv = {}
            work_path = "/home/optimizer/%s" % cluster_name
            if not os.path.exists(work_path):
                os.makedirs(work_path)
            project_name = request.args.get('project', "admin")
            output = shell.call(get_sahara_cluster_s_masterIP_cmd(project_name, cluster_name)).strip()
            retv['masterIP'] = output
            shell.call(write_sahara_cluster_s_slavesIP_to_file_cmd(project_name, cluster_name, work_path)).strip()
            return output_json("%s" % retv, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            
class Deploy(Resource):
    
    def __init__(self):
        self.scriptName = "deploy.sh"
    
    def post(self, cluster_name):
        try:
            ip_file = "/home/optimizer/%s/slave" % cluster_name
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            workDir = dict_data.get('workDir')
            scriptName = dict_data.get('scriptName', self.scriptName)
            sshKeyPath = dict_data.get('sshKeyPath')
            masterIP = dict_data.get('masterIP')
            if not workDir or not sshKeyPath or not masterIP:
                abort(400, message="bad parameter in request body")
            output = shell.call("/usr/bin/bash %s/%s %s %s %s &" \
                                 %(workDir, scriptName, ip_file, sshKeyPath, masterIP), \
                                workdir=workDir)
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            
class Setup(Resource):
    
    def __init__(self):
        self.scriptName = "benchmark.sh"
    
    def post(self, cluster_name):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            workDir = dict_data.get('workDir')
            scriptName = dict_data.get('scriptName', self.scriptName)
            sshKeyPath = dict_data.get('sshKeyPath')
            masterIP = dict_data.get('masterIP')
            if not workDir or not sshKeyPath or not masterIP:
                abort(400, message="bad parameter in request body")
            output = shell.call("ssh -i %s centos@%s \"cd %s; /usr/bin/bash %s\"" \
                                %(sshKeyPath, masterIP, workDir, scriptName))
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            
class Distribute(Resource):
    
    def __init__(self):
        self.scriptName = "install_btrace.sh"
    
    def post(self, cluster_name):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            workDir = dict_data.get('workDir')
            scriptName = dict_data.get('scriptName', self.scriptName)
            sshKeyPath = dict_data.get('sshKeyPath')
            masterIP = dict_data.get('masterIP')
            if not workDir or not sshKeyPath or not masterIP:
                abort(400, message="bad parameter in request body")
            output = shell.call("ssh -i %s centos@%s \"cd %s; /usr/bin/bash %s slave\"" \
                                %(sshKeyPath, masterIP, workDir, scriptName))
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")

class Reconfigure(Resource):
    
    def __init__(self):
        self.scriptName = "cluster_yarn.sh"
    
    def post(self, cluster_name):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            masterIP = dict_data.get('masterIP')
            sshKeyPath = dict_data.get('sshKeyPath')
            vcpuNum = dict_data.get('vcpuNum')
            memMB = dict_data.get('memMB')
            if not masterIP or not sshKeyPath or not vcpuNum or not memMB:
                abort(400, message="bad parameter in request body")
            else:
                project_name = request.args.get('project', "admin")
                slaveIPArray = shell.call(get_sahara_cluster_s_slavesIP_cmd(project_name, cluster_name)).strip()
                slaveIPArrayStr = str(slaveIPArray).replace("\n", " ")
                script_setting_str = "master_ip=%s\nslave_ip_array=(%s)\nuser=centos\nssh_key=\\\"%s\\\"\nyarn_vcpu_new_value=\\\"<value>%s<\/value>\\\"\nyarn_mem_new_value=\\\"<value>%s<\/value>\\\"" \
                                    % (masterIP, slaveIPArrayStr, sshKeyPath, str(vcpuNum), str(memMB))
                work_path = "/home/optimizer/%s" % cluster_name
                if not os.path.exists(work_path):
                    os.makedirs(work_path)
                shell.call("echo \"%s\" > %s/cluster_yarn.conf" % (script_setting_str, work_path))
                shell.call("/usr/bin/cp -f /home/optimizer/scripts/cluster_yarn.sh %s" % (work_path))
                output = shell.call("/usr/bin/bash cluster_yarn.sh reconfigure", workdir=work_path)
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            