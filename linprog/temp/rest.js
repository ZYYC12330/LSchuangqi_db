async function main(data) {
    const unsatisfied_requirements = data.unsatisfied_requirements;
    const matched_boards = data.matched_boards; // ✅ 修正：原代码是 matched_board，应为 matched_boards（复数）
    const results_board = data.results_board;
  
    // 正则：匹配以 "_channel_count" 结尾的字段名
    const channelCountRegex = /_channel_count$/;
  
    // 遍历每个未满足的需求
    for (const requirement of unsatisfied_requirements) {
      const original = requirement.original;
  
      // 在匹配的板卡中查找与该需求原始描述最匹配的板卡
      let bestMatch = null;
      let highestMatchDegree = -1;
  
      for (const board of matched_boards) {
        if (board.original === original) {
          if (board.match_degree > highestMatchDegree) {
            highestMatchDegree = board.match_degree;
            bestMatch = board;
          }
        }
      }
  
      // ======== 统一处理：计算 quantity = ceil(需求通道数 / 最佳匹配板卡的通道数) ========
      let requirementValue = 0;
      let boardValue = 0; // ✅ 改为只取 bestMatch 的通道数

      // 1. 从 bestMatch 的 requirement_specification 中查找第一个匹配 _channel_count 的字段
      if (bestMatch && bestMatch.requirement_specification) {
        for (const [key, value] of Object.entries(bestMatch.requirement_specification)) {
          if (channelCountRegex.test(key) && typeof value.value === 'number' && value.value > 0) {
            requirementValue = value.value;
            break; // 只取第一个匹配的通道字段
          }
        }
      }
  
      // 2. 仅从 bestMatch 中获取 board_specification 的通道数（关键修改！）
      if (bestMatch && bestMatch.board_specification) {
        for (const [key, value] of Object.entries(bestMatch.board_specification)) {
          if (channelCountRegex.test(key) && typeof value.value === 'number' && value.value > 0) {
            boardValue = value.value;
            break; // 只取第一个匹配的通道字段（每个板卡通常只有一种通道类型）
          }
        }
      }
  
      // 3. 如果 board_specification 中没有通道数字段，尝试从描述中解析
      if (boardValue <= 0 && bestMatch && bestMatch.description) {
        // 尝试匹配 "X通道" 或 "X路" 的模式
        const channelMatch = bestMatch.description.match(/(\d+)[通道路]/);
        if (channelMatch) {
          boardValue = parseInt(channelMatch[1], 10);
        }
      }
  
      // 4. 避免除零或无效值：如果仍然找不到，使用需求值（这样至少需要1张板卡）
      if (boardValue <= 0) {
        boardValue = requirementValue > 0 ? requirementValue : 1;
      }
  
      // 5. 计算最少需要的板卡数量（向上取整）
      const quantity = Math.ceil(requirementValue / boardValue);
  
      // ======== 构造结果对象：无论是否匹配，都添加 quantity ========
      if (bestMatch) {
        // 匹配到板卡：提取字段，剔除不需要的，添加 status 和 quantity
        const { requirement_specification, board_specification, compliance, ...cleanBoard } = bestMatch;
        results_board.push({
          ...cleanBoard,
          status: "single_choice",
          quantity: quantity // ✅ 正确：基于 bestMatch 的通道数计算
        });
      } else {
        // 未找到匹配板卡
        const notFoundBoard = {
          original: original,
          description: "找不到相关板卡",
          status: "single_choice",
          quantity: quantity // ✅ 依然使用需求值 / 1（因为 boardValue=1）
        };
        results_board.push(notFoundBoard);
      }
    }
  
    return { 
    "results_board": results_board, 
    "matched_board": matched_boards 
  };
  }
  