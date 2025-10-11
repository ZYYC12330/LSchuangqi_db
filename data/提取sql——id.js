async function main(data) {
    const raw = data.raw;
  
    // 提取所有 id，并去重
    const allIds = new Set();
  
    raw.forEach(group => {
      if (Array.isArray(group.matched_board)) {
        group.matched_board.forEach(board => {
          if (board.id) {
            allIds.add(board.id);
          }
        });
      }
    });
    const allIdsString = `(${Array.from(allIds).map(id => `'${id}'`).join(', ')})`
  
    return {allIdsString:allIdsString}
  }