#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2016/05/25

KEYSTONE_USER_NAME = "admin"
KEYSTONE_USER_PASSWORD = "admin"

def get_sahara_cluster_s_masterIP_cmd(project_name, cluster_name):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s server list --name %s -f value | grep master | awk -F\' \' \'{print $(NF)}\'" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, cluster_name)
            
def get_sahara_cluster_s_slavesIP_cmd(project_name, cluster_name):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s server list --name %s -f value | grep worker | awk -F\' \' \'{print $(NF)}\'" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, cluster_name)
            
def get_sahara_worker_node_group_template_name_cmd(project_name, cluster_name):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s dataprocessing cluster show my-cluster-1 -c \"Node groups\" -f value | awk -F\' \' \'{print $(NF)}\' | awk -F\':\' \'{print $1}\'"
            
def write_sahara_cluster_s_slavesIP_to_file_cmd(project_name, cluster_name, work_path):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s server list --name %s -f value | grep worker | awk -F\' \' \'{print $(NF)}\' > %s/slave" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, cluster_name, work_path)
            
def scale_sahara_cluster_cmd(project_name, cluster_name, worker_template_name, size):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s dataprocessing cluster scale %s --instances %s:%s" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, cluster_name, worker_template_name, str(size))
            
def create_sahara_cluster_from_template_cmd(project_name, cluster_name, template_name, key_pair, neutron_private_network, image):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s dataprocessing cluster create --name %s \
            --cluster-template %s --user-keypair %s --neutron-network %s --image %s" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, cluster_name, template_name, key_pair, neutron_private_network, image)
            
def create_sahara_node_group_template_cmd(project_name, node_template_name, node_template_plugin, \
                                 node_template_plugin_version, node_template_processes, \
                                 node_template_flavor, node_template_floating_ip_pool):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s dataprocessing node group template create --name %s \
            --plugin %s --plugin-version %s --processes %s --flavor %s \
            --auto-security-group --autoconfig --floating-ip-pool %s" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, node_template_name, node_template_plugin, \
                                 node_template_plugin_version, node_template_processes, \
                                 str(node_template_flavor), node_template_floating_ip_pool)
            
def create_sahara_cluster_template_cmd(project_name, cluster_template_name, master_node_template_name, \
                              slave_node_template_name, cluster_worker_count):
    return "openstack --os-username %s \
            --os-password %s --os-auth-url http://127.0.0.1:5000/v2.0 \
            --os-project-name %s dataprocessing cluster template create --name %s \
            --autoconfig --node-groups %s:1 %s:%s" \
            %(KEYSTONE_USER_NAME, KEYSTONE_USER_PASSWORD, project_name, cluster_template_name, master_node_template_name, \
              slave_node_template_name, str(cluster_worker_count))