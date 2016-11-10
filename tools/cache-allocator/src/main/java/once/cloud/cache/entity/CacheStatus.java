// ===============================================================
// Copyright(c) Institute of Software, Chinese Academy of Sciences
// ===============================================================
// Author : Zhen Tang <tangzhen12@otcaix.iscas.ac.cn>
// Date   : 2016/11/10

package once.cloud.cache.entity;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class CacheStatus {
	private long start;
	private long end;
	private String policy;
	private long usedMetadataBlocks;
	private long totalMetadataBlocks;
	private long readHits;
	private long readMisses;
	private long writeHits;
	private long writeMisses;
	private long demotions;
	private long promotions;
	private long blocksInCache;
	private long dirty;
	private List<String> featureList;
	private Map<String, String> coreArgumentList;
	private Map<String, String> policyArgumentList;

	public long getStart() {
		return start;
	}

	public void setStart(long start) {
		this.start = start;
	}

	public long getEnd() {
		return end;
	}

	public void setEnd(long end) {
		this.end = end;
	}

	public String getPolicy() {
		return policy;
	}

	public void setPolicy(String policy) {
		this.policy = policy;
	}

	public long getUsedMetadataBlocks() {
		return usedMetadataBlocks;
	}

	public void setUsedMetadataBlocks(long usedMetadataBlocks) {
		this.usedMetadataBlocks = usedMetadataBlocks;
	}

	public long getTotalMetadataBlocks() {
		return totalMetadataBlocks;
	}

	public void setTotalMetadataBlocks(long totalMetadataBlocks) {
		this.totalMetadataBlocks = totalMetadataBlocks;
	}

	public long getReadHits() {
		return readHits;
	}

	public void setReadHits(long readHits) {
		this.readHits = readHits;
	}

	public long getReadMisses() {
		return readMisses;
	}

	public void setReadMisses(long readMisses) {
		this.readMisses = readMisses;
	}

	public long getWriteHits() {
		return writeHits;
	}

	public void setWriteHits(long writeHits) {
		this.writeHits = writeHits;
	}

	public long getWriteMisses() {
		return writeMisses;
	}

	public void setWriteMisses(long writeMisses) {
		this.writeMisses = writeMisses;
	}

	public long getDemotions() {
		return demotions;
	}

	public void setDemotions(long demotions) {
		this.demotions = demotions;
	}

	public long getPromotions() {
		return promotions;
	}

	public void setPromotions(long promotions) {
		this.promotions = promotions;
	}

	public long getBlocksInCache() {
		return blocksInCache;
	}

	public void setBlocksInCache(long blocksInCache) {
		this.blocksInCache = blocksInCache;
	}

	public long getDirty() {
		return dirty;
	}

	public void setDirty(long dirty) {
		this.dirty = dirty;
	}

	public List<String> getFeatureList() {
		return featureList;
	}

	public void setFeatureList(List<String> featureList) {
		this.featureList = featureList;
	}

	public Map<String, String> getCoreArgumentList() {
		return coreArgumentList;
	}

	public void setCoreArgumentList(Map<String, String> coreArgumentList) {
		this.coreArgumentList = coreArgumentList;
	}

	public Map<String, String> getPolicyArgumentList() {
		return policyArgumentList;
	}

	public void setPolicyArgumentList(Map<String, String> policyArgumentList) {
		this.policyArgumentList = policyArgumentList;
	}

	public CacheStatus() {
		this.setFeatureList(new LinkedList<String>());
		this.setCoreArgumentList(new HashMap<String, String>());
		this.setPolicyArgumentList(new HashMap<String, String>());
	}
}
