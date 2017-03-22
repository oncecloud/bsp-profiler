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
from optimizer.restful.hadoop_cmd import *
from optimizer.utils import shell
from optimizer.utils.hadoop2_job_stats import Hadoop2JobStats
from optimizer import app

log = app.logger

__all__ = [
        "Prepare",
        "Deploy",
        "Setup",
        "Distribute",
        "Analysis",
        "Reconfigure",
        "Scale",
        "CreateCluster",
        "Submit",
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
        self.sourceDir = "/home/sf"
    
    def post(self, cluster_name):
        try:
            ip_file = "/home/optimizer/%s/slave" % cluster_name
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            sourceDir = dict_data.get('sourceDir', self.sourceDir)
            scriptName = dict_data.get('scriptName', self.scriptName)
            sshKeyPath = dict_data.get('sshKeyPath')
            masterIP = dict_data.get('masterIP')
            if not sshKeyPath or not masterIP:
                abort(400, message="bad parameter in request body")
            output = shell.call("/usr/bin/bash %s/%s %s %s %s &" \
                                 %(sourceDir, scriptName, ip_file, sshKeyPath, masterIP), \
                                workdir=sourceDir)
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            
class Setup(Resource):
    
    def __init__(self):
        self.scriptName = "benchmark.sh"
        self.sourceDir = "/home/sf"
    
    def post(self, cluster_name):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            workDir = dict_data.get('workDir')
            sourceDir = dict_data.get('sourceDir', self.sourceDir)
            scriptName = dict_data.get('scriptName', self.scriptName)
            scriptPath = os.path.join(sourceDir, scriptName)
            sshKeyPath = dict_data.get('sshKeyPath')
            masterIP = dict_data.get('masterIP')
            if not workDir or not sshKeyPath or not masterIP:
                abort(400, message="bad parameter in request body")
            shell.call("scp -i %s %s centos@%s:/home/centos" %(sshKeyPath, scriptPath, masterIP))
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
            
class Analysis(Resource):
    
    def __init__(self):
        self.scriptName = "analysis.py"
        
    def _analysis_jhist_json(self, jhist_json_path):
        jhist_dict_data = json.load(file(jhist_json_path))
        key_stats_dict = Hadoop2JobStats(jhist_dict_data).to_dict()
        return key_stats_dict
    
    def post(self, cluster_name):
        try:
            work_path = "/home/optimizer/%s" % cluster_name
            if not os.path.exists(work_path):
                os.makedirs(work_path)
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            jobID = dict_data.get('jobID')
            workDir = dict_data.get('workDir')
            scriptName = dict_data.get('scriptName', self.scriptName)
            sshKeyPath = dict_data.get('sshKeyPath')
            masterIP = dict_data.get('masterIP')
            if not workDir or not sshKeyPath or not masterIP or not jobID:
                abort(400, message="bad parameter in request body")
                
            jhist_json_path = "%s/%s-trace.json" % (work_path, jobID)
            jhist_path = shell.call("ssh -i %s centos@%s \"sudo su - -c \'%s\' hadoop\"" \
                                    %(sshKeyPath, masterIP, find_jhist_file_in_hdfs_cmd(jobID))).strip()
            shell.call("ssh -i %s centos@%s \"sudo su - -c \'%s\' hadoop\"" \
                        %(sshKeyPath, masterIP, analysis_job_with_hadoop_rumen_cmd(cluster_name, jobID, jhist_path)))
            shell.call("ssh -i %s centos@%s \"sudo su - -c \'cat /home/hadoop/%s/%s-trace.json\' hadoop\" > %s" \
                       % (sshKeyPath, masterIP, cluster_name, jobID, jhist_json_path))
            output = self._analysis_jhist_json(jhist_json_path)
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
            
class Scale(Resource):

    def __init__(self):
        self.scriptName = ""

    def post(self, cluster_name):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            project_name = request.args.get('project', "admin")
            size = dict_data.get('size')
            if not size:
                abort(400, message="bad parameter in request body")
            output = shell.call(scale_sahara_cluster_cmd(project_name, cluster_name, size)).strip()
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            
class CreateCluster(Resource):

    def __init__(self):
        self.scriptName = ""

    def post(self):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            project_name = request.args.get('project', "admin")
            cluster_name = dict_data.get('clusterName')
            template_name = dict_data.get('template')
            key_pair = dict_data.get('keyPair')
            neutron_private_network = dict_data.get('privateNetwork')
            image = dict_data.get('image')
            if not project_name or not cluster_name or not template_name or not key_pair or not neutron_private_network or not image:
                abort(400, message="bad parameter in request body")
            output = shell.call(create_sahara_cluster_from_template_cmd(project_name, cluster_name, template_name, \
                                                                        key_pair, neutron_private_network, image)).strip()
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            
class Submit(Resource):

    def __init__(self):
        self.scriptName = ""

    def post(self, cluster_name):
        try:
            json_data = request.get_json(force=True)
            json_str = json.dumps(json_data)
            dict_data = JSONDecoder().decode(json_str)
            project_name = request.args.get('project', "admin")
            masterIP = dict_data.get('masterIP')
            sshKeyPath = dict_data.get('sshKeyPath')
            jar_dir = dict_data.get('jarDir')
            jar_name = dict_data.get('jarName')
            jar_class = dict_data.get('jarClass')
            jar_params = dict_data.get('jarParams')
            if not masterIP or not sshKeyPath or not jar_dir or not jar_name or not jar_class or not jar_params:
                abort(400, message="bad parameter in request body")
            shell.call("scp -i %s -r %s centos@%s:/home/centos" %(sshKeyPath, jar_dir, masterIP))
            shell.call("sudo su - -c \"cp -R /home/centos/%s /home/hadoop \&\& \
            mv /home/hadoop/%s /home/hadoop/jars \&\& chown -R hadoop:hadoop /home/hadoop/jars\"" % (jar_dir, jar_dir))
            output = shell.call("ssh -i %s centos@%s \"sudo su - -c \'%s\' hadoop\"" \
                                    %(sshKeyPath, masterIP, submit_job_on_hadoop_cmd(jar_name, jar_class, jar_params))).strip()
            return output_json(output, 200)
        except Exception:
            log.exception(traceback.format_exc())
            abort(400, message="Request failed")
            