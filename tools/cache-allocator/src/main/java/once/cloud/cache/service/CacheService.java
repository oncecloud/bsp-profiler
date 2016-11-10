// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.service;

import java.util.Scanner;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import once.cloud.cache.entity.CacheStatus;
import once.cloud.cache.helper.CommandResult;
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
		String commandLine = "dmsetup status " + name;
		LOGGER.trace("getCacheStatus(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		String cacheStatus = commandResult.getStandardError().trim();
		LOGGER.trace("getCacheStatus(): cache status: {}", cacheStatus);
		return this.parseCacheStatus(cacheStatus);
	}

	private CacheStatus parseCacheStatus(String cacheStatus) {
		int i;
		Scanner scanner = null;

		try {
			scanner = new Scanner(cacheStatus);
			CacheStatus status = new CacheStatus();
			long start = scanner.nextLong();
			status.setStart(start);

			long end = scanner.nextLong();
			status.setEnd(end);

			String policy = scanner.next();
			status.setPolicy(policy);

			String next = scanner.next();

			long usedMetadataBlocks = Long.parseLong(next.substring(0, next.indexOf('/')));
			status.setUsedMetadataBlocks(usedMetadataBlocks);

			long totalMetadataBlocks = Long.parseLong(next.substring(next.indexOf('/') + 1));
			status.setTotalMetadataBlocks(totalMetadataBlocks);

			long readHits = scanner.nextLong();
			status.setReadHits(readHits);

			long readMisses = scanner.nextLong();
			status.setReadMisses(readMisses);

			long writeHits = scanner.nextLong();
			status.setWriteHits(writeHits);

			long writeMisses = scanner.nextLong();
			status.setWriteMisses(writeMisses);

			long demotions = scanner.nextLong();
			status.setDemotions(demotions);

			long promotions = scanner.nextLong();
			status.setPromotions(promotions);

			long blocksInCache = scanner.nextLong();
			status.setBlocksInCache(blocksInCache);

			long dirty = scanner.nextLong();
			status.setDirty(dirty);

			LOGGER.trace(
					"parseCacheStatus(): " + "start={}, " + "end={}, " + "policy={}, " + "used metadata blocks={}, "
							+ "total metadata blocks={}, " + "read hits={}, " + "read misses={}, " + "write hits={}, "
							+ "write misses={}, " + "demotions={}, " + "promotions={}, " + "blocks in cache={}, "
							+ "dirty={}",
					start, end, policy, usedMetadataBlocks, totalMetadataBlocks, readHits, readMisses, writeHits,
					writeMisses, demotions, promotions, blocksInCache, dirty);

			int features = scanner.nextInt();
			LOGGER.trace("parseCacheStatus(): features count: {}", features);
			for (i = 0; i < features; i++) {
				String feature = scanner.next();
				LOGGER.trace("parseCacheStatus(): features: {}", feature);
				status.getFeatureList().add(feature);
			}

			int coreArguments = scanner.nextInt();
			LOGGER.trace("parseCacheStatus(): core arguments: {}", coreArguments);
			for (i = 0; i < coreArguments / 2; i++) {
				String key = scanner.next();
				String value = scanner.next();
				LOGGER.trace("parseCacheStatus(): core argument: key={}, value={}", key, value);
				status.getCoreArgumentList().put(key, value);
			}

			int policyArguments = scanner.nextInt();
			LOGGER.trace("parseCacheStatus(): policy arguments: {}", policyArguments);
			for (i = 0; i < policyArguments / 2; i++) {
				String key = scanner.next();
				String value = scanner.next();
				LOGGER.trace("parseCacheStatus(): policy argument: key={}, value={}", key, value);
				status.getPolicyArgumentList().put(key, value);
			}

			return status;
		} finally {
			if (scanner != null) {
				scanner.close();
			}
		}
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
