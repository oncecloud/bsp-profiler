// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/14

package once.cloud.deploy.agent.api.model;

public class CommandResultModel {
	private int exitValue;
	private String standardOutput;
	private String standardError;

	public int getExitValue() {
		return exitValue;
	}

	public void setExitValue(int exitValue) {
		this.exitValue = exitValue;
	}

	public String getStandardOutput() {
		return standardOutput;
	}

	public void setStandardOutput(String standardOutput) {
		this.standardOutput = standardOutput;
	}

	public String getStandardError() {
		return standardError;
	}

	public void setStandardError(String standardError) {
		this.standardError = standardError;
	}

}
