const fs = require('fs');
const path = require('path');
const { main } = require('./analyze_card_coverage');

// 读取原始数据
const inputFile = path.join(__dirname, '所有满足条件的板卡.json');
const jsonData = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));

// 调用函数，传入数据
const result = main({ raw: jsonData.Result });

// 输出结果
console.log('分析完成！');
console.log(`共分析 ${result.cards.length} 张板卡\n`);

// 展示前5个结果
console.log('前5张板卡的分析结果:');
result.cards.slice(0, 5).forEach((card, index) => {
    console.log(`\n${index + 1}. ${JSON.stringify(card, null, 2)}`);
});

// 保存完整结果到文件
const outputFile = path.join(__dirname, 'card_coverage_result.json');
fs.writeFileSync(outputFile, JSON.stringify(result.cards, null, 2), 'utf-8');
console.log(`\n完整结果已保存到: ${outputFile}`);

