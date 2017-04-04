#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/03/16

def find_jhist_file_in_hdfs_cmd(jobID):
    return "hadoop fs -find / -name %s*.jhist | grep jhist" % jobID

def analysis_job_with_hadoop_rumen_cmd(cluster_name, jobID, jhistPath):
    return "hadoop jar \$HADOOP_COMMON_HOME/share/hadoop/tools/lib/hadoop-rumen-*.jar \
            org.apache.hadoop.tools.rumen.TraceBuilder file:///home/hadoop/%s/%s-trace.json \
            file:///home/hadoop/%s/%s-topology.json hdfs://%s" \
            %(cluster_name, jobID, cluster_name, jobID, jhistPath)
            
def submit_job_on_hadoop_cmd(jar_name, jar_class, jar_params):
    return "nohup hadoop jar /home/hadoop/jars/%s %s %s >/dev/null 2>&1 &" \
            %(jar_name, jar_class, jar_params)