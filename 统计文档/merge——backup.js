async function main(data) {
  const cc = data.yy;

  // 创建一个 Map 来存储每个 id 对应的对象
  const idToProperties = new Map();

  cc.forEach(group => {
    // 确保 group.kkrr 存在并且是一个数组
    if (group.kkrr && Array.isArray(group.kkrr)) {
      group.kkrr.forEach(item => {
        const { id, ...properties } = item; // 分离 id 和其他属性
        if (!idToProperties.has(id)) {
          idToProperties.set(id, { id, properties: [] });
        }
        idToProperties.get(id).properties.push(properties);
      });
    }
  });

  // 将 Map 转换为数组
  const raw_data = Array.from(idToProperties.values()).map(entry => ({
    id: entry.id,
    properties: entry.properties.reduce((acc, prop) => {
      Object.keys(prop).forEach(key => {
        if (!acc[key]) acc[key] = [];
        acc[key].push(prop[key]);
      });
      return acc;
    }, {})
  })).map(entry => ({
    id: entry.id,
    properties: Object.entries(entry.properties)
      .sort((a, b) => b[1].length - a[1].length) // 按数组长度降序排序
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {}) // 将排序后的结果转换回对象
  })).sort((a, b) => Object.keys(b.properties).length - Object.keys(a.properties).length); // 根据 properties 对象的元素个数降序排序

  // 找出四项属性都完全匹配且都有值的 id
  const prefect_matched_id = raw_data.filter(entry => {
    const keys = Object.keys(entry.properties);
    return keys.length === 4 && keys.every(key => entry.properties[key].every(value => value !== null && value !== undefined));
  }).map(entry => entry.id);


  // 此处可修改！！！
  // 如果 prefect_matched_id 为空，则取 raw_data 中前三个 id 作为备用结果
  const final_matched_id = prefect_matched_id.length > 0 ? prefect_matched_id : raw_data.slice(0, 3).map(entry => entry.id);

  return { raw_data, final_matched_id };
}