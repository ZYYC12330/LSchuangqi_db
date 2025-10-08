// Function to select the best material for each demand based on occurrences
function main(data) {

  function countMaterialOccurrences(data) {
    const materialCount = {};
    data.forEach(result => {
      result.matched_board.forEach(item => {
        const id = item.id;
        if (materialCount[id]) {
          materialCount[id].count++;
          materialCount[id].original.push(item.original);
          materialCount[id].details.push({
            original: item.original,
            description: item['description '] || item.description,
            reason: item.reason
          });
        } else {
          materialCount[id] = {
            count: 1,
            price: parsePrice(item.price_cny),
            original: [item.original],
            details: [{
              original: item.original,
              description: item['description '] || item.description,
              reason: item.reason
            }]
          };
        }
      });
    });
    return materialCount;
  }


  function parsePrice(price) {
    if (typeof price === 'string') {
      return parseFloat(price.replace('￥', '').trim()) || 0;
    }
    return price || 0;
    }


  
  const yy = data.rr;
  const materialCount = countMaterialOccurrences(yy);
  const result = [];
  const usedDemands = new Set();

  // 贪心算法：优先选择覆盖最多需求的板卡
  const sortedMaterials = Object.entries(materialCount).sort((a, b) => {
    if (b[1].count !== a[1].count) {
      return b[1].count - a[1].count; // 按覆盖需求数量降序
    }
    return a[1].price - b[1].price; // 如果数量相同，按价格升序
  });

  for (const [id, info] of sortedMaterials) {
    // 检查该板卡是否覆盖了未满足的需求
    const newOriginals = info.original.filter(d => !usedDemands.has(d));
    if (newOriginals.length > 0) {
      result.push({
        id: id,
        Price_CNY: info.price,
        details: info.details.map(detail => ({
          Original: detail.original,
          Description: detail.description,
          Reason: detail.reason
        }))
      });
      info.original.forEach(d => usedDemands.add(d));
    }
  }

  return result;
}