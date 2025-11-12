以下是${I3xmtwTmZJYbSxPD["type"]}类型的卡的描述，请你将该描述中的所有属性抽取出来，根据提供的sql建表语句，填入对应的字段中。

sql建表语句:
```



```


以下是一个示例：
```
描述：
32通道并行模拟量采集，16位分辨率
每8通道一组，整组支持配置为电压采集或电流采集
电压采集：精度0.2%（F.S.），范围-10V～+10V（可客制-30V～+30V）
采样率：200kHz
电流采集：精度0.2%（F.S.），范围-20mA～+20mA（可客制-100mA～+100mA）

输出：
{
  "AD_channel_count": 16,
  "AD_resolution_bits": 16,
  "AD_sampling_rate_Hz": 200000,
  "AD_input_voltage_min_V": -10.0,
  "AD_input_voltage_max_V": 10.0,
  "AD_input_current_min_mA": -20.0,
  "AD_input_current_max_mA": 20.0,
  "AD_accuracy_percent_FS": 0.1,
  "Customization_support": "电压范围可定制为-30V～+30V；电流范围可定制为-100mA～+100mA"
}
```

参考以上信息，请你对以下描述进行转译：