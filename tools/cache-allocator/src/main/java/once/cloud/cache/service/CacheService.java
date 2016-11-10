// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import once.cloud.cache.entity.CacheStatus;
import once.cloud.cache.helper.ProcessHelper;

@Component
public class CacheService {
	private static final Logger LOGGER = LoggerFactory.getLogger(CacheService.class);
	private ProcessHelper processHelper;

	private ProcessHelper getProcessHelper() {
		return processHelper;
	}

	@Autowired
	private void setProcessHelper(ProcessHelper processHelper) {
		this.processHelper = processHelper;
	}

	public CacheStatus getCacheStatus(String name) {
		// TODO Auto-generated method stub
		return null;
	}

	public boolean createCache(String name, int size, String cacheImageFile, String diskImageFile) {
		// TODO Auto-generated method stub
		return false;
	}

	public boolean removeCache(String name, String cacheImageFile, String diskImageFile) {
		// TODO Auto-generated method stub
		return false;
	}
}
