// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.api.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import once.cloud.cache.api.model.CacheStatusModel;
import once.cloud.cache.entity.CacheStatus;
import once.cloud.cache.service.CacheService;

@Controller
public class CacheController {
	private static Logger LOGGER = LoggerFactory.getLogger(CacheController.class);
	private CacheService cacheService;

	private CacheService getCacheService() {
		return cacheService;
	}

	@Autowired
	private void setCacheService(CacheService cacheService) {
		this.cacheService = cacheService;
	}

	@RequestMapping(value = "/Api/Cache/{name}", method = { RequestMethod.GET })
	@ResponseBody
	public CacheStatusModel getCacheStatus(@PathVariable("name") String name) {
		LOGGER.trace("getCacheStatus(): enter function.");
		LOGGER.trace("getCacheStatus(): cache name={}", name);

		try {
			CacheStatus status = this.getCacheService().getCacheStatus(name);
			if (status == null) {
				LOGGER.warn("getCacheStatus(): fail to get cache status. (cache name={})", name);
				return null;
			}

			CacheStatusModel result = new CacheStatusModel();
			result.setStart(status.getStart());
			result.setEnd(status.getEnd());
			result.setPolicy(status.getPolicy());
			result.setUsedMetadataBlocks(status.getUsedMetadataBlocks());
			result.setTotalMetadataBlocks(status.getTotalMetadataBlocks());
			result.setReadHits(status.getReadHits());
			result.setReadMisses(status.getReadMisses());
			result.setWriteHits(status.getWriteHits());
			result.setWriteMisses(status.getWriteMisses());
			result.setDemotions(status.getDemotions());
			result.setPromotions(status.getPromotions());
			result.setBlocksInCache(status.getBlocksInCache());
			result.setDirty(status.getDirty());
			result.getFeatureList().addAll(status.getFeatureList());
			result.getCoreArgumentList().putAll(status.getCoreArgumentList());
			result.getPolicyArgumentList().putAll(status.getPolicyArgumentList());
			return result;
		} catch (Exception exception) {
			exception.printStackTrace();
			LOGGER.warn("getCacheStatus(): exception caught: {}", exception.getMessage());
			return null;
		} finally {
			LOGGER.trace("getCacheStatus(): exit function.");
		}
	}

	@RequestMapping(value = "/Api/Cache/{name}", method = { RequestMethod.POST })
	@ResponseBody
	public boolean createCache(@PathVariable("name") String name, @RequestHeader("x-ocme-cache-size") int size,
			@RequestHeader("x-ocme-cache-cache-image-file") String cacheImageFile,
			@RequestHeader("x-ocme-cache-disk-image-file") String diskImageFile) {
		LOGGER.trace("createCache(): enter function.");
		LOGGER.trace("createCache(): name={}, size={}, cache image file=[], disk image file={}.", name, size,
				cacheImageFile, diskImageFile);

		boolean result = true;

		try {
			result = this.getCacheService().createCache(name, size, cacheImageFile, diskImageFile);
			if (result == false) {
				LOGGER.warn(
						"createCache(): fail to create cache. (name={}, size={}, cache image file=[], disk image file={})",
						name, size, cacheImageFile, diskImageFile);
			}
			return result;
		} catch (Exception exception) {
			exception.printStackTrace();
			LOGGER.warn("createCache(): exception caught: {}", exception.getMessage());
			return (result = false);
		} finally {
			LOGGER.trace("createCache(): {}", result);
			LOGGER.trace("createCache(): exit function.");
		}
	}

	@RequestMapping(value = "/Api/Cache/{name}", method = { RequestMethod.DELETE })
	@ResponseBody
	public boolean removeCache(@PathVariable("name") String name,
			@RequestHeader("x-ocme-cache-cache-image-file") String cacheImageFile,
			@RequestHeader("x-ocme-cache-disk-image-file") String diskImageFile) {
		LOGGER.trace("removeCache(): enter function.");
		LOGGER.trace("removeCache(): name={}, cache image file={}, disk image file={}.", name, cacheImageFile,
				diskImageFile);

		boolean result = true;

		try {
			result = this.getCacheService().removeCache(name, cacheImageFile, diskImageFile);
			if (result == false) {
				LOGGER.warn("removeCache(): fail to remove cache. (name={}, cache image file={}, disk image file={}",
						name, cacheImageFile, diskImageFile);
			}
			return result;
		} catch (Exception exception) {
			exception.printStackTrace();
			LOGGER.warn("removeCache(): exception caught: {}", exception.getMessage());
			return (result = false);
		} finally {
			LOGGER.trace("removeCache(): {}", result);
			LOGGER.trace("removeCache(): exit function.");
		}
	}
}
