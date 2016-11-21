// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/21

package once.cloud.deploy.host.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import once.cloud.deploy.host.helper.AgentHelper;

@Component
public class DeployService {
	private AgentHelper agentHelper;

	private AgentHelper getAgentHelper() {
		return agentHelper;
	}

	@Autowired
	private void setAgentHelper(AgentHelper agentHelper) {
		this.agentHelper = agentHelper;
	}

	private String coreSiteFileLocationTemplate = "{location}/etc/hadoop/core-site.xml";
	private String coreSiteFileContentTemplate = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
			+ "<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n" + "<!--\n"
			+ "  Licensed under the Apache License, Version 2.0 (the \"License\");\n"
			+ "  you may not use this file except in compliance with the License.\n"
			+ "  You may obtain a copy of the License at\n" + "\n" + "    http://www.apache.org/licenses/LICENSE-2.0\n"
			+ "\n" + "  Unless required by applicable law or agreed to in writing, software\n"
			+ "  distributed under the License is distributed on an \"AS IS\" BASIS,\n"
			+ "  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
			+ "  See the License for the specific language governing permissions and\n"
			+ "  limitations under the License. See accompanying LICENSE file.\n" + "-->\n" + "\n"
			+ "<!-- Put site-specific property overrides in this file. -->\n" + "\n" + "<configuration>\n"
			+ "    <property>\n" + "        <name>fs.defaultFS</name>\n"
			+ "        <value>hdfs://{master}:9000</value>\n" + "    </property>\n" + "    <property>\n"
			+ "        <name>hadoop.tmp.dir</name>\n" + "        <value>file:{location}/tmp</value>\n"
			+ "    </property>\n" + "    <property>\n" + "        <name>io.file.buffer.size</name>\n"
			+ "        <value>131702</value>\n" + "    </property>\n" + "</configuration>\n";

	private String hdfsSiteFileLocationTemplate = "{location}/etc/hadoop/hdfs-site.xml";
	private String hdfsSiteFileContentTemplate = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
			+ "<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n" + "<!--\n"
			+ "  Licensed under the Apache License, Version 2.0 (the \"License\");\n"
			+ "  you may not use this file except in compliance with the License.\n"
			+ "  You may obtain a copy of the License at\n" + "\n" + "    http://www.apache.org/licenses/LICENSE-2.0\n"
			+ "\n" + "  Unless required by applicable law or agreed to in writing, software\n"
			+ "  distributed under the License is distributed on an \"AS IS\" BASIS,\n"
			+ "  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
			+ "  See the License for the specific language governing permissions and\n"
			+ "  limitations under the License. See accompanying LICENSE file.\n" + "-->\n" + "\n"
			+ "<!-- Put site-specific property overrides in this file. -->\n" + "\n" + "<configuration>\n"
			+ "    <property>\n" + "        <name>dfs.namenode.name.dir</name>\n"
			+ "        <value>file:{location}/hdfs/name</value>\n" + "    </property>\n" + "    <property>\n"
			+ "        <name>dfs.datanode.data.dir</name>\n" + "        <value>file:{location}/hdfs/data</value>\n"
			+ "    </property>\n" + "    <property>\n" + "        <name>dfs.replication</name>\n"
			+ "        <value>2</value>\n" + "    </property>\n" + "    <property>\n"
			+ "        <name>dfs.namenode.secondary.http-address</name>\n" + "        <value>{master}:9001</value>\n"
			+ "    </property>\n" + "    <property>\n" + "        <name>dfs.webhdfs.enabled</name>\n"
			+ "        <value>true</value>\n" + "    </property>\n" + "</configuration>\n";

	public boolean deployHadoopCluster(String location, String masterIp, List<String> slaveIpList) {
		String coreSiteFileLocation = this.coreSiteFileLocationTemplate.replace("{master}", masterIp)
				.replace("{location}", location);
		String coreSiteFileContent = this.coreSiteFileContentTemplate.replace("{master}", masterIp)
				.replace("{location}", location);
		this.getAgentHelper().upload(masterIp, coreSiteFileLocation, coreSiteFileContent);
		for (String slaveIp : slaveIpList) {
			this.getAgentHelper().upload(slaveIp, coreSiteFileLocation, coreSiteFileContent);
		}

		String hdfsSiteFileLocation = this.hdfsSiteFileLocationTemplate.replace("{master}", masterIp)
				.replace("{location}", location);
		String hdfsSiteFileContent = this.hdfsSiteFileContentTemplate.replace("{master}", masterIp)
				.replace("{location}", location);
		this.getAgentHelper().upload(masterIp, hdfsSiteFileLocation, hdfsSiteFileContent);
		for (String slaveIp : slaveIpList) {
			this.getAgentHelper().upload(slaveIp, hdfsSiteFileLocation, hdfsSiteFileContent);
		}
		return true;
	}
}
