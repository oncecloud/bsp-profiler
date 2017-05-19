#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/03/17

import json
import pprint
import re
import operator
from pip._vendor import progress

class Hadoop2JobAnalysis(object):
    
    def __init__(self, hadoop2_job_stats_dict, yarn_cluster_workers_number=7, yarn_max_memory_mb=5120, yarn_max_cpu=5, yarn_container_memory_mb=1024, yarn_container_cpu=1, compute_node_max_memory_gb=65536, compute_node_max_cpu_core=24):
        self.hadoop2_job_stats = hadoop2_job_stats_dict
        self.job_id = self.hadoop2_job_stats.get('jobID')
        self.job_submit_time = self.hadoop2_job_stats.get('submitTime')
        self.job_launch_time = self.hadoop2_job_stats.get('launchTime')
        self.job_finish_time = self.hadoop2_job_stats.get('finishTime')
        self.job_run_time = self.job_finish_time - self.job_launch_time
        self.job_elapsed = self.job_finish_time - self.job_submit_time
        self.total_maps = self.hadoop2_job_stats.get('totalMaps')
        self.total_reduces = self.hadoop2_job_stats.get('totalReduces')
        self.job_resource_usage_metrics = {}
        self.map_contain_final_failed = False
        self.successful_attempt_timeline = []
        self.successful_attempt_topology = []
        self.job_data_skew = []
        self.map_final_failed_task_ID = []
        self.map_elapsed_maximum = 0
        self.map_elapsed_minimum = 0
        self.map_elapsed_average = 0
        self.successful_map_attempt_CDFs = self.hadoop2_job_stats.get('successfulMapAttemptCDFs')
        self.failed_map_attempt_CDFs = self.hadoop2_job_stats.get('failedMapAttemptCDFs')
        self.map_elapsed_maximum_contain_attempt_failed = False
        self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum = 0
        self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum = 0
        self.failed_map_attempt_total_time = 0
        self.failed_map_attempt_count = 0
        self.map_overview = []
        self.reduce_contain_final_failed = False
        self.reduce_final_failed_task_ID = []
        self.reduce_elapsed_maximum = 0
        self.reduce_elapsed_minimum = 0
        self.reduce_elapsed_average = 0
        self.successful_reduce_attempt_CDFs = self.hadoop2_job_stats.get('successfulReduceAttemptCDF')
        self.failed_reduce_attempt_CDFs = self.hadoop2_job_stats.get('failedReduceAttemptCDF')
        self.reduce_elapsed_maximum_contain_attempt_failed = False
        self.reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum = 0
        self.reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum = 0
        self.failed_reduce_attempt_total_time = 0
        self.failed_reduce_attempt_count = 0
        self.reduce_overview = []
        self.cluster_advise = {}
        self.map_tasks_analysis()
        self.reduce_task_analysis()
        self.cluster_analysis(int(yarn_cluster_workers_number), int(round(float(yarn_max_memory_mb)/1024)), int(yarn_max_cpu), int(round(float(yarn_container_memory_mb)/1024)), int(yarn_container_cpu), int(compute_node_max_memory_gb), int(compute_node_max_cpu_core))
        self.total_container = int(yarn_cluster_workers_number) * int(round(float(yarn_max_memory_mb)/1024)) / int(round(float(yarn_container_memory_mb)/1024))
        self.timeline_analysis(int(yarn_cluster_workers_number))
    
    def to_dict(self):
        retv = {
            "jobID" : self.job_id,
            "jobSubmitTime" : self.job_submit_time,
            "jobLaunchTime" : self.job_launch_time,
            "jobFinishTime" : self.job_finish_time,
            "jobRuntime" : self.job_run_time,
            "jobElapsed" : self.job_elapsed,
            "jobResourceUsageMetrics" : self.job_resource_usage_metrics,
            "jobDataSkew" : self.job_data_skew,
            "totalMaps" : self.total_maps,
            "totalReduces" : self.total_reduces,
            "mapContainFinalFailed" : self.map_contain_final_failed,
            "mapFinalFailedTaskID" : self.map_final_failed_task_ID,
            "mapElapsedMaximum" : self.map_elapsed_maximum,
            "mapElapsedMinimum" : self.map_elapsed_minimum,
            "mapElapsedAverage" : self.map_elapsed_average,
            "mapElapsedMaximumContainAttemptFailed" : self.map_elapsed_maximum_contain_attempt_failed,
            "mapAttemptSpilledMinusMapOutputMinusReduceOutputMaximum" : self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum,
            "mapAttemptSpilledMinusMapOutputMinusReduceOutputMinimum" : self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum,
#             "successfulMapAttemptCDFs" : self.successful_map_attempt_CDFs,
#             "failedMapAttemptCDFs" : self.failed_map_attempt_CDFs,
            "failedMapAttemptTotalTime" : self.failed_map_attempt_total_time,
            "failedMapAttemptCount" : self.failed_map_attempt_count,
            "reduceContainFinalFailed" : self.reduce_contain_final_failed,
            "reduceFinalFailedTaskID" : self.reduce_final_failed_task_ID,
            "reduceElapsedMaximum" : self.reduce_elapsed_maximum,
            "reduceElapsedMinimum" : self.reduce_elapsed_minimum,
            "reduceElapsedAverage" : self.reduce_elapsed_average,
            "reduceElapsedMaximumContainAttemptFailed" : self.reduce_elapsed_maximum_contain_attempt_failed,
#             "successfulReduceAttemptCDFs" : self.successful_reduce_attempt_CDFs,
#             "failedReduceAttemptCDFs" : self.failed_reduce_attempt_CDFs,
            "failedReduceAttemptTotalTime" : self.failed_reduce_attempt_total_time,
            "failedReduceAttemptCount" : self.failed_reduce_attempt_count,
            "clusterAdvise" : self.cluster_advise,
            }
        return retv
    
    def _job_progress_percentile_timestamp(self):
        job_runtime = self.job_finish_time - self.job_launch_time
        progress_percentile = []
        for i in xrange(0, 100, 5):
            progress_percentile.append((float(i) / 100, float(i + 5) / 100))
        progress_percentile_timestamp = []
        for p in progress_percentile:
            time_interval_s = int(round(job_runtime * p[0]))
            time_interval_e = int(round(job_runtime * p[1]))
            progress_percentile_timestamp.append((self.job_launch_time + time_interval_s, self.job_launch_time + time_interval_e))
        return progress_percentile_timestamp

    def _job_progress_percentile_parallelism_init(self):
        job_progress_percentile_parallelism = []
        for i in xrange(0, 100, 5):
            job_progress_percentile_parallelism.append(0)       
        return job_progress_percentile_parallelism 
        
    def map_tasks_analysis(self):
        total_maps = self.hadoop2_job_stats.get('totalMaps')
        map_tasks = self.hadoop2_job_stats.get('mapTasks')
        set_value_once = [0, 0]
        map_records_keys = ['taskID', 'startTime', 'finishTime']
        map_virtual_memory_usage_total = 0
        map_physical_memory_usage_total = 0
        map_cpu_time_usage_total = 0
        map_elapsed_total = 0
        map_attempt_run_time_total = 0
        map_attempt_count = 0
        map_attempt_input_bytes_total = 0
        map_attempt_output_bytes_total = 0
        for map_task in map_tasks:
            map_records = {}
            for map_records_key in map_records_keys:
                map_records[map_records_key] = map_task.get(map_records_key)
            map_attempts = map_task.get('attempts')
            map_attempts_count = len(map_attempts)
            if map_task.get('taskStatus') != 'SUCCESS':
                self.map_contain_final_failed = True
                self.map_final_failed_task_ID.append(map_task.get('taskID'))
            cost_time = map_task.get('finishTime') - map_task.get('startTime')
            map_elapsed_total += cost_time
            map_records['runTime'] = cost_time
            map_attempt_input_bytes_total += map_task.get('inputBytes')
            map_attempt_output_bytes_total += map_task.get('outputBytes')
            map_records['inputMbPerSec'] = '%.6f' % ((float(map_task.get('inputBytes')) / 1024 / 1024) / (float(cost_time) / 1000))
            map_records['outputMbPerSec'] = '%.6f' % ((float(map_task.get('outputBytes')) / 1024 / 1024) / (float(cost_time) / 1000))
            if not set_value_once[0]:
                self.map_elapsed_maximum = cost_time
                self.map_elapsed_minimum = cost_time
                set_value_once[0] = 1
            if cost_time > self.map_elapsed_maximum:
                self.map_elapsed_maximum = cost_time
                self.map_elapsed_maximum_contain_attempt_failed = False
                if map_attempts_count >= 1:
                    for map_attempt in map_attempts:
                        map_attempt_result = map_attempt.get('result')
                        if map_attempt_result != 'SUCCESS':
                            self.map_elapsed_maximum_contain_attempt_failed = True
                            continue
            elif cost_time < self.map_elapsed_minimum:
                self.map_elapsed_minimum = cost_time
            else:
                pass
            map_attempt_records_list = []
            if map_attempts_count >= 1:
                for map_attempt in map_attempts:
                    map_attempt_records = {}
                    map_attempt_records['spilledRecords'] = map_attempt.get('spilledRecords')
                    run_time = map_attempt.get('finishTime') - map_attempt.get('startTime')
                    map_attempt_run_time_total += run_time
                    map_attempt_result = map_attempt.get('result')
                    map_attempt_records['runTime'] = run_time
                    map_attempt_records['result'] = map_attempt_result
                    if map_attempt_result != 'SUCCESS':
                        self.failed_map_attempt_count += 1
                        self.failed_map_attempt_total_time += run_time
                    else:
                        successful_map_attempt_timeline_details = {}
                        successful_map_attempt_timeline_details['taskType'] = "map"
                        successful_map_attempt_timeline_details['startTime'] = map_attempt.get('startTime')
                        successful_map_attempt_timeline_details['finishTime'] = map_attempt.get('finishTime')
                        re_host_name = re.search(r'-(\d+)\.', map_attempt.get('hostName'))
                        if re_host_name:
                            successful_map_attempt_timeline_details['hostName'] = re_host_name.group(1)
                        else:
                            raise Exception('Host name mismatch.') 
                        re_task_id = re.search(r"_(\w_\d+_\d)", map_attempt.get('attemptID'))
                        if re_task_id:
                            successful_map_attempt_timeline_details['attemptID'] = re_task_id.group(1)
                        else:
                            raise Exception('Attempt ID mismatch.')
                        self.successful_attempt_timeline.append(successful_map_attempt_timeline_details)
                        map_attempt_count += 1
                    resource_usage_metrics = map_attempt.get('resourceUsageMetrics')
                    cumulative_cpu_usage = resource_usage_metrics.get('cumulativeCpuUsage')
                    physical_memory_usage = resource_usage_metrics.get('physicalMemoryUsage')
                    virtual_memory_usage = resource_usage_metrics.get('virtualMemoryUsage')
                    map_cpu_time_usage_total += cumulative_cpu_usage
                    map_physical_memory_usage_total += physical_memory_usage
                    map_virtual_memory_usage_total += virtual_memory_usage
                    resource_usage_metrics_spec = {}
                    resource_usage_metrics_spec['cpuUsagePerSec'] = '%.6f' % (float(cumulative_cpu_usage) / run_time)
                    resource_usage_metrics_spec['physicalMemoryUsageMb'] = '%.6f' % (float(physical_memory_usage) / 1024 / 1024)
                    map_attempt_records['resourceUsageMetrics'] = resource_usage_metrics_spec
                    spilled_records = map_attempt.get('spilledRecords')
                    map_output_records = map_attempt.get('mapOutputRecords')
                    reduce_output_records = map_attempt.get('reduceOutputRecords')
                    minus_result = spilled_records - map_output_records - reduce_output_records
                    map_attempt_records['spilledMinusMapMinusReduceResult'] = minus_result
                    map_attempt_records_list.append(map_attempt_records)
                    if not set_value_once[1]:
                        self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum = minus_result
                        self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum = minus_result
                        set_value_once[1] = 1
                    if minus_result > self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum:
                        self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum = minus_result
                    elif minus_result < self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum:
                        self.map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum = minus_result
                    else:
                        pass
            map_records['attempts'] = map_attempt_records_list
            self.map_overview.append(map_records)
#         self.job_resource_usage_metrics['mapCumulativeCpuUsageMilliseconds'] = map_cpu_time_usage_total
#         self.job_resource_usage_metrics['mapPhysicalMemoryUsageMb'] = '%.2f' % (float(map_physical_memory_usage_total) / 1024 / 1024)
#         self.job_resource_usage_metrics['mapVirtualMemoryUsageMb'] = '%.2f' % (float(map_virtual_memory_usage_total) / 1024 / 1024)
        self.job_resource_usage_metrics['mapAttemptAverageRuntime'] = '%.2f' % (float(map_attempt_run_time_total) / map_attempt_count)
        self.job_resource_usage_metrics['mapAverageCpuUsage'] = '%.6f' % (float(map_cpu_time_usage_total) / map_attempt_run_time_total)
        self.job_resource_usage_metrics['mapAveragePhysicalMemoryUsageMb'] = '%.6f' % (float(map_physical_memory_usage_total) / 1024 / 1024 / map_attempt_count)
        self.job_resource_usage_metrics['mapAverageVirtualMemoryUsageMb'] = '%.6f' % (float(map_virtual_memory_usage_total) / 1024 / 1024 / map_attempt_count)
        self.job_resource_usage_metrics['mapInputMbTotal'] = '%.2f' % (float(map_attempt_input_bytes_total) / 1024 / 1024)
        self.job_resource_usage_metrics['mapOutputMbTotal'] = '%.2f' % (float(map_attempt_output_bytes_total) / 1024 / 1024)
        self.job_resource_usage_metrics['mapInputAverageIoRateMbPerSec'] = '%.6f' % (float(map_attempt_input_bytes_total) / 1024 / 1024 / map_attempt_run_time_total)
        self.job_resource_usage_metrics['mapOutputAverageIoRateMbPerSec'] = '%.6f' % (float(map_attempt_output_bytes_total) / 1204 / 1024 / map_attempt_run_time_total)
        self.map_elapsed_average = '%.2f' % (float(map_elapsed_total) / self.total_maps)
            
    def reduce_task_analysis(self):
        total_reduces = self.hadoop2_job_stats.get('totalReduces')
        reduce_tasks = self.hadoop2_job_stats.get('reduceTasks')
        set_value_once = [0]
        reduce_records_keys = ['taskID', 'startTime', 'finishTime']
        reduce_virtual_memory_usage_total = 0
        reduce_physical_memory_usage_total = 0
        reduce_cpu_time_usage_total = 0
        reduce_elapsed_total = 0
        reduce_attempt_run_time_total = 0
        reduce_attempt_count = 0
        reduce_attempt_input_bytes_total = 0
        reduce_attempt_output_bytes_total = 0
        for reduce_task in reduce_tasks:
            reduce_records = {}
            for reduce_records_key in reduce_records_keys:
                reduce_records[reduce_records_key] = reduce_task.get(reduce_records_key)
            reduce_attempts = reduce_task.get('attempts')
            reduce_attempts_count = len(reduce_attempts)
            if reduce_task.get('taskStatus') != 'SUCCESS':
                self.reduce_contain_final_failed = True
                self.reduce_final_failed_task_ID.append(reduce_task.get('taskID'))
            cost_time = reduce_task.get('finishTime') - reduce_task.get('startTime')
            reduce_elapsed_total += cost_time
            reduce_records['runTime'] = cost_time
            reduce_attempt_input_bytes_total += reduce_task.get('inputBytes')
            reduce_attempt_output_bytes_total += reduce_task.get('outputBytes')
            reduce_records['inputMbPerSec'] = '%.6f' % ((float(reduce_task.get('inputBytes')) / 1024 / 1024) / (float(cost_time) / 1000))
            reduce_records['outputMbPerSec'] = '%.6f' % ((float(reduce_task.get('outputBytes')) / 1024 / 1024) / (float(cost_time) / 1000))
            if not set_value_once[0]:
                self.reduce_elapsed_maximum = cost_time
                self.reduce_elapsed_minimum = cost_time
                set_value_once[0] = 1
            if cost_time > self.reduce_elapsed_maximum:
                self.reduce_elapsed_maximum = cost_time
                self.reduce_elapsed_maximum_contain_attempt_failed = False
                if reduce_attempts_count >= 1:
                    for reduce_attempt in reduce_attempts:
                        reduce_attempt_result = reduce_attempt.get('result')
                        if reduce_attempt_result != 'SUCCESS':
                            self.reduce_elapsed_maximum_contain_attempt_failed = True
                            continue
            elif cost_time < self.reduce_elapsed_minimum:
                self.reduce_elapsed_minimum = cost_time
            else:
                pass
            reduce_attempt_records_list = []
            if reduce_attempts_count >= 1:
                for reduce_attempt in reduce_attempts:
                    reduce_attempt_records = {}
                    reduce_attempt_records['spilledRecords'] = reduce_attempt.get('spilledRecords')
                    run_time = reduce_attempt.get('finishTime') - reduce_attempt.get('startTime')
                    reduce_attempt_run_time_total += run_time
                    reduce_attempt_result = reduce_attempt.get('result')
                    reduce_attempt_records['runTime'] = run_time
                    reduce_attempt_records['result'] = reduce_attempt_result
                    if reduce_attempt_result != 'SUCCESS':
                        self.failed_reduce_attempt_count += 1
                        self.failed_reduce_attempt_total_time += run_time
                    else:
                        successful_reduce_attempt_timeline_details = {}
                        successful_reduce_attempt_timeline_details['taskType'] = "reduce"
                        successful_reduce_attempt_timeline_details['startTime'] = reduce_attempt.get('startTime')
                        successful_reduce_attempt_timeline_details['finishTime'] = reduce_attempt.get('finishTime')
                        re_host_name = re.search(r'-(\d+)\.', reduce_attempt.get('hostName'))
                        if re_host_name:
                            successful_reduce_attempt_timeline_details['hostName'] = re_host_name.group(1)
                        else:
                            raise Exception('Host name mismatch.') 
                        re_task_id = re.search(r"_(\w_\d+_\d)", reduce_attempt.get('attemptID'))
                        if re_task_id:
                            successful_reduce_attempt_timeline_details['attemptID'] = re_task_id.group(1)
                        else:
                            raise Exception('Attempt ID mismatch.')
                        self.successful_attempt_timeline.append(successful_reduce_attempt_timeline_details)
                        reduce_attempt_count += 1
                    resource_usage_metrics = reduce_attempt.get('resourceUsageMetrics')
                    cumulative_cpu_usage = resource_usage_metrics.get('cumulativeCpuUsage')
                    physical_memory_usage = resource_usage_metrics.get('physicalMemoryUsage')
                    virtual_memory_usage = resource_usage_metrics.get('virtualMemoryUsage')
                    reduce_cpu_time_usage_total += cumulative_cpu_usage
                    reduce_physical_memory_usage_total += physical_memory_usage
                    reduce_virtual_memory_usage_total += virtual_memory_usage
                    resource_usage_metrics_spec = {}
                    resource_usage_metrics_spec['cpuUsagePerSec'] = '%.6f' % (float(cumulative_cpu_usage) / run_time)
                    resource_usage_metrics_spec['physicalMemoryUsageMb'] = '%.6f' % (float(physical_memory_usage) / 1024 / 1024)
                    reduce_attempt_records['resourceUsageMetrics'] = resource_usage_metrics_spec
                    reduce_attempt_records_list.append(reduce_attempt_records)
            reduce_records['attempts'] = reduce_attempt_records_list
            self.reduce_overview.append(reduce_records)
#         self.job_resource_usage_metrics['reduceCumulativeCpuUsageMilliseconds'] = reduce_cpu_time_usage_total
#         self.job_resource_usage_metrics['reducePhysicalMemoryUsageMb'] = '%.2f' % (float(reduce_physical_memory_usage_total) / 1024 / 1024)
#         self.job_resource_usage_metrics['reduceVirtualMemoryUsageMb'] = '%.2f' % (float(reduce_virtual_memory_usage_total) / 1024 / 1024)
        self.job_resource_usage_metrics['reduceAttemptAverageRuntime'] = '%.2f' % (float(reduce_attempt_run_time_total) / reduce_attempt_count)
        self.job_resource_usage_metrics['reduceAverageCpuUsage'] = '%.6f' % (float(reduce_cpu_time_usage_total) / reduce_attempt_run_time_total)
        self.job_resource_usage_metrics['reduceAveragePhysicalMemoryUsageMb'] = '%.6f' % (float(reduce_physical_memory_usage_total) / 1024 / 1024 / reduce_attempt_count)
        self.job_resource_usage_metrics['reduceAverageVirtualMemoryUsageMb'] = '%.6f' % (float(reduce_virtual_memory_usage_total) / 1024 / 1024 / reduce_attempt_count)
        self.job_resource_usage_metrics['reduceInputMbTotal'] = '%.2f' % (float(reduce_attempt_input_bytes_total) / 1024 / 1024)
        self.job_resource_usage_metrics['reduceOutputMbTotal'] = '%.2f' % (float(reduce_attempt_output_bytes_total) / 1024 / 1024)
        self.job_resource_usage_metrics['reduceInputAverageIoRateMbPerSec'] = '%.6f' % (float(reduce_attempt_input_bytes_total) / 1024 / 1024 / reduce_attempt_run_time_total)
        self.job_resource_usage_metrics['reduceOutputAverageIoRateMbPerSec'] = '%.6f' % (float(reduce_attempt_output_bytes_total) / 1024 / 1024 / reduce_attempt_run_time_total)
        self.reduce_elapsed_average = '%.2f' % (float(reduce_elapsed_total) / self.total_reduces)

    def cluster_analysis(self, yarn_cluster_workers_number, yarn_max_memory_gb, yarn_max_cpu, yarn_container_memory_gb, yarn_container_cpu, compute_node_max_memory_gb, compute_node_max_cpu_core):
        scale_prediction = []
        advise = ""
        max_container_per_worker = min(yarn_max_memory_gb / yarn_container_memory_gb, yarn_max_cpu / yarn_container_cpu)
        total_container_all_workers = int(max_container_per_worker * yarn_cluster_workers_number)
        map_modulo_result = self.total_maps % total_container_all_workers
        map_division_result = self.total_maps / total_container_all_workers
        reduce_modulo_result = self.total_reduces % total_container_all_workers
        reduce_division_result = self.total_reduces / total_container_all_workers
        map_loops = map_division_result if map_modulo_result == 0 else map_division_result + 1 
        reduce_loops = reduce_division_result if reduce_modulo_result == 0 else reduce_division_result + 1
        bigger_loops = max(map_loops, reduce_loops)
        if bigger_loops > 1: 
            for decrease_N_loops in range(1, bigger_loops, 1):
                decrease_loops_of_map = decrease_N_loops if cmp(map_loops-1, decrease_N_loops) >= 0 else map_loops-1
                decrease_loops_of_reduce = decrease_N_loops if cmp(reduce_loops-1, decrease_N_loops) >=0 else reduce_loops-1
                loops_after_opt = max(map_loops - decrease_loops_of_map, reduce_loops - decrease_loops_of_reduce)
                time_opt_of_decrease_loops_of_map = self.map_elapsed_minimum * decrease_loops_of_map
                time_opt_of_decrease_loops_of_reduce = self.reduce_elapsed_minimum * decrease_loops_of_reduce
                containers_demands_for_current_loops = self.total_maps / loops_after_opt + self.total_maps % loops_after_opt \
                if map_loops > reduce_loops else self.total_reduces / loops_after_opt + self.total_reduces % loops_after_opt
                total_time_opt = time_opt_of_decrease_loops_of_map + time_opt_of_decrease_loops_of_reduce
                scale_out_workers = containers_demands_for_current_loops / max_container_per_worker \
                if containers_demands_for_current_loops % max_container_per_worker == 0 else containers_demands_for_current_loops / max_container_per_worker + 1
                scale_out_for_decrease_N_loop = {"workers" : scale_out_workers,
                                                 "cpuCore" : yarn_max_cpu,
                                                 "memoryGb" : yarn_max_memory_gb,
                                                 "timeOptOneSecPerResourceUnit" : '%.4f' % (float((scale_out_workers - yarn_cluster_workers_number) * max_container_per_worker) / (float(total_time_opt) / 1000)),
                                                 }
                scale_up_container_per_worker = containers_demands_for_current_loops / yarn_cluster_workers_number \
                if containers_demands_for_current_loops % yarn_cluster_workers_number == 0 else containers_demands_for_current_loops / yarn_cluster_workers_number + 1
                scale_up_for_decrease_N_loop = {"workers" : yarn_cluster_workers_number,
                                                "cpuCore" : yarn_container_cpu * scale_up_container_per_worker, 
                                                "memoryGb" : yarn_container_memory_gb * scale_up_container_per_worker,
                                                "timeOptOneSecPerResourceUnit" : '%.4f' % (float((scale_up_container_per_worker - max_container_per_worker) * yarn_cluster_workers_number) / (float(total_time_opt) / 1000) ),
                                                }
                details_for_decrease_N_loops = {"mapLoopsAfterOpt" : map_loops - decrease_loops_of_map,
                                                "reduceLoopsAfterOpt" : reduce_loops - decrease_loops_of_reduce,
                                                "decreaseLoopsOfMap" : decrease_loops_of_map,
                                                "decreaseLoopsOfReduce" : decrease_loops_of_reduce,
                                                "timeOptimizationOfDecreaseLoopsOfMap" : time_opt_of_decrease_loops_of_map,
                                                "timeOptimizationOfDecreaseLoopsOfReduce" : time_opt_of_decrease_loops_of_reduce,
                                                "timeOptimizationTotal" : total_time_opt,
                                                "jobElapsedAfterOpt" : self.job_elapsed - total_time_opt,
                                                "scaleUpForDecreaseLoops" : scale_up_for_decrease_N_loop,
                                                "scaleOutForDecreaseLoops" : scale_out_for_decrease_N_loop}
                scale_prediction.append(details_for_decrease_N_loops)
            advise += "Scale current cluster to optimize Job's elapsed, details in scalePrediction. p.s. Any bottleneck resource may interfere scale prediction. "
        else:
            advise += "No need to scale. "
            scale_prediction.append({})
        mapInputParallelIoRateMbPerSec = '%.6f' % (float(self.job_resource_usage_metrics['mapInputAverageIoRateMbPerSec']) * total_container_all_workers)
        mapOutputParallelIoRateMbPerSec = '%.6f' % (float(self.job_resource_usage_metrics['mapOutputAverageIoRateMbPerSec']) * total_container_all_workers)
        reduceInputParallelIoRateMbPerSec = '%.6f' % (float(self.job_resource_usage_metrics['reduceInputAverageIoRateMbPerSec']) * total_container_all_workers)
        reduceOutputParallelIoRateMbPerSec = '%.6f' % (float(self.job_resource_usage_metrics['reduceOutputAverageIoRateMbPerSec']) * total_container_all_workers)
        if float(self.job_resource_usage_metrics.get('mapAverageCpuUsage')) >= 0.9 or float(self.job_resource_usage_metrics.get('reduceAverageCpuUsage')) >= 0.9:
            advise += "CPU bottleneck exists in YARN container, mapAverageCpuUsage=%s, reduceAverageCpuUsage=%s. " \
            % (self.job_resource_usage_metrics.get('mapAverageCpuUsage'), self.job_resource_usage_metrics.get('reduceAverageCpuUsage'))
        if float(self.job_resource_usage_metrics.get('mapAveragePhysicalMemoryUsageMb')) >= yarn_container_memory_gb * 1024 or float(self.job_resource_usage_metrics.get('reduceAveragePhysicalMemoryUsageMb')) >= yarn_container_memory_gb * 1024:
            advise += "Memory bottleneck exists in YARN container, mapAveragePhysicalMemoryUsageMb=%s, reduceAverageCpuUsage=%s. " \
            % (self.job_resource_usage_metrics.get('mapAveragePhysicalMemoryUsageMb'), self.job_resource_usage_metrics.get('reduceAveragePhysicalMemoryUsageMb'))
        advise += "Disk parallel IO rate Mb/s details: mapInputParallelIoRateMbPerSec=%s, mapOutputParallelIoRateMbPerSec=%s, reduceInputParallelIoRateMbPerSec=%s, reduceOutputParallelIoRateMbPerSec=%s. " \
        % (mapInputParallelIoRateMbPerSec, mapOutputParallelIoRateMbPerSec, reduceInputParallelIoRateMbPerSec, reduceOutputParallelIoRateMbPerSec)
        self.cluster_advise['advise'] = advise
        self.cluster_advise['scalePrediction'] = scale_prediction
        
    def timeline_analysis(self, yarn_cluster_workers_number):
        job_progress_percentile_timestamp_array = self._job_progress_percentile_timestamp()
        for i in xrange(0, yarn_cluster_workers_number):
            self.successful_attempt_topology.append([])
        sorted_timeline = sorted(self.successful_attempt_timeline, key=operator.itemgetter('startTime'))
        for timeline in sorted_timeline:
            self.successful_attempt_topology[int(timeline.get('hostName'))-1].append([timeline.get('attemptID') , timeline.get('startTime'), timeline.get('finishTime'), timeline.get('finishTime') - timeline.get('startTime')])
        for host in self.successful_attempt_topology:
            job_progress_percentile_parallelism = self._job_progress_percentile_parallelism_init()
            for attempt_details in host:
                for progress in job_progress_percentile_timestamp_array:
                    if cmp(attempt_details[1], progress[0]) >= 0 and cmp(attempt_details[1], progress[1]) <= 0 and cmp(attempt_details[2], progress[1]) >= 0:
#                         print job_progress_percentile_timestamp_array.index(progress)
                        job_progress_percentile_parallelism[job_progress_percentile_timestamp_array.index(progress)] += 1
                    elif cmp(attempt_details[1], progress[0]) >= 0 and cmp(attempt_details[1], progress[1]) <= 0 and cmp(attempt_details[2], progress[1]) <= 0:
                        job_progress_percentile_parallelism[job_progress_percentile_timestamp_array.index(progress)] += 1
                    if cmp(attempt_details[1], progress[0]) <= 0 and cmp(attempt_details[2], progress[1]) >=0:
                        job_progress_percentile_parallelism[job_progress_percentile_timestamp_array.index(progress)] += 1
                    if cmp(attempt_details[1], progress[0]) >= 0 and cmp(attempt_details[2], progress[0]) >= 0 and cmp(attempt_details[2], progress[1]) <= 0:
                        job_progress_percentile_parallelism[job_progress_percentile_timestamp_array.index(progress)] += 1
            self.job_data_skew.append([len(host), job_progress_percentile_parallelism])
        return sorted_timeline

    def get_hadoop_2_job_stats(self):
        return self.__hadoop2_job_stats


    def get_job_id(self):
        return self.__job_id


    def get_job_submit_time(self):
        return self.__job_submit_time


    def get_job_launch_time(self):
        return self.__job_launch_time


    def get_job_finish_time(self):
        return self.__job_finish_time


    def get_job_run_time(self):
        return self.__job_run_time


    def get_job_elapsed(self):
        return self.__job_elapsed


    def get_total_maps(self):
        return self.__total_maps


    def get_total_reduces(self):
        return self.__total_reduces


    def get_job_resource_usage_metrics(self):
        return self.__job_resource_usage_metrics


    def get_map_contain_final_failed(self):
        return self.__map_contain_final_failed


    def get_successful_attempt_timeline(self):
        return self.__successful_attempt_timeline


    def get_map_final_failed_task_id(self):
        return self.__map_final_failed_task_ID


    def get_map_elapsed_maximum(self):
        return self.__map_elapsed_maximum


    def get_map_elapsed_minimum(self):
        return self.__map_elapsed_minimum


    def get_map_elapsed_average(self):
        return self.__map_elapsed_average


    def get_successful_map_attempt_cdfs(self):
        return self.__successful_map_attempt_CDFs


    def get_failed_map_attempt_cdfs(self):
        return self.__failed_map_attempt_CDFs


    def get_map_elapsed_maximum_contain_attempt_failed(self):
        return self.__map_elapsed_maximum_contain_attempt_failed


    def get_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum(self):
        return self.__map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum


    def get_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum(self):
        return self.__map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum


    def get_failed_map_attempt_total_time(self):
        return self.__failed_map_attempt_total_time


    def get_failed_map_attempt_count(self):
        return self.__failed_map_attempt_count


    def get_map_overview(self):
        return self.__map_overview


    def get_reduce_contain_final_failed(self):
        return self.__reduce_contain_final_failed


    def get_reduce_final_failed_task_id(self):
        return self.__reduce_final_failed_task_ID


    def get_reduce_elapsed_maximum(self):
        return self.__reduce_elapsed_maximum


    def get_reduce_elapsed_minimum(self):
        return self.__reduce_elapsed_minimum


    def get_reduce_elapsed_average(self):
        return self.__reduce_elapsed_average


    def get_successful_reduce_attempt_cdfs(self):
        return self.__successful_reduce_attempt_CDFs


    def get_failed_reduce_attempt_cdfs(self):
        return self.__failed_reduce_attempt_CDFs


    def get_reduce_elapsed_maximum_contain_attempt_failed(self):
        return self.__reduce_elapsed_maximum_contain_attempt_failed


    def get_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum(self):
        return self.__reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum


    def get_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum(self):
        return self.__reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum


    def get_failed_reduce_attempt_total_time(self):
        return self.__failed_reduce_attempt_total_time


    def get_failed_reduce_attempt_count(self):
        return self.__failed_reduce_attempt_count


    def get_reduce_overview(self):
        return self.__reduce_overview


    def get_cluster_advise(self):
        return self.__cluster_advise


    def set_hadoop_2_job_stats(self, value):
        self.__hadoop2_job_stats = value


    def set_job_id(self, value):
        self.__job_id = value


    def set_job_submit_time(self, value):
        self.__job_submit_time = value


    def set_job_launch_time(self, value):
        self.__job_launch_time = value


    def set_job_finish_time(self, value):
        self.__job_finish_time = value


    def set_job_run_time(self, value):
        self.__job_run_time = value


    def set_job_elapsed(self, value):
        self.__job_elapsed = value


    def set_total_maps(self, value):
        self.__total_maps = value


    def set_total_reduces(self, value):
        self.__total_reduces = value


    def set_job_resource_usage_metrics(self, value):
        self.__job_resource_usage_metrics = value


    def set_map_contain_final_failed(self, value):
        self.__map_contain_final_failed = value


    def set_successful_attempt_timeline(self, value):
        self.__successful_attempt_timeline = value


    def set_map_final_failed_task_id(self, value):
        self.__map_final_failed_task_ID = value


    def set_map_elapsed_maximum(self, value):
        self.__map_elapsed_maximum = value


    def set_map_elapsed_minimum(self, value):
        self.__map_elapsed_minimum = value


    def set_map_elapsed_average(self, value):
        self.__map_elapsed_average = value


    def set_successful_map_attempt_cdfs(self, value):
        self.__successful_map_attempt_CDFs = value


    def set_failed_map_attempt_cdfs(self, value):
        self.__failed_map_attempt_CDFs = value


    def set_map_elapsed_maximum_contain_attempt_failed(self, value):
        self.__map_elapsed_maximum_contain_attempt_failed = value


    def set_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum(self, value):
        self.__map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum = value


    def set_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum(self, value):
        self.__map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum = value


    def set_failed_map_attempt_total_time(self, value):
        self.__failed_map_attempt_total_time = value


    def set_failed_map_attempt_count(self, value):
        self.__failed_map_attempt_count = value


    def set_map_overview(self, value):
        self.__map_overview = value


    def set_reduce_contain_final_failed(self, value):
        self.__reduce_contain_final_failed = value


    def set_reduce_final_failed_task_id(self, value):
        self.__reduce_final_failed_task_ID = value


    def set_reduce_elapsed_maximum(self, value):
        self.__reduce_elapsed_maximum = value


    def set_reduce_elapsed_minimum(self, value):
        self.__reduce_elapsed_minimum = value


    def set_reduce_elapsed_average(self, value):
        self.__reduce_elapsed_average = value


    def set_successful_reduce_attempt_cdfs(self, value):
        self.__successful_reduce_attempt_CDFs = value


    def set_failed_reduce_attempt_cdfs(self, value):
        self.__failed_reduce_attempt_CDFs = value


    def set_reduce_elapsed_maximum_contain_attempt_failed(self, value):
        self.__reduce_elapsed_maximum_contain_attempt_failed = value


    def set_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum(self, value):
        self.__reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum = value


    def set_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum(self, value):
        self.__reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum = value


    def set_failed_reduce_attempt_total_time(self, value):
        self.__failed_reduce_attempt_total_time = value


    def set_failed_reduce_attempt_count(self, value):
        self.__failed_reduce_attempt_count = value


    def set_reduce_overview(self, value):
        self.__reduce_overview = value


    def set_cluster_advise(self, value):
        self.__cluster_advise = value


    def del_hadoop_2_job_stats(self):
        del self.__hadoop2_job_stats


    def del_job_id(self):
        del self.__job_id


    def del_job_submit_time(self):
        del self.__job_submit_time


    def del_job_launch_time(self):
        del self.__job_launch_time


    def del_job_finish_time(self):
        del self.__job_finish_time


    def del_job_run_time(self):
        del self.__job_run_time


    def del_job_elapsed(self):
        del self.__job_elapsed


    def del_total_maps(self):
        del self.__total_maps


    def del_total_reduces(self):
        del self.__total_reduces


    def del_job_resource_usage_metrics(self):
        del self.__job_resource_usage_metrics


    def del_map_contain_final_failed(self):
        del self.__map_contain_final_failed


    def del_successful_attempt_timeline(self):
        del self.__successful_attempt_timeline


    def del_map_final_failed_task_id(self):
        del self.__map_final_failed_task_ID


    def del_map_elapsed_maximum(self):
        del self.__map_elapsed_maximum


    def del_map_elapsed_minimum(self):
        del self.__map_elapsed_minimum


    def del_map_elapsed_average(self):
        del self.__map_elapsed_average


    def del_successful_map_attempt_cdfs(self):
        del self.__successful_map_attempt_CDFs


    def del_failed_map_attempt_cdfs(self):
        del self.__failed_map_attempt_CDFs


    def del_map_elapsed_maximum_contain_attempt_failed(self):
        del self.__map_elapsed_maximum_contain_attempt_failed


    def del_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum(self):
        del self.__map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum


    def del_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum(self):
        del self.__map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum


    def del_failed_map_attempt_total_time(self):
        del self.__failed_map_attempt_total_time


    def del_failed_map_attempt_count(self):
        del self.__failed_map_attempt_count


    def del_map_overview(self):
        del self.__map_overview


    def del_reduce_contain_final_failed(self):
        del self.__reduce_contain_final_failed


    def del_reduce_final_failed_task_id(self):
        del self.__reduce_final_failed_task_ID


    def del_reduce_elapsed_maximum(self):
        del self.__reduce_elapsed_maximum


    def del_reduce_elapsed_minimum(self):
        del self.__reduce_elapsed_minimum


    def del_reduce_elapsed_average(self):
        del self.__reduce_elapsed_average


    def del_successful_reduce_attempt_cdfs(self):
        del self.__successful_reduce_attempt_CDFs


    def del_failed_reduce_attempt_cdfs(self):
        del self.__failed_reduce_attempt_CDFs


    def del_reduce_elapsed_maximum_contain_attempt_failed(self):
        del self.__reduce_elapsed_maximum_contain_attempt_failed


    def del_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum(self):
        del self.__reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum


    def del_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum(self):
        del self.__reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum


    def del_failed_reduce_attempt_total_time(self):
        del self.__failed_reduce_attempt_total_time


    def del_failed_reduce_attempt_count(self):
        del self.__failed_reduce_attempt_count


    def del_reduce_overview(self):
        del self.__reduce_overview


    def del_cluster_advise(self):
        del self.__cluster_advise

    hadoop2_job_stats = property(get_hadoop_2_job_stats, set_hadoop_2_job_stats, del_hadoop_2_job_stats, "hadoop2_job_stats's docstring")
    job_id = property(get_job_id, set_job_id, del_job_id, "job_id's docstring")
    job_submit_time = property(get_job_submit_time, set_job_submit_time, del_job_submit_time, "job_submit_time's docstring")
    job_launch_time = property(get_job_launch_time, set_job_launch_time, del_job_launch_time, "job_launch_time's docstring")
    job_finish_time = property(get_job_finish_time, set_job_finish_time, del_job_finish_time, "job_finish_time's docstring")
    job_run_time = property(get_job_run_time, set_job_run_time, del_job_run_time, "job_run_time's docstring")
    job_elapsed = property(get_job_elapsed, set_job_elapsed, del_job_elapsed, "job_elapsed's docstring")
    total_maps = property(get_total_maps, set_total_maps, del_total_maps, "total_maps's docstring")
    total_reduces = property(get_total_reduces, set_total_reduces, del_total_reduces, "total_reduces's docstring")
    job_resource_usage_metrics = property(get_job_resource_usage_metrics, set_job_resource_usage_metrics, del_job_resource_usage_metrics, "job_resource_usage_metrics's docstring")
    map_contain_final_failed = property(get_map_contain_final_failed, set_map_contain_final_failed, del_map_contain_final_failed, "map_contain_final_failed's docstring")
    successful_attempt_timeline = property(get_successful_attempt_timeline, set_successful_attempt_timeline, del_successful_attempt_timeline, "successful_attempt_timeline's docstring")
    map_final_failed_task_ID = property(get_map_final_failed_task_id, set_map_final_failed_task_id, del_map_final_failed_task_id, "map_final_failed_task_ID's docstring")
    map_elapsed_maximum = property(get_map_elapsed_maximum, set_map_elapsed_maximum, del_map_elapsed_maximum, "map_elapsed_maximum's docstring")
    map_elapsed_minimum = property(get_map_elapsed_minimum, set_map_elapsed_minimum, del_map_elapsed_minimum, "map_elapsed_minimum's docstring")
    map_elapsed_average = property(get_map_elapsed_average, set_map_elapsed_average, del_map_elapsed_average, "map_elapsed_average's docstring")
    successful_map_attempt_CDFs = property(get_successful_map_attempt_cdfs, set_successful_map_attempt_cdfs, del_successful_map_attempt_cdfs, "successful_map_attempt_CDFs's docstring")
    failed_map_attempt_CDFs = property(get_failed_map_attempt_cdfs, set_failed_map_attempt_cdfs, del_failed_map_attempt_cdfs, "failed_map_attempt_CDFs's docstring")
    map_elapsed_maximum_contain_attempt_failed = property(get_map_elapsed_maximum_contain_attempt_failed, set_map_elapsed_maximum_contain_attempt_failed, del_map_elapsed_maximum_contain_attempt_failed, "map_elapsed_maximum_contain_attempt_failed's docstring")
    map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum = property(get_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum, set_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum, del_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum, "map_attempt_spilled_minus_mapoutput_minus_reduceoutput_maximum's docstring")
    map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum = property(get_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum, set_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum, del_map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum, "map_attempt_spilled_minus_mapoutput_minus_reduceoutput_minimum's docstring")
    failed_map_attempt_total_time = property(get_failed_map_attempt_total_time, set_failed_map_attempt_total_time, del_failed_map_attempt_total_time, "failed_map_attempt_total_time's docstring")
    failed_map_attempt_count = property(get_failed_map_attempt_count, set_failed_map_attempt_count, del_failed_map_attempt_count, "failed_map_attempt_count's docstring")
    map_overview = property(get_map_overview, set_map_overview, del_map_overview, "map_overview's docstring")
    reduce_contain_final_failed = property(get_reduce_contain_final_failed, set_reduce_contain_final_failed, del_reduce_contain_final_failed, "reduce_contain_final_failed's docstring")
    reduce_final_failed_task_ID = property(get_reduce_final_failed_task_id, set_reduce_final_failed_task_id, del_reduce_final_failed_task_id, "reduce_final_failed_task_ID's docstring")
    reduce_elapsed_maximum = property(get_reduce_elapsed_maximum, set_reduce_elapsed_maximum, del_reduce_elapsed_maximum, "reduce_elapsed_maximum's docstring")
    reduce_elapsed_minimum = property(get_reduce_elapsed_minimum, set_reduce_elapsed_minimum, del_reduce_elapsed_minimum, "reduce_elapsed_minimum's docstring")
    reduce_elapsed_average = property(get_reduce_elapsed_average, set_reduce_elapsed_average, del_reduce_elapsed_average, "reduce_elapsed_average's docstring")
    successful_reduce_attempt_CDFs = property(get_successful_reduce_attempt_cdfs, set_successful_reduce_attempt_cdfs, del_successful_reduce_attempt_cdfs, "successful_reduce_attempt_CDFs's docstring")
    failed_reduce_attempt_CDFs = property(get_failed_reduce_attempt_cdfs, set_failed_reduce_attempt_cdfs, del_failed_reduce_attempt_cdfs, "failed_reduce_attempt_CDFs's docstring")
    reduce_elapsed_maximum_contain_attempt_failed = property(get_reduce_elapsed_maximum_contain_attempt_failed, set_reduce_elapsed_maximum_contain_attempt_failed, del_reduce_elapsed_maximum_contain_attempt_failed, "reduce_elapsed_maximum_contain_attempt_failed's docstring")
    reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum = property(get_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum, set_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum, del_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum, "reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_maximum's docstring")
    reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum = property(get_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum, set_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum, del_reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum, "reduce_attempt_spilled_minus_reduceoutput_minus_reduceoutput_minimum's docstring")
    failed_reduce_attempt_total_time = property(get_failed_reduce_attempt_total_time, set_failed_reduce_attempt_total_time, del_failed_reduce_attempt_total_time, "failed_reduce_attempt_total_time's docstring")
    failed_reduce_attempt_count = property(get_failed_reduce_attempt_count, set_failed_reduce_attempt_count, del_failed_reduce_attempt_count, "failed_reduce_attempt_count's docstring")
    reduce_overview = property(get_reduce_overview, set_reduce_overview, del_reduce_overview, "reduce_overview's docstring")
    cluster_advise = property(get_cluster_advise, set_cluster_advise, del_cluster_advise, "cluster_advise's docstring")

if __name__ == '__main__':
    from hadoop2_job_stats import Hadoop2JobStats
    jhist1 = json.load(file("/Users/frank/Working/Projects/lenovo/TeraSort_cpu_pin_test/TS_14G14U_5_in_diff_machines_pin_1.json"))
    j1 = Hadoop2JobStats(jhist1)
    a1 = Hadoop2JobAnalysis(j1.to_dict(), 5, 14*1024, 14)
#     print "===============Hadoop cluster: 10 workers(8G/8U)================"
    pprint.pprint(a1.to_dict())
#     pprint.pprint(a1.get_successful_attempt_timeline())
#     pprint.pprint(a1.get_successful_map_attempt_cdfs())
#     pprint.pprint(a1.get_successful_reduce_attempt_cdfs())
    print "\n"
    
    jhist2 = json.load(file("/Users/frank/Working/Projects/lenovo/TeraSort_cpu_pin_test/TS_14G14U_5_in_3machines_pin_1.json"))
    j2 = Hadoop2JobStats(jhist2)
    a2 = Hadoop2JobAnalysis(j2.to_dict(), 5, 14*1024, 14)
#     print "===============Hadoop cluster: 10 workers(4G/8U)================"
#     print "Job elapsed: %s seconds" % (a2.get_job_elapsed() / 1000)
#     print a2.get_map_attempt_start_time_array()
#     sorted_map_attempt_start_time_array = sorted(a2.get_map_attempt_start_time_array())
#     sorted_map_attempt_finish_time_array = sorted(a2.get_map_attempt_finish_time_array())
#     pprint.pprint(sorted_map_attempt_start_time_array[-1] - sorted_map_attempt_start_time_array[0])
#     pprint.pprint(sorted_map_attempt_finish_time_array[-1] - sorted_map_attempt_finish_time_array[0])
#     sorted_reduce_attempt_start_time_array = sorted(a2.get_reduce_attempt_start_time_array())
#     sorted_reduce_attempt_finish_time_array = sorted(a2.get_reduce_attempt_finish_time_array())
#     pprint.pprint(sorted_reduce_attempt_start_time_array[-1] - sorted_reduce_attempt_start_time_array[0])
#     pprint.pprint(sorted_reduce_attempt_finish_time_array[-1] - sorted_reduce_attempt_finish_time_array[0])
    pprint.pprint(a2.to_dict())
#     pprint.pprint(a2.get_successful_map_attempt_cdfs())
#     pprint.pprint(a2.get_successful_reduce_attempt_cdfs())
    print "\n"
     
#     jhist3 = json.load(file("/Users/frank/Downloads/TS_15G15U_9_1-trace-after-opt.json"))
#     j3 = Hadoop2JobStats(jhist3)
#     a3 = Hadoop2JobAnalysis(j3.to_dict(), 9, 15*1024, 15)
#     print "===============Hadoop cluster: 10 workers(4G/4U)================"
#     print "Job elapsed: %s seconds" % (a3.get_job_elapsed() / 1000)
#     pprint.pprint(a3.to_dict())
#     pprint.pprint(a1.get_map_overview())
#     pprint.pprint(a1.get_reduce_overview())
    
