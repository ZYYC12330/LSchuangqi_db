/**
 * 分析板卡覆盖情况
 * @param {Object} data - 输入数据对象，包含 raw 字段
 * @param {Array} data.raw - 板卡数据数组
 * @returns {Object} 返回格式: { cards: [{ id: string, not_satisfied: string[] }] }
 */
function main(data) {
    const raw = data.raw;

    // 收集所有的 Channels_type（过滤掉空字符串）
    const allChannelsTypes = new Set();
    raw.forEach(item => {
        if (item.Channels_type && item.Channels_type.trim() !== '') {
            allChannelsTypes.add(item.Channels_type);
        }
    });

    // 建立板卡 ID 到出现的 Channels_type 的映射
    const cardToChannelsTypes = new Map();

    raw.forEach(item => {
        const channelType = item.Channels_type;
        if (!channelType || channelType.trim() === '') {
            return;
        }

        if (item.matched_board && Array.isArray(item.matched_board)) {
            item.matched_board.forEach(board => {
                if (board.id) {
                    if (!cardToChannelsTypes.has(board.id)) {
                        cardToChannelsTypes.set(board.id, new Set());
                    }
                    cardToChannelsTypes.get(board.id).add(channelType);
                }
            });
        }
    });

    // 生成每张板卡未满足的需求类型
    const result = [];

    cardToChannelsTypes.forEach((satisfiedTypes, cardId) => {
        const notSatisfied = Array.from(allChannelsTypes).filter(
            type => !satisfiedTypes.has(type)
        );
        result.push({
            id: cardId,
            not_satisfied: notSatisfied
        });
    });

    // 按未满足数量升序排序（即满足需求多的在前）
    result.sort((a, b) => a.not_satisfied.length - b.not_satisfied.length);

    // 返回结构化 JSON 结果
    return {
        cards: result
    };
}

// 导出函数
module.exports = { main };
