CREATE TABLE real_time_simulator_1109 (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,                    -- 分类
    type TEXT NOT NULL,                        -- 类型
    model TEXT NOT NULL,                       -- 设备型号，如：Links-Box-03-S4（便携）
    manufacturer TEXT NOT NULL,                -- 制造商，如：灵思创奇、信利恒丰
    quote_price NUMERIC NOT NULL,              -- 单台报价（元），不含税
    quantity INTEGER NOT NULL,                 -- 采购数量
    total_price NUMERIC NOT NULL,              -- 总价 = 报价 × 数量（元）
    series TEXT NOT NULL,                      -- 产品系列，如：Links-BOX、Links-C3U

    -- CPU 拆分字段（原 cpu_model 拆解）
    cpu_brand TEXT,                            -- CPU品牌，如：Intel、AMD、海光
    cpu_series TEXT,                           -- CPU系列，如：Core、Xeon、Ryzen
    cpu_model_code TEXT,                       -- CPU型号代码，如：i7-7700k、3350、Gold 6348

    cpu_cores INTEGER,                         -- CPU核心数，如：4、8、16
    cpu_frequency_value NUMERIC,               -- CPU主频数值，如：4.2（单位：GHz）
    cpu_frequency_unit TEXT,                   -- CPU主频单位，如：GHz、MHz
    cpu_threads INTEGER,                       -- CPU线程数，如无则为 NULL，如：8、16、32

    -- 内存拆分字段（原 memory_type 拆解）
    memory_standard TEXT,                      -- 内存标准，如：DDR4、DDR3、LPDDR5
    memory_technology TEXT,                    -- 内存技术，如：SDRAM、DDR5（未来扩展）
    memory_capacity INTEGER,                   -- 内存容量（GB），如：16、64、128

    -- 存储字段
    storage_capacity INTEGER,                  -- 存储容量（GB），如：512、1000、2000
    storage_type TEXT,                         -- 存储类型，如：SATA硬盘、固态盘、NVMe SSD

    -- I/O 插槽字段
    io_slots_pci INTEGER,                      -- 传统PCI插槽数量
    io_slots_pcie_x1 INTEGER,                  -- PCIe x1插槽数量
    io_slots_pcie_x4 INTEGER,                  -- PCIe x4插槽数量
    io_slots_pcie_x8 INTEGER,                  -- PCIe x8插槽数量
    io_slots_pcie_x16 INTEGER,                 -- PCIe x16插槽数量

    -- 网络与系统
    network_ports INTEGER,                     -- 千兆以太网口数量
    os TEXT,                                   -- 操作系统，如：实时操作系统、RTLinux、Windows 10 IoT

    -- 机箱与物理结构
    form_factor TEXT,                          -- 机箱形态，如：便携、机架式、cPCI
    chassis_slots INTEGER,                     -- 机箱总插槽数（仅cPCI适用）
    chassis_height TEXT,                       -- 机箱高度，如：4U、3U、1U
    chassis_design TEXT,                       -- 机箱设计，如：半机架、冗余电源、风冷/液冷

    -- 其他特性
    additional_features TEXT,                  -- 其他特性，如：串口、USB 3.0、HDMI、PS/2、GPIO

    -- 原始描述字段（仅用于调试/审计，非业务核心）
    description_simple TEXT,                   -- 原始“描述（精简）”（保留用于溯源）
    description_detailed TEXT                  -- 原始“描述（详细）”（保留用于溯源）
);
COMMENT ON TABLE real_time_simulator_1109 IS '实时仿真器选型数据表，用于存储仿真设备的硬件配置与报价信息，所有硬件字段均已细粒度拆分，便于查询与分析';

COMMENT ON COLUMN real_time_simulator_1109.id IS '主键ID，自增序列';
COMMENT ON COLUMN real_time_simulator_1109.category IS '设备分类，如：机箱&CPU控制器、机箱&CPU控制板';
COMMENT ON COLUMN real_time_simulator_1109.type IS '设备类型，如：实时仿真器';
COMMENT ON COLUMN real_time_simulator_1109.model IS '设备型号，如：Links-Box-03-S4（便携）';
COMMENT ON COLUMN real_time_simulator_1109.manufacturer IS '制造商名称，如：灵思创奇、信利恒丰';
COMMENT ON COLUMN real_time_simulator_1109.quote_price IS '单台报价（元），不含税价格';
COMMENT ON COLUMN real_time_simulator_1109.quantity IS '采购数量';
COMMENT ON COLUMN real_time_simulator_1109.total_price IS '总价 = 报价 × 数量（元）';
COMMENT ON COLUMN real_time_simulator_1109.series IS '产品系列，如：Links-BOX、Links-C3U';

-- CPU 拆分字段
COMMENT ON COLUMN real_time_simulator_1109.cpu_brand IS 'CPU品牌，如：Intel、AMD、海光';
COMMENT ON COLUMN real_time_simulator_1109.cpu_series IS 'CPU系列，如：Core、Xeon、Ryzen、Phenom';
COMMENT ON COLUMN real_time_simulator_1109.cpu_model_code IS 'CPU型号代码，如：i7-7700k、3350、Gold 6348，用于精确识别型号';
COMMENT ON COLUMN real_time_simulator_1109.cpu_cores IS 'CPU核心数，整数，如：4、8、16、36';
COMMENT ON COLUMN real_time_simulator_1109.cpu_frequency_value IS 'CPU主频数值部分，单位为GHz或MHz，如：4.2、3.0，数值型便于排序与计算';
COMMENT ON COLUMN real_time_simulator_1109.cpu_frequency_unit IS 'CPU主频单位，如：GHz、MHz，用于明确单位语义';
COMMENT ON COLUMN real_time_simulator_1109.cpu_threads IS 'CPU线程数，如无则为NULL，如：8、16、32';

-- 内存拆分字段
COMMENT ON COLUMN real_time_simulator_1109.memory_standard IS '内存标准代号，如：DDR4、DDR3、LPDDR5，用于区分世代';
COMMENT ON COLUMN real_time_simulator_1109.memory_technology IS '内存技术类型，如：SDRAM、GDDR6、DDR5，用于区分架构';
COMMENT ON COLUMN real_time_simulator_1109.memory_capacity IS '内存容量（GB），整数，如：16、64、128';

-- 存储字段
COMMENT ON COLUMN real_time_simulator_1109.storage_capacity IS '存储容量（GB），整数，如：512、1000、2000';
COMMENT ON COLUMN real_time_simulator_1109.storage_type IS '存储介质类型，如：SATA硬盘、固态盘、NVMe SSD、M.2 SSD';

-- I/O 插槽
COMMENT ON COLUMN real_time_simulator_1109.io_slots_pci IS '传统PCI插槽数量，如：0、2、4';
COMMENT ON COLUMN real_time_simulator_1109.io_slots_pcie_x1 IS 'PCIe x1插槽数量，如：1、5';
COMMENT ON COLUMN real_time_simulator_1109.io_slots_pcie_x4 IS 'PCIe x4插槽数量，如：1、2、3';
COMMENT ON COLUMN real_time_simulator_1109.io_slots_pcie_x8 IS 'PCIe x8插槽数量，如：0、1、2';
COMMENT ON COLUMN real_time_simulator_1109.io_slots_pcie_x16 IS 'PCIe x16插槽数量，如：1、2、4';

-- 网络与系统
COMMENT ON COLUMN real_time_simulator_1109.network_ports IS '千兆以太网口数量，如：1、2、4';
COMMENT ON COLUMN real_time_simulator_1109.os IS '操作系统，如：实时操作系统、RTLinux、Windows 10 IoT';

-- 机箱与物理结构
COMMENT ON COLUMN real_time_simulator_1109.form_factor IS '机箱形态，如：便携、机架式、cPCI、VPX';
COMMENT ON COLUMN real_time_simulator_1109.chassis_slots IS '机箱总插槽数，仅cPCI/VME等模块化机箱适用，如：8、14';
COMMENT ON COLUMN real_time_simulator_1109.chassis_height IS '机箱高度（标准机架单位），如：4U、3U、1U';
COMMENT ON COLUMN real_time_simulator_1109.chassis_design IS '机箱设计特性，如：半机架、冗余电源、风冷、液冷、防震设计';

-- 其他特性
COMMENT ON COLUMN real_time_simulator_1109.additional_features IS '其他扩展特性，如：串口（RS232）、USB 3.0、HDMI、DisplayPort、GPIO、PS/2、CAN总线等';

-- 原始描述字段（仅用于调试、审计、数据溯源）
COMMENT ON COLUMN real_time_simulator_1109.description_simple IS '原始“描述（精简）”字段，用于数据清洗溯源或异常排查，非业务核心字段';
COMMENT ON COLUMN real_time_simulator_1109.description_detailed IS '原始“描述（详细）”字段，用于完整保留原始输入，供审计或模型训练使用';
