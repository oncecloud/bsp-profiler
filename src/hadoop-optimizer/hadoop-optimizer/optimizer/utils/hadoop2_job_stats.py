#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/03/17

import json
import pprint

RUN_WITHOUT_LOGGING = False
log = None

try:
    from optimizer import app
    log = app.logger
except:
    RUN_WITHOUT_LOGGING = True


class Hadoop2JobStats(object):

    def __init__(self, jhist_dict_data):
        self.__jobID = jhist_dict_data.get('jobID', None)
        self.__submitTime = jhist_dict_data.get('submitTime', 0)
        self.__launchTime = jhist_dict_data.get('launchTime', 0)
        self.__finishTime = jhist_dict_data.get('finishTime', 0)
        self.__totalMaps = jhist_dict_data.get('totalMaps', 0)
        self.__totalReduce = jhist_dict_data.get('totalReduces', 0)
        self.__result = jhist_dict_data.get('outcome', None)
        self.__jobType = jhist_dict_data.get('jobtype', None)
        self.__mapTasks = self._map_tasks_stats_filter(jhist_dict_data.get('mapTasks', []))
        self.__reduceTasks = self._reduce_tasks_stats_filter(jhist_dict_data.get('reduceTasks', []))
        self.__successfulMapAttemptCDFs = self._successful_map_attempt_CDFs_filter(jhist_dict_data.get("successfulMapAttemptCDFs", []))
        self.__failedMapAttemptCDFs = self._failed_map_attempt_CDFs_filter(jhist_dict_data.get("failedMapAttemptCDFs", []))
        self.__successfulReduceAttemptCDF = self._successful_reduce_attempt_CDF_filter(jhist_dict_data.get("successfulReduceAttemptCDF", []))
        self.__failedReduceAttemptCDF = self._failed_reduce_attempt_CDF_filter(jhist_dict_data.get("failedReduceAttemptCDF", []))
        self.__mapper_tries_to_succeed = jhist_dict_data.get("mapperTriesToSucceed", [])

    def to_dict(self):
        retv = {
            "jobID" : self.get_job_id(),
            "submitTime" : self.get_submit_time(),
            "launchTime" : self.get_launch_time(),
            "finishTime" : self.get_finish_time(),
            "totalMaps" : self.get_total_maps(),
            "totalReduces" : self.get_total_reduce(),
            "result" : self.get_result(),
            "jobType" : self.get_job_type(),
            "mapTasks" : self.get_map_tasks(),
            "reduceTasks" : self.get_reduce_tasks(),
            "successfulMapAttemptCDFs" : self.get_successful_map_attempt_cdfs(),
            "successfulReduceAttemptCDF" : self.get_successful_reduce_attempt_cdf(),
            "failedMapAttemptCDFs" : self.get_failed_map_attempt_cdfs(),
            "failedReduceAttemptCDF" : self.get_failed_reduce_attempt_cdf()
            }
        if not RUN_WITHOUT_LOGGING:
            log.debug(pprint.pprint(retv))
        return retv
    
    def _successful_map_attempt_CDFs_filter(self, jhist_successful_map_attempt_CDFs):
        useful_map_attempt_CDFs = []
        key_stats = ["numberValues", "minimum", "maximum", "rankings"]
        if jhist_successful_map_attempt_CDFs:
            for jhist_successful_map_attempt_CDF in jhist_successful_map_attempt_CDFs:
                numberValues = jhist_successful_map_attempt_CDF.get('numberValues', 0)
                if int(numberValues) >= 1:
                    key_stats_dict = {}
                    for k in key_stats:
                        key_stats_dict[k] = jhist_successful_map_attempt_CDF.get(k)
                    useful_map_attempt_CDFs.append(key_stats_dict)
                else:
                    continue
        return useful_map_attempt_CDFs
    
    def _failed_map_attempt_CDFs_filter(self, jhist_failed_map_attempt_CDFs):
        useful_map_attempt_CDFs = []
        key_stats = ["numberValues", "minimum", "maximum", "rankings"]
        if jhist_failed_map_attempt_CDFs:
            for jhist_failed_map_attempt_CDF in jhist_failed_map_attempt_CDFs:
                numberValues = jhist_failed_map_attempt_CDF.get('numberValues', 0)
                if int(numberValues) >= 1:
                    key_stats_dict = {}
                    for k in key_stats:
                        key_stats_dict[k] = jhist_failed_map_attempt_CDF.get(k)
                    useful_map_attempt_CDFs.append(key_stats_dict)
                else:
                    continue
        return useful_map_attempt_CDFs
    
    def _successful_reduce_attempt_CDF_filter(self, jhist_successful_reduce_attempt_CDF):
        useful_reduce_attempt_CDF = {}
        key_stats = ["numberValues", "minimum", "maximum", "rankings"]
        if jhist_successful_reduce_attempt_CDF:
            numberValues = jhist_successful_reduce_attempt_CDF.get('numberValues', 0)
            if int(numberValues) >= 1:
                for k in key_stats:
                    useful_reduce_attempt_CDF[k] = jhist_successful_reduce_attempt_CDF.get(k)
        return useful_reduce_attempt_CDF
    
    def _failed_reduce_attempt_CDF_filter(self, jhist_failed_reduce_attempt_CDF):
        useful_reduce_attempt_CDF = {}
        key_stats = ["numberValues", "minimum", "maximum", "rankings"]
        if jhist_failed_reduce_attempt_CDF:
            numberValues = jhist_failed_reduce_attempt_CDF.get('numberValues', 0)
            if int(numberValues) >= 1:
                for k in key_stats:
                    useful_reduce_attempt_CDF[k] = jhist_failed_reduce_attempt_CDF.get(k)
        return useful_reduce_attempt_CDF
    
    def _map_tasks_stats_filter(self, jhist_map_tasks_stats):
        map_tasks_key_stats = []
        key_stats = ["inputBytes", "outputBytes", "startTime", "finishTime", "taskStatus", "taskID"]
        key_stats_in_attempts = ["attemptID", "startTime", "finishTime", "hostName", "resourceUsageMetrics", "result", "mapOutputRecords", "reduceOutputRecords", "spilledRecords"]
        if jhist_map_tasks_stats:
            for map in jhist_map_tasks_stats:
                map_stats_dict = {}
                attempts_list = map.get('attempts')
                for k in key_stats:
                    map_stats_dict[k] = map.get(k)
                attempts_list_tmp = []
                for attempts_sub_dict in attempts_list:
                    attempts_stats_dict = {}
                    for k in key_stats_in_attempts:
                        attempts_stats_dict[k] = attempts_sub_dict.get(k)
                    attempts_list_tmp.append(attempts_stats_dict)
                map_stats_dict['attempts'] = attempts_list_tmp
                map_tasks_key_stats.append(map_stats_dict)
        return map_tasks_key_stats
    
    def _reduce_tasks_stats_filter(self, jhist_reduce_tasks_stats):
        reduce_tasks_key_stats = []
        key_stats = ["inputBytes", "outputBytes", "startTime", "finishTime", "taskStatus", "taskID"]
        key_stats_in_attempts = ["attemptID", "startTime", "finishTime", "hostName", "resourceUsageMetrics", "result"]
        if jhist_reduce_tasks_stats:
            for reduce in jhist_reduce_tasks_stats:
                reduce_stats_dict = {}
                attempts_list = reduce.get('attempts')
                for k in key_stats:
                    reduce_stats_dict[k] = reduce.get(k)
                attempts_list_tmp = []
                for attempts_sub_dict in attempts_list:
                    attempts_stats_dict = {}
                    for k in key_stats_in_attempts:
                        attempts_stats_dict[k] = attempts_sub_dict.get(k)
                    attempts_list_tmp.append(attempts_stats_dict)
                reduce_stats_dict['attempts'] = attempts_list_tmp
                reduce_tasks_key_stats.append(reduce_stats_dict)
        return reduce_tasks_key_stats

    def get_job_id(self):
        return self.__jobID


    def get_submit_time(self):
        return self.__submitTime


    def get_launch_time(self):
        return self.__launchTime


    def get_finish_time(self):
        return self.__finishTime


    def get_total_maps(self):
        return self.__totalMaps


    def get_total_reduce(self):
        return self.__totalReduce


    def get_result(self):
        return self.__result


    def get_job_type(self):
        return self.__jobType


    def get_map_tasks(self):
        return self.__mapTasks


    def get_reduce_tasks(self):
        return self.__reduceTasks


    def get_successful_map_attempt_cdfs(self):
        return self.__successfulMapAttemptCDFs


    def get_failed_map_attempt_cdfs(self):
        return self.__failedMapAttemptCDFs


    def get_successful_reduce_attempt_cdf(self):
        return self.__successfulReduceAttemptCDF


    def get_failed_reduce_attempt_cdf(self):
        return self.__failedReduceAttemptCDF


    def get_mapper_tries_to_succeed(self):
        return self.__mapper_tries_to_succeed


    def set_job_id(self, value):
        self.__jobID = value


    def set_submit_time(self, value):
        self.__submitTime = value


    def set_launch_time(self, value):
        self.__launchTime = value


    def set_finish_time(self, value):
        self.__finishTime = value


    def set_total_maps(self, value):
        self.__totalMaps = value


    def set_total_reduce(self, value):
        self.__totalReduce = value


    def set_result(self, value):
        self.__result = value


    def set_job_type(self, value):
        self.__jobType = value


    def set_map_tasks(self, value):
        self.__mapTasks = value


    def set_reduce_tasks(self, value):
        self.__reduceTasks = value


    def set_successful_map_attempt_cdfs(self, value):
        self.__successfulMapAttemptCDFs = value


    def set_failed_map_attempt_cdfs(self, value):
        self.__failedMapAttemptCDFs = value


    def set_successful_reduce_attempt_cdf(self, value):
        self.__successfulReduceAttemptCDF = value


    def set_failed_reduce_attempt_cdf(self, value):
        self.__failedReduceAttemptCDF = value


    def set_mapper_tries_to_succeed(self, value):
        self.__mapper_tries_to_succeed = value


    def del_job_id(self):
        del self.__jobID


    def del_submit_time(self):
        del self.__submitTime


    def del_launch_time(self):
        del self.__launchTime


    def del_finish_time(self):
        del self.__finishTime


    def del_total_maps(self):
        del self.__totalMaps


    def del_total_reduce(self):
        del self.__totalReduce


    def del_result(self):
        del self.__result


    def del_job_type(self):
        del self.__jobType


    def del_map_tasks(self):
        del self.__mapTasks


    def del_reduce_tasks(self):
        del self.__reduceTasks


    def del_successful_map_attempt_cdfs(self):
        del self.__successfulMapAttemptCDFs


    def del_failed_map_attempt_cdfs(self):
        del self.__failedMapAttemptCDFs


    def del_successful_reduce_attempt_cdf(self):
        del self.__successfulReduceAttemptCDF


    def del_failed_reduce_attempt_cdf(self):
        del self.__failedReduceAttemptCDF


    def del_mapper_tries_to_succeed(self):
        del self.__mapper_tries_to_succeed

    jobID = property(get_job_id, set_job_id, del_job_id, "jobID's docstring")
    submitTime = property(get_submit_time, set_submit_time, del_submit_time, "submitTime's docstring")
    launchTime = property(get_launch_time, set_launch_time, del_launch_time, "launchTime's docstring")
    finishTime = property(get_finish_time, set_finish_time, del_finish_time, "finishTime's docstring")
    totalMaps = property(get_total_maps, set_total_maps, del_total_maps, "totalMaps's docstring")
    totalReduce = property(get_total_reduce, set_total_reduce, del_total_reduce, "totalReduce's docstring")
    result = property(get_result, set_result, del_result, "result's docstring")
    jobType = property(get_job_type, set_job_type, del_job_type, "jobType's docstring")
    mapTasks = property(get_map_tasks, set_map_tasks, del_map_tasks, "mapTasks's docstring")
    reduceTasks = property(get_reduce_tasks, set_reduce_tasks, del_reduce_tasks, "reduceTasks's docstring")
    successfulMapAttemptCDFs = property(get_successful_map_attempt_cdfs, set_successful_map_attempt_cdfs, del_successful_map_attempt_cdfs, "successfulMapAttemptCDFs's docstring")
    failedMapAttemptCDFs = property(get_failed_map_attempt_cdfs, set_failed_map_attempt_cdfs, del_failed_map_attempt_cdfs, "failedMapAttemptCDFs's docstring")
    successfulReduceAttemptCDF = property(get_successful_reduce_attempt_cdf, set_successful_reduce_attempt_cdf, del_successful_reduce_attempt_cdf, "successfulReduceAttemptCDF's docstring")
    failedReduceAttemptCDF = property(get_failed_reduce_attempt_cdf, set_failed_reduce_attempt_cdf, del_failed_reduce_attempt_cdf, "failedReduceAttemptCDF's docstring")
    mapper_tries_to_succeed = property(get_mapper_tries_to_succeed, set_mapper_tries_to_succeed, del_mapper_tries_to_succeed, "mapper_tries_to_succeed's docstring")
    
if __name__ == '__main__':
    jhist = json.load(file("/Users/frank/Downloads/job2.json"))
    j = Hadoop2JobStats(jhist)
    pprint.pprint(j.to_dict())