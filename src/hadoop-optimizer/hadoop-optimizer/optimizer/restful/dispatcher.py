#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/01/06

from optimizer import restful_api
from optimizer.restful.drivers.hadoop import *

restful_api.add_resource(Prepare, '/v1.0/sahara-cluster/<string:cluster_name>/masterIP/json')
restful_api.add_resource(Deploy, '/v1.0/sahara-cluster/<string:cluster_name>/starfish/deploy')
restful_api.add_resource(Setup, '/v1.0/sahara-cluster/<string:cluster_name>/benchmark/setup')
restful_api.add_resource(Distribute, '/v1.0/sahara-cluster/<string:cluster_name>/btrace/distribute')
restful_api.add_resource(Analysis, '/v1.0/sahara-cluster/<string:cluster_name>/rumen/analysis')
restful_api.add_resource(Reconfigure, '/v1.0/sahara-cluster/<string:cluster_name>/yarn/reconfigure')
restful_api.add_resource(Scale, '/v1.0/sahara-cluster/<string:cluster_name>/scale')
restful_api.add_resource(CreateCluster, '/v1.0/sahara-cluster/create')
restful_api.add_resource(Submit, '/v1.0/sahara-cluster/<string:cluster_name>/job/submit')