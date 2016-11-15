// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/12

package once.cloud.deploy.agent.helper;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import org.springframework.stereotype.Component;

@Component
public class ProcessHelper {
	public CommandResult run(String commandLine) {
		try {
			final Process process = Runtime.getRuntime().exec(new String[] { "/bin/sh", "-c", commandLine });
			final StringBuilder standardOutput = new StringBuilder();
			final StringBuilder standardError = new StringBuilder();
			Thread readStandardOutput = new Thread() {
				public void run() {
					try {
						BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
						int c = -1;
						try {
							while ((c = reader.read()) != -1) {
								standardError.append((char) c);
							}
						} finally {
							reader.close();
						}
					} catch (Exception e) {
						e.printStackTrace();
					}
				}
			};
			Thread readStandardError = new Thread() {
				public void run() {
					try {
						BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
						int c = -1;
						try {
							while ((c = reader.read()) != -1) {
								standardError.append((char) c);
							}
						} finally {
							reader.close();
						}
					} catch (Exception e) {
						e.printStackTrace();
					}
				}
			};
			readStandardOutput.start();
			readStandardError.start();
			int exitValue = process.waitFor();
			readStandardOutput.join();
			readStandardError.join();
			return new CommandResult(exitValue, standardOutput.toString(), standardError.toString());
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
}
