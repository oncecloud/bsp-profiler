#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2016/05/25


def get_sahara_cluster_s_masterIP_cmd(project_name, cluster_name):
    return "openstack --os-username admin  \
            --os-password admin --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s server list --name %s -f value | grep master | awk -F\' \' \'{print $(NF)}\'" \
            %(project_name, cluster_name)
            
def get_sahara_cluster_s_slavesIP_cmd(project_name, cluster_name):
    return "openstack --os-username admin  \
            --os-password admin --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s server list --name %s -f value | grep worker | awk -F\' \' \'{print $(NF)}\'" \
            %(project_name, cluster_name)
            
def write_sahara_cluster_s_slavesIP_to_file_cmd(project_name, cluster_name, work_path):
    return "openstack --os-username admin  \
            --os-password admin --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s server list --name %s -f value | grep worker | awk -F\' \' \'{print $(NF)}\' > %s/slave" \
            %(project_name, cluster_name, work_path)