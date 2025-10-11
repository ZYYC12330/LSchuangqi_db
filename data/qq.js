async function main(data) {
    const matched_board = data.matched_board?.length > 0 
      ? data.matched_board 
      : [{"reason": "未找到相关功能板卡"}];
    const original = data.original;
  
    matched_board.forEach(item => {
      item.original = original;
      delete item.total_amount_cny; // 清除旧值，保证统一格式
  
      // 标准化 price_cny
      let priceStr = String(item.price_cny || "").trim();
      if (!priceStr) {
        return;
      }
  
      // 提取数字部分（支持小数）
      const priceMatch = priceStr.match(/(\d+(\.\d+)?)$/);
      const price = priceMatch ? parseFloat(priceMatch[1]) : 0;
      item.price_cny = price; // 设置为 number

      const quantity = item.quantity || 1;

      // 计算总价并设置 total_amount_cny
      if (price > 0 && quantity > 0) {
        const total = quantity * price;
        item.total_amount_cny = parseFloat(total.toFixed(2));
      }
    });
  
    return { matched_board: matched_board };
  }
  