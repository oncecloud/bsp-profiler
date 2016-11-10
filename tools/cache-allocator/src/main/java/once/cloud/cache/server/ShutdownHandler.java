// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.server;

public class ShutdownHandler extends Thread {
	private StandaloneServer standaloneServer;

	private StandaloneServer getStandaloneServer() {
		return standaloneServer;
	}

	private void setStandaloneServer(StandaloneServer standaloneServer) {
		this.standaloneServer = standaloneServer;
	}

	public ShutdownHandler(StandaloneServer standaloneServer) {
		this.setStandaloneServer(standaloneServer);
	}

	@Override
	public void run() {
		this.getStandaloneServer().stop();
	}
}
