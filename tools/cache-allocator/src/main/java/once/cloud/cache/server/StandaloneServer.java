// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.server;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.webapp.WebAppContext;

public class StandaloneServer {
	private Server server;
	private int port;

	private Server getServer() {
		return server;
	}

	private void setServer(Server server) {
		this.server = server;
	}

	private int getPort() {
		return port;
	}

	private void setPort(int port) {
		this.port = port;
	}

	public StandaloneServer(int port) {
		this.setPort(port);
	}

	private String getWebXmlLocation() {
		return Thread.currentThread().getContextClassLoader()
				.getResource("webapp/WEB-INF/web.xml").toString();
	}

	private String getResourceBase() {
		return Thread.currentThread().getContextClassLoader()
				.getResource("webapp/").toString();
	}

	public boolean start() {
		try {
			this.setServer(new Server(this.getPort()));
			WebAppContext webAppContext = new WebAppContext();
			webAppContext.setContextPath("/");
			webAppContext.setDescriptor(this.getWebXmlLocation());
			webAppContext.setResourceBase(this.getResourceBase());
			this.getServer().setHandler(webAppContext);
			this.getServer().start();
			return true;
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
	}

	public boolean stop() {
		try {
			if (this.getServer() != null) {
				this.getServer().stop();
			}
			return true;
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		} finally {
			this.setServer(null);
		}
	}

}
