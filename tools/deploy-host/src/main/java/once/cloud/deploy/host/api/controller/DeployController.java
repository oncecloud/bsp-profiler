// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/21

package once.cloud.deploy.host.api.controller;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import once.cloud.deploy.host.service.DeployService;

@Controller
public class DeployController {
	private DeployService deployService;

	private DeployService getDeployService() {
		return deployService;
	}

	@Autowired
	private void setDeployService(DeployService deployService) {
		this.deployService = deployService;
	}

	// Slave IP split by space
	@RequestMapping(value = "/Api/Deploy/Hadoop", method = { RequestMethod.POST })
	@ResponseBody
	public boolean deployHadoopCluster(@RequestHeader("x-ocme-hadoop-location") String location,
			@RequestHeader("x-ocme-hadoop-master-ip") String masterIp,
			@RequestHeader("x-ocme-hadoop-slave-ips") String slaveIps) {
		List<String> slaveIpList = new ArrayList<String>();
		String[] ips = slaveIps.split(" ");
		int i = 0;
		for (i = 0; i < ips.length; i++) {
			if (!(ips[i].isEmpty())) {
				slaveIpList.add(ips[i]);
			}
		}
		return this.getDeployService().deployHadoopCluster(location, masterIp, slaveIpList);
	}
}
