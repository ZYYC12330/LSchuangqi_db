/**
 * 主函数：根据匹配结果选择最优材料（基于覆盖需求数量和价格）
 * @param {Object} data - 输入数据，包含 rr 字段（即匹配结果数组）
 * @returns {Object} 返回最优材料列表，字段为 Demands_top_price
 */
function main(data) {
    const results = Array.isArray(data?.rr) ? data.rr : [];
  
    // 步骤1：统计每个材料在所有匹配中的出现情况
    const materialStats = countMaterialOccurrences(results);
  
    // 步骤2：排序 —— 先按覆盖需求数量降序，再按总价升序（便宜优先）
    const sortedMaterials = Object.entries(materialStats)
      .sort((a, b) => {
        if (b[1].count !== a[1].count) {
          return b[1].count - a[1].count; // 覆盖越多越靠前
        }
        return a[1].total_amount_cny - b[1].total_amount_cny; // 总价越低越靠前
      });
  
    // 步骤3：去重处理 —— 每个需求只被选一次
    const usedDemands = new Set();
    const selectedMaterials = [];
  
    // 新增：收集未匹配的需求
    const unmatchedDemands = [];
    
    for (const result of results) {
      const matchedBoard = result.matched_board;
      if (!Array.isArray(matchedBoard)) continue;
      
      // 检查是否有未匹配的条目
      const hasUnmatched = matchedBoard.some(item => 
        item.reason === "未找到相关功能板卡"
      );
      
      if (hasUnmatched) {
        // 收集所有未匹配的需求
        const unmatchedItems = matchedBoard.filter(item => 
          item.reason === "未找到相关功能板卡"
        );
        
        unmatchedItems.forEach(item => {
          unmatchedDemands.push({
            original: item.original,
            reason: item.reason
          });
        });
      }
    }

    for (const [materialId, stats] of sortedMaterials) {
      const unusedOriginals = stats.original.filter(original => !usedDemands.has(original));
  
      if (unusedOriginals.length === 0) continue;
  
      selectedMaterials.push({
        id: materialId,
        price_cny: stats.price,
        quantity: stats.quantity,
        total_amount_cny: stats.total_amount_cny,
        details: stats.details.map(detail => ({
          original: detail.original,
          reason: detail.reason
        }))
      });
  
      // 标记这些需求已被使用
      unusedOriginals.forEach(original => usedDemands.add(original));
    }
  
    return { 
      Demands_top: selectedMaterials.concat(unmatchedDemands)
    };
  }
  
  /**
   * 统计每个材料的出现频率、总金额、关联需求等信息
   * @param {Array} results - 匹配结果数组，每项有 matched_board 数组
   * @returns {Object} 材料统计对象，key: materialId, value: 统计信息
   */
  function countMaterialOccurrences(results) {
    const materialStats = {};
  
    for (const result of results) {
      const matchedBoard = result.matched_board;
      if (!Array.isArray(matchedBoard)) continue;
  
      for (const item of matchedBoard) {
        const id = item.id;
        if (!id) continue;
  
        if (!materialStats[id]) {
          materialStats[id] = {
            count: 0,
            price: parsePrice(item.price_cny),
            quantity: item.quantity, 
            total_amount_cny: parseAmount(item.total_amount_cny), // 单次价格
            original: [],
            details: []
          };
        }
  
        // 如果这个需求还没记录过，则添加
        const original = item.original;
        if (!materialStats[id].original.includes(original)) {
          materialStats[id].original.push(original);
          materialStats[id].details.push({
            original,
            reason: item.reason || ''
          });
        }
  
        // 增加覆盖需求数量（去重）
        materialStats[id].count++;
      }
    }
  
    return materialStats;
  }
  
  /**
   * 解析价格字符串（如 "￥123.45" 或 "260"）为数字
   * @param {string|number} price - 价格值
   * @returns {number} 数值形式的价格
   */
  function parsePrice(price) {
    if (typeof price === 'string') {
      return parseFloat(price.replace(/[^0-9.-]/g, '')) || 0;
    }
    return Number(price) || 0;
  }
  
  /**
   * 解析总金额字段（更安全地提取数值）
   * @param {string|number} amount - 总金额值
   * @returns {number} 数值形式的金额
   */
  function parseAmount(amount) {
    if (typeof amount === 'string') {
      return parseFloat(amount.replace(/[^0-9.-]/g, '')) || 0;
    }
    return Number(amount) || 0;
  }
  