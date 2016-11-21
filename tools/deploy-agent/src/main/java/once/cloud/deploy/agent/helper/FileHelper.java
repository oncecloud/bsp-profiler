// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/21

package once.cloud.deploy.agent.helper;

import java.io.File;
import java.io.FileWriter;

import org.springframework.stereotype.Component;

@Component
public class FileHelper {
	public boolean writeTextFile(String location, String content) {
		try {
			File file = new File(location);
			if (!file.exists()) {
				file.createNewFile();
			}
			FileWriter writer = new FileWriter(file);
			writer.write(content);
			writer.close();
			return true;
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
	}
}
