
function main(data) {
    const dd = data.yy
    const merged = {};
    const categories = ['CPU', 'Hard Disk', 'Memory', 'Slots'];
  
    dd.forEach((result, index) => {
      if (result.kkrr) {
        result.kkrr.forEach(item => {
          const { id, reason, original, score, ...rest } = item;
          if (!merged[id]) {
            merged[id] = {
              id,
              details: [],
              total_score: 0
            };
          }
  
          const category = categories[index] || 'Unknown';
          const detail = {
            category,
            score: typeof score === 'boolean' ? (score ? 1 : 0) : parseFloat(score),
            reason,
            original
          };
  
          Object.keys(rest).forEach(key => {
            if (key !== 'id' && key !== 'reason' && key !== 'original' && key !== 'score') {
              detail[key] = rest[key];
            }
          });
  
          merged[id].details.push(detail);
          merged[id].total_score += typeof score === 'boolean' ? (score ? 1 : 0) : parseFloat(score);
        });
      }
    });
  
    Object.values(merged).forEach(item => {
      item.total_score = item.total_score || 0;
    });
  
    const goodMatch = Object.values(merged).filter(item => item.total_score > 2.4).sort((a, b) => b.total_score - a.total_score);
  
    return {
      MergedResults: Object.values(merged),  //  所有的结果
      GoodMatch: goodMatch  //  评分 60% 以上
    };
  }
  