// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/12

package once.cloud.deploy.agent.helper;

public class CommandResult {
	private int exitValue;
	private String standardOutput;
	private String standardError;

	public int getExitValue() {
		return exitValue;
	}

	private void setExitValue(int exitValue) {
		this.exitValue = exitValue;
	}

	public String getStandardOutput() {
		return standardOutput;
	}

	private void setStandardOutput(String standardOutput) {
		this.standardOutput = standardOutput;
	}

	public String getStandardError() {
		return standardError;
	}

	private void setStandardError(String standardError) {
		this.standardError = standardError;
	}

	public CommandResult(int exitValue, String standardOutput, String standardError) {
		this.setExitValue(exitValue);
		this.setStandardOutput(standardOutput);
		this.setStandardError(standardError);
	}
}
