// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/21

package once.cloud.deploy.host.helper;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class AgentHelper {
	private static final int PORT = 10012;
	private HttpHelper httpHelper;
	private ObjectMapper objectMapper;

	private HttpHelper getHttpHelper() {
		return httpHelper;
	}

	@Autowired
	private void setHttpHelper(HttpHelper httpHelper) {
		this.httpHelper = httpHelper;
	}

	private ObjectMapper getObjectMapper() {
		return objectMapper;
	}

	@Autowired
	private void setObjectMapper(ObjectMapper objectMapper) {
		this.objectMapper = objectMapper;
	}

	public boolean upload(String ip, String location, String content) {
		try {
			String url = "http://" + ip + ":" + AgentHelper.PORT + "/Api/Agent/Upload";
			UploadInfo uploadInfo = new UploadInfo();
			uploadInfo.setContent(content);
			uploadInfo.setLocation(location);
			String requestBody = this.getObjectMapper().writeValueAsString(uploadInfo);
			String ret = this.getHttpHelper().postJson(url, requestBody);
			return this.getObjectMapper().readValue(ret, Boolean.class);
		} catch (Exception exception) {
			exception.printStackTrace();
			return false;
		}
	}

	public CommandResult run(String ip, String command) {
		try {
			String url = "http://" + ip + ":" + AgentHelper.PORT + "/Api/Agent/Run";
			Map<String, String> headers = new HashMap<String, String>();
			headers.put("x-ocme-agent-command", command);
			String ret = this.getHttpHelper().post(url, headers);
			return this.getObjectMapper().readValue(ret, CommandResult.class);
		} catch (Exception exception) {
			exception.printStackTrace();
			return null;
		}
	}
}
