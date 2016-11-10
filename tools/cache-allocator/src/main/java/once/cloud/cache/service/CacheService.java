// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.service;

import java.util.Scanner;
import java.util.UUID;

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
		LOGGER.trace("createCache(): enter function.");
		LOGGER.trace("createCache(): name={}, size={}, cacheImageFile={}, disk image file={}.", name, size,
				cacheImageFile, diskImageFile);

		boolean result = true;

		try {
			LOGGER.trace("createCache(): get next available loop device for target image.");
			String targetDevice = this.nextAvailableLoopDevice();
			if (targetDevice == null) {
				LOGGER.warn("createCache(): fail to get next available loop device.");
				return (result = false);
			}
			LOGGER.trace("createCache(): next available loop device is {}.", targetDevice);

			LOGGER.trace("createCache(): attach image file \"{}\" to loop device \"{}\".", diskImageFile, targetDevice);
			result = result && this.attachImageToLoopDevice(diskImageFile, targetDevice);
			if (result == false) {
				LOGGER.warn("createCache(): fail to attach image file to loop device.");
				return (result = false);
			}

			LOGGER.trace("createCache(): create cache image file.");
			result = result && this.createCacheImage(cacheImageFile, size);
			if (result == false) {
				LOGGER.warn("createCache(): fail to create cache image file.");
				return (result = false);
			}

			LOGGER.trace("createCache(): get next available loop device for cache image.");
			String cacheDevice = this.nextAvailableLoopDevice();
			if (cacheDevice == null) {
				LOGGER.warn("createCache(): fail to get next available loop device.");
				return (result = false);
			}
			LOGGER.trace("createCache(): next available loop device is {}.", cacheDevice);

			LOGGER.trace("createCache(): attach cache \"{}\" to loop device \"{}\".", cacheImageFile, cacheDevice);
			result = result && this.attachImageToLoopDevice(cacheImageFile, cacheDevice);
			if (result == false) {
				LOGGER.warn("createCache(): fail to attach cache to loop device.");
				return (result = false);
			}

			LOGGER.trace("createCache(): configure cache: cache image file={}, cache size={}, target device={}.",
					cacheImageFile, size, targetDevice);
			result = result && this.configureCache(name, cacheDevice, targetDevice);
			if (result == false) {
				LOGGER.warn("createCache(): fail to configure cache.");
				return (result = false);
			}
			return result;
		} finally {
			LOGGER.trace("createCache(): {}", result);
			LOGGER.trace("createCache(): exit function.");
		}
	}

	private String nextAvailableLoopDevice() {
		String commandLine = "losetup --find";
		LOGGER.trace("nextAvailableLoopDevice(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		String result = commandResult.getStandardError().trim();
		LOGGER.trace("nextAvailableLoopDevice(): command returns: {}", result);
		return result;
	}

	private boolean attachImageToLoopDevice(String imageFileName, String loopDevice) {
		LOGGER.trace("attachImageToLoopDevice(): file name={}, loop device={}", imageFileName, loopDevice);
		String commandLine = "losetup " + loopDevice + " " + imageFileName;
		LOGGER.trace("attachImageToLoopDevice(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		int exitValue = commandResult.getExitValue();
		boolean result = commandResult.getExitValue() == 0;
		LOGGER.trace("attachImageToLoopDevice(): exit value {}", exitValue);
		return result;
	}

	private boolean createCacheImage(String cacheImageFile, int cacheSize) {
		String commandLine = "dd if=/dev/zero of=" + cacheImageFile + " bs=1M count=1 seek=" + (cacheSize - 1);
		LOGGER.trace("createCacheImage(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		return commandResult.getExitValue() == 0;
	}

	private boolean configureCache(String name, String cacheDevice, String targetDevice) {
		long totalCacheBlockSize = this.getBlockDeviceSize(cacheDevice);
		long reservedSize = (long) Math
				.ceil((4 * 1024 * 1024 + ((16 * 512 * totalCacheBlockSize) / (256 * 1024))) / 512.0);
		this.configureMetadataDevice(name, cacheDevice, reservedSize);
		String cacheMetadataDevice = this.getCacheMetadataDevice(name);
		this.cleanUpDevice(cacheMetadataDevice);
		long cacheSize = totalCacheBlockSize - reservedSize;
		this.configureCacheDevice(name, cacheDevice, cacheSize, reservedSize);
		long toCacheBlockSize = this.getBlockDeviceSize(targetDevice);
		boolean result = this.applyCacheConfiguration(name, targetDevice, toCacheBlockSize);
		return result;
	}

	private long getBlockDeviceSize(String device) {
		String commandLine = "blockdev --getsize " + device;
		LOGGER.trace("getBlockDeviceSize(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		return Long.parseLong(commandResult.getStandardError().trim());
	}

	private boolean configureMetadataDevice(String name, String cacheDevice, long size) {
		String commandLine = "dmsetup create metadata-" + name + " --table '0 " + size + " linear " + cacheDevice
				+ " 0'";
		LOGGER.trace("configureMetadataDevice(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		return commandResult.getExitValue() == 0;
	}

	private String getCacheMetadataDevice(String name) {
		return "/dev/mapper/metadata-" + name;
	}

	private boolean cleanUpDevice(String device) {
		String commandLine = "dd if=/dev/zero of=" + device;
		LOGGER.trace("cleanUpDevice(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		return commandResult.getExitValue() == 0;
	}

	private boolean configureCacheDevice(String name, String cacheDevice, long cacheSize, long reservedSize) {
		String commandLine = "dmsetup create cache-" + name + " --table '0 " + cacheSize + " linear " + cacheDevice
				+ " " + reservedSize + "'";
		LOGGER.trace("configureCacheDevice(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		return commandResult.getExitValue() == 0;
	}

	private boolean applyCacheConfiguration(String name, String targetDevice, long toCacheBlockSize) {
		String cacheMetadataDevice = this.getCacheMetadataDevice(name);
		String cacheDevice = this.getCacheDevice(name);
		String commandLine = "dmsetup create cached-" + name + " --table '0 " + toCacheBlockSize + " cache "
				+ cacheMetadataDevice + " " + cacheDevice + " " + targetDevice + " 512 1 writeback default 0'";
		LOGGER.trace("applyCacheConfiguration(): command line: {}", commandLine);
		CommandResult commandResult = this.getProcessHelper().run(commandLine);
		return commandResult.getExitValue() == 0;
	}

	private String getCacheDevice(String name) {
		return "/dev/mapper/cache-" + name;
	}

	public boolean removeCache(String name, String cacheImageFile, String diskImageFile) {
		// TODO Auto-generated method stub
		return false;
	}
}
