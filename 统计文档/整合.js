function main(data) {
  // 将输入2转换为以original为键的映射，方便查找
  const input1 = data.Demands_top
  const input2 = data.Price_top
  const input3 = data.error_info

  const input2Map = {};
  input2.forEach(item => {
    if (item.original) {
      if (!input2Map[item.original]) {
        input2Map[item.original] = [];
      }
      input2Map[item.original].push(item);
    }
  });

  const result = [];

  // 遍历输入1的每个对象
  input1.forEach(demand => {
    // 处理没有details字段的情况（只有original和reason）
    if (!demand.details) {
      result.push({
        id: demand.id || "",
        original: demand.original,
        reason: demand.reason
      });
      return; // 跳过当前循环
    }

    // 如果details数组长度大于1，则需要比较价格
    if (demand.details.length > 1) {
      let input1Total = 0;
      let input2Total = 0;
      let hasInput2Match = true;

      // 计算输入1中该对象所有detail的总价
      input1Total = demand.total_amount_cny;

      // 计算输入2中对应original的总价
      for (const detail of demand.details) {
        const matches = input2Map[detail.original];
        if (matches && matches.length > 0) {
          // 如果有多个匹配项，取第一个
          input2Total += parseFloat(matches[0].total_amount_cny.replace('￥', ''));
        } else {
          hasInput2Match = false;
          break;
        }
      }

      // 如果输入2中有所有匹配项，则比较价格
      if (hasInput2Match) {
        if (input1Total <= input2Total) {
          // 输入1更便宜或相等，使用输入1的数据
          result.push({
            id: demand.id,
            price_cny: demand.price_cny,
            quantity: demand.quantity,
            total_amount_cny: demand.total_amount_cny,
            details: demand.details
          });
        } else {
          // 输入2更便宜，使用输入2的数据
          demand.details.forEach(detail => {
            const matches = input2Map[detail.original];
            if (matches && matches.length > 0) {
              result.push({
                id: matches[0].id,
                quantity: matches[0].quantity,
                reason: matches[0].reason,
                price_cny: parseFloat(matches[0].price_cny.replace('￥', '')),
                description: matches[0].description,
                match_degree: matches[0].match_degree,
                original: matches[0].original,
                total_amount_cny: parseFloat(matches[0].total_amount_cny.replace('￥', ''))
              });
            }
          });
        }
      } else {
        // 输入2没有完全匹配，使用输入1的数据
        result.push({
          id: demand.id,
          price_cny: demand.price_cny,
          quantity: demand.quantity,
          total_amount_cny: demand.total_amount_cny,
          details: demand.details
        });
      }
    } else {
      // 如果details数组长度不大于1，直接添加到结果中
      result.push({
        id: demand.id,
        price_cny: demand.price_cny,
        quantity: demand.quantity,
        total_amount_cny: demand.total_amount_cny,
        details: demand.details
      });
    }
  });

  // 处理错误信息
  if (input3 && Array.isArray(input3)) {
    input3.forEach(errorItem => {
      result.push({
        type: "error",
        original: errorItem.original,
        reason: errorItem.reason
      });
    });
  }

  return {result:result};
}