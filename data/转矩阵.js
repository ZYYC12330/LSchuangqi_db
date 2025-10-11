async function main(data) {
    const inputArray = data.rawData; // 假设输入是数组，如题目所示
    const bad_cards = data.bad_cards;
    // 定义通道顺序（按你期望的 matrix 顺序）
    const channelOrder = [
      "analogInputChannels",
      "analogOutputChannels",
      "digitalInputChannels",
      "digitalOutputChannels",
      "digitalIOChannels",
      "serialPortChannels",
      "canBusChannels",
      "pwmOutputChannels",
      "encoderChannels",
      "ssiBusChannels",
      "spiBusChannels",
      "i2cBusChannels",
      "pcmLvdChannels",
      "bissCChannels",
      "afdxChannels",
      "ppsPulseChannels",
      "rtdResistanceChannels",
      "differentialInputChannels",
      "milStd1553BChannels",
      "timerCounterChannels",
      "relayOutputChannels"
    ];
  
    // 创建 bad_cards 的映射，方便快速查找
    const badCardsMap = new Map();
    if (bad_cards) {
      // 处理 bad_cards 可能是数组或对象的情况
      const cardsArray = Array.isArray(bad_cards) ? bad_cards : (bad_cards.cards || []);
      cardsArray.forEach(card => {
        if (card.id && card.not_satisfied) {
          badCardsMap.set(card.id, card.not_satisfied);
        }
      });
    }
  
    // 处理每个设备对象
    const result = inputArray.map(item => {
      // 创建 item 的副本，避免修改原始数据
      const processedItem = { ...item };
      
      // 检查该 id 是否在 bad_cards 中
      if (badCardsMap.has(item.id)) {
        const notSatisfiedFields = badCardsMap.get(item.id);
        // 将不满足的通道字段置为 null
        notSatisfiedFields.forEach(field => {
          processedItem[field] = null;
        });
      }
      
      // 构建 matrix 数组：按 channelOrder 顺序取值，null 替换为 0
      const matrix = channelOrder.map(key => {
        return processedItem[key] !== null ? processedItem[key] : 0;
      });
  
      // 构建 each_card
      const each_card = {
        matrix: matrix,
        model: processedItem.model,
        price_cny: processedItem.price_cny,
        id: processedItem.id
      };
  
      return each_card;
    });
  
    // 返回结果（如果只有一项也可以直接返回数组）
    return { each_card: result };
  }
  