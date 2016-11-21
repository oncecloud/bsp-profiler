// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/21

package once.cloud.deploy.host.helper;

import java.nio.charset.Charset;
import java.util.Map;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;
import org.springframework.stereotype.Component;

@Component
public class HttpHelper {
	public String post(String url, Map<String, String> headers) {
		try {
			HttpClient httpClient = HttpClientBuilder.create().build();
			HttpPost httpPost = new HttpPost(url);
			for (String name : headers.keySet()) {
				httpPost.setHeader(name, headers.get(name));
			}
			HttpResponse httpResponse = httpClient.execute(httpPost);
			HttpEntity httpEntity = httpResponse.getEntity();
			String body = EntityUtils.toString(httpEntity, Charset.forName("utf-8"));
			EntityUtils.consume(httpEntity);
			return body;
		} catch (Exception exception) {
			exception.printStackTrace();
			return null;
		}
	}

	public String postJson(String url, String requestBody) {
		try {
			HttpClient httpClient = HttpClientBuilder.create().build();
			HttpPost httpPost = new HttpPost(url);
			StringEntity entity = new StringEntity(requestBody, ContentType.APPLICATION_JSON);
			httpPost.setEntity(entity);
			HttpResponse httpResponse = httpClient.execute(httpPost);
			HttpEntity httpEntity = httpResponse.getEntity();
			String body = EntityUtils.toString(httpEntity, Charset.forName("utf-8"));
			EntityUtils.consume(httpEntity);
			return body;
		} catch (Exception exception) {
			exception.printStackTrace();
			return null;
		}
	}
}
