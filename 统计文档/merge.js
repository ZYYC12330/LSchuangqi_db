/**
 * 主函数：根据匹配结果选择最优材料（基于覆盖需求数量和价格）
 * @param {Object} data - 输入数据，包含 rr 字段（即匹配结果数组）
 * @returns {Object} 返回最优材料列表，字段为 Demands_top_price
 */
function main(data) {
  const results = data.rr || [];

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

  for (const [materialId, stats] of sortedMaterials) {
    // 找出当前材料尚未被使用的原始需求
    const unusedOriginals = stats.original.filter(original => !usedDemands.has(original));
    
    if (unusedOriginals.length === 0) continue;

    // 添加到结果中
    selectedMaterials.push({
      id: materialId,
      price_cny: stats.total_amount_cny,
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

  return { Demands_top_price: selectedMaterials };
}

/**
 * 统计每个材料的出现频率、总金额、关联需求等信息
 * @param {Array} results - 匹配结果数组，每项有 matched_board 数组
 * @returns {Object} 材料统计对象，key: materialId, value: 统计信息
 */
function countMaterialOccurrences(results) {
  const materialStats = {};

  results.forEach(result => {
    if (!result.matched_board || !Array.isArray(result.matched_board)) return;

    result.matched_board.forEach(item => {
      const id = item.id;
      if (!id) return; // 跳过无ID项

      if (!materialStats[id]) {
        materialStats[id] = {
          count: 1,
          price: parsePrice(item.price), // 单价（用于参考）
          quantity: item.quantity || 0,
          total_amount_cny: parseFloat(item.total_amount_cny) || 0, // 总价（用于排序和输出）
          original: [item.original],
          details: [...]
        };

      }

      // 累加统计
      materialStats[id].count++;
      materialStats[id].quantity += item.quantity || 0;
      materialStats[id].total_amount_cny += parseFloat(item.total_amount_cny) || 0;
      materialStats[id].original.push(item.original);
      materialStats[id].details.push({
        original: item.original,
        reason: item.reason
      });
    });
  });

  return materialStats;
}

/**
 * 解析价格字符串（如 "￥123.45"）为数字
 * @param {string|number} price - 价格值
 * @returns {number} 数值形式的价格
 */
function parsePrice(price) {
  if (typeof price === 'string') {
    return parseFloat(price.replace('￥', '').trim()) || 0;
  }
  return price || 0;
}
