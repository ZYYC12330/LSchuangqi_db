-- 删除已存在的表（如果存在）- 必须先删除表，因为表依赖枚举类型
DROP TABLE IF EXISTS hardware_specifications_1109 CASCADE;

-- 删除已存在的枚举类型（如果存在）
DROP TYPE IF EXISTS ad_coupling_mode_enum CASCADE;
DROP TYPE IF EXISTS ad_input_mode_enum CASCADE;
DROP TYPE IF EXISTS uart_mode_enum CASCADE;
DROP TYPE IF EXISTS rfm_fiber_mode_enum CASCADE;
DROP TYPE IF EXISTS i2c_interface_type_enum CASCADE;
DROP TYPE IF EXISTS motion_pulse_output_enum CASCADE;
DROP TYPE IF EXISTS encoder_signal_level_enum CASCADE;
DROP TYPE IF EXISTS pps_logic_level_enum CASCADE;
DROP TYPE IF EXISTS mil1553_operation_mode_enum CASCADE;

-- A/D 耦合方式
CREATE TYPE ad_coupling_mode_enum AS ENUM (
    'DC',  -- 直流耦合
    'AC'   -- 交流耦合
);

-- A/D 输入模式
CREATE TYPE ad_input_mode_enum AS ENUM (
    '单端',
    '差分'
);

-- 串口模式
CREATE TYPE uart_mode_enum AS ENUM (
    'RS-232',
    'RS-422',
    'RS-485'
);

-- 反射内存光纤模式
CREATE TYPE rfm_fiber_mode_enum AS ENUM (
    '多模',
    '单模'
);

-- I2C 接口主从类型
CREATE TYPE i2c_interface_type_enum AS ENUM (
    'Master',
    'Slave'
);

-- 运动控制脉冲输出类型
CREATE TYPE motion_pulse_output_enum AS ENUM (
    '差分',
    '单端'
);

-- 编码器信号电平类型（新增）
CREATE TYPE encoder_signal_level_enum AS ENUM (
    'RS-422',
    '5V CMOS'
);

-- PPS 电平标准（新增）
CREATE TYPE pps_logic_level_enum AS ENUM (
    '5V CMOS',
    '5V RS422'
);

-- MIL-1553B 工作模式（新增）
CREATE TYPE mil1553_operation_mode_enum AS ENUM (
    'BC',
    'RT',
    'BM'
);

-- 创建硬件规格表
CREATE TABLE hardware_specifications_1109 (
    id SERIAL PRIMARY KEY,

    -- 基础信息 (从 raw_data.csv 导入)
    category VARCHAR(100),
    type VARCHAR(200),
    model VARCHAR(100),
    brand VARCHAR(100),
    price_cny NUMERIC(12, 2),
    quantity INT,
    total_amount_cny NUMERIC(14, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 保留原始文本描述
    brief_description TEXT,
    detailed_description TEXT,

    -- A/D (模拟量输入)
    AD_channel_count_single_ended INT,          -- 单端通道数量（例如：32）
    AD_channel_count_differential INT,          -- 差分通道数量（例如：16）
    AD_resolution_bits INT NOT NULL,            -- 分辨率，单位：位（如16）
    AD_sampling_rate_Hz NUMERIC(15, 3),         -- 最大采样率，单位：Hz（如100000.000）
    AD_input_voltage_range_min_V NUMERIC(10, 3), -- 最小输入电压（如 -10.000）
    AD_input_voltage_range_max_V NUMERIC(10, 3), -- 最大输入电压（如 +10.000）
    AD_input_voltage_programmable BOOLEAN,       -- 是否支持软件设置不同量程（如 ±10V/±5V/...）
    AD_input_current_ranges_mA VARCHAR(100),
    AD_accuracy_voltage_percent_FS NUMERIC(8, 4),
    AD_accuracy_current_percent_FS NUMERIC(8, 4),
    AD_accuracy_description TEXT,                -- 补充精度说明（如温度影响、线性度等）
    AD_input_impedance_ohm NUMERIC(15, 3),      -- 输入阻抗，单位：Ω（如 10000000 表示 10 MΩ）
    AD_coupling_mode ad_coupling_mode_enum,
    AD_input_modes ad_input_mode_enum[],
    AD_isolation_support BOOLEAN,
    AD_channel_group_size INT,                  -- 通道分组大小（如每8通道一组）
    AD_group_configurable_voltage_current BOOLEAN, -- 组内是否可分别配置为电压或电流输入
    AD_current_sampling_resistor_ohm NUMERIC(10, 3),
    AD_current_sampling_resistor_accuracy_percent NUMERIC(8, 4),

    -- D/A (模拟量输出)
    DA_channel_count INT,
    DA_resolution_bits INT,
    DA_update_rate_Hz NUMERIC(15, 3),
    DA_output_voltage_min_V NUMERIC(10, 6),
    DA_output_voltage_max_V NUMERIC(10, 6),
    DA_output_current_min_mA NUMERIC(12, 6),
    DA_output_current_max_mA NUMERIC(12, 6),
    DA_accuracy_voltage_percent_FS NUMERIC(8, 4),
    DA_accuracy_current_percent_FS NUMERIC(8, 4),
    DA_slew_rate_V_per_us NUMERIC(10, 6),
    DA_slew_rate_mA_per_us NUMERIC(12, 6),
    DA_isolation_support BOOLEAN,
    DA_output_mode_programmable BOOLEAN,
    DA_output_mode_configurable_switch BOOLEAN,

    -- DIO (数字 I/O)
    DIO_total_channel_count INT,
    DI_channel_count INT,
    DO_channel_count INT,
    DIO_logic_level VARCHAR(50),  -- 电平标准较复杂，如 "5V CMOS/TTL"，保留VARCHAR
    DIO_isolation_voltage_V NUMERIC(10, 3),
    DIO_interrupt_capability BOOLEAN,
    DIO_direction_group_size INT,
    DIO_isolation_support BOOLEAN,
    DIO_configurable_as_counter BOOLEAN,
    DIO_configurable_as_pwm BOOLEAN,
    DIO_configurable_as_pulse_input BOOLEAN,
    DI_voltage_range_min_V NUMERIC(10, 3),
    DI_voltage_range_max_V NUMERIC(10, 3),
    DO_voltage_range_min_V NUMERIC(10, 3),
    DO_voltage_range_max_V NUMERIC(10, 3),
    DO_drive_current_mA NUMERIC(10, 3),
    DO_sink_current_max_mA NUMERIC(10, 3),
    DO_is_relay BOOLEAN,

    -- PWM (脉宽调制)
    PWM_output_channel_count INT,
    PWM_frequency_min_Hz NUMERIC(15, 3),
    PWM_frequency_max_Hz NUMERIC(15, 3),
    PWM_complementary_output_support BOOLEAN,
    PWM_dead_zone_configurable BOOLEAN,
    PWM_isolation_support BOOLEAN,
    
    -- Encoder (编码器)
    Encoder_quadrature_channel_count INT,
    Encoder_hall_channel_count INT,
    Encoder_channel_count_differential INT,
    Encoder_channel_count_single_ended INT,
    Encoder_counter_bits INT,
    Encoder_max_input_frequency_Hz NUMERIC(15, 3),
    Encoder_signal_types_supported encoder_signal_level_enum[],  -- 多选：RS-422 和/或 5V CMOS
    Encoder_isolation_support BOOLEAN,
    Encoder_digital_debounce_support BOOLEAN,

    -- Counter (计数器)
    Counter_channel_count INT,
    Counter_bits INT,
    Counter_max_input_frequency_Hz NUMERIC(15, 3),
    Counter_reference_clock_Hz NUMERIC(15, 3),

    -- CAN
    CAN_channel_count INT,
    CAN_baud_rate_min_bps NUMERIC(12, 0),
    CAN_baud_rate_max_bps NUMERIC(12, 0),
    CAN_FD_support BOOLEAN,
    CAN_FD_baud_rate_min_bps NUMERIC(12, 0),
    CAN_FD_baud_rate_max_bps NUMERIC(12, 0),
    CAN_isolation_voltage_V NUMERIC(10, 3),
    can_protocol_j1939_support BOOLEAN,
    can_protocol_canopen_support BOOLEAN,
    can_protocol_dbc_support BOOLEAN,
    can_protocol_uds_support BOOLEAN,

    -- UART (串口)
    UART_channel_count INT,
    UART_interface_types_supported uart_mode_enum[],  -- 多选：支持多种模式
    UART_max_baud_rate_bps NUMERIC(12, 0),
    UART_FIFO_depth_bytes INT,
    UART_isolation_support BOOLEAN,

    -- 1553B
    MIL1553_channel_count INT,
    MIL1553_redundancy_support BOOLEAN,
    MIL1553_operation_modes_supported mil1553_operation_mode_enum[],  -- 多选：BC/RT/BM 可同时工作
    MIL1553_multifunction_support BOOLEAN,

    -- ARINC429
    A429_tx_channel_count INT,
    A429_rx_channel_count INT,
    A429_baud_rate_options_bps VARCHAR(200),  -- 波特率选项如 "12.5k,48k,100k"，较复杂，保留TEXT
    A429_FIFO_depth_bytes INT,

    -- AFDX
    AFDX_channel_count INT,
    AFDX_port_count INT,
    AFDX_tx_buffer_depth_bytes INT,
    AFDX_rx_buffer_depth_bytes INT,
    AFDX_hardware_protocol_stack BOOLEAN,
    
    -- 其他总线协议（布尔标志即可）
    Profinet_support BOOLEAN,
    EtherCat_support BOOLEAN,
    DeviceNet_support BOOLEAN,
    Profibus_DP_support BOOLEAN,

    -- SPI
    SPI_channel_count INT,
    SPI_master_slave_modes VARCHAR(50),  -- 如 "2主2从"，结构复杂，保留TEXT
    SPI_data_width_bits INT,
    SPI_clock_frequency_Hz NUMERIC(15, 3),
    SPI_logic_level VARCHAR(50),

    -- SSI
    SSI_channel_count INT,
    SSI_data_width_bits_min INT,
    SSI_data_width_bits_max INT,
    SSI_baud_rate_options_Hz NUMERIC[],  -- 注意：这里仍是 NUMERIC[]，因为波特率是数值列表，非枚举
    SSI_measurement_interval_us INT,

    -- Endat
    Endat_channel_count INT,
    Endat_version VARCHAR(10),
    Endat_resolution_bits_min INT,
    Endat_resolution_bits_max INT,
    Endat_baud_rate_options_Hz NUMERIC[],
    endat22_flag_bits_options INT[],
    endat22_recovery_time_min_us INT,
    endat22_recovery_time_max_us INT,

    -- BISS-C
    BISSC_channel_count INT,
    BISSC_data_width_bits_min INT,
    BISSC_data_width_bits_max INT,
    BISSC_baud_rate_options_Hz NUMERIC[],

    -- SENT / PSI5
    SENT_channel_count INT,
    PSI5_channel_count INT,

    -- I2C
    I2C_channel_count INT,
    I2C_interface_type i2c_interface_type_enum,  -- 单选：Slave or Master
    i2c_standard_mode_rate_kbps INT,
    i2c_fast_mode_rate_kbps INT,
    i2c_fast_mode_plus_rate_Mbps NUMERIC(4, 2),
    I2C_address_space_bytes INT,

    -- PCM / LVDS
    PCM_channel_count INT,
    LVDS_channel_count INT,

    -- RDC/SDC (旋变/自整角机)
    RDC_SDC_channel_count INT,
    RDC_SDC_resolution_bits INT,
    RDC_SDC_excitation_voltage_Vpp NUMERIC(10, 6),
    RDC_SDC_excitation_frequency_min_Hz NUMERIC(15, 3),
    RDC_SDC_excitation_frequency_max_Hz NUMERIC(15, 3),
    RDC_SDC_input_signal_min_Vrms NUMERIC(10, 6),
    RDC_SDC_input_signal_max_Vrms NUMERIC(10, 6),
    RDC_SDC_coarse_fine_support BOOLEAN,
    RDC_SDC_mode_configurable BOOLEAN,

    -- LVDT/RVDT
    LVDT_RVDT_channel_count INT,
    LVDT_RVDT_reference_voltage_V NUMERIC(10, 6),
    LVDT_RVDT_reference_frequency_min_Hz NUMERIC(15, 3),
    LVDT_RVDT_reference_frequency_max_Hz NUMERIC(15, 3),
    LVDT_RVDT_output_voltage_min_V NUMERIC(10, 6),
    LVDT_RVDT_output_voltage_max_V NUMERIC(10, 6),
    LVDT_RVDT_accuracy_arcmin NUMERIC(8, 3),
    LVDT_RVDT_rdc_support BOOLEAN,

    -- RTD (可编程电阻)
    RTD_channel_count INT,
    RTD_resolution_bits INT,
    RTD_resistance_min_ohm NUMERIC(12, 6),
    RTD_resistance_max_ohm NUMERIC(12, 6),
    RTD_resolution_ohm NUMERIC(12, 6),
    RTD_accuracy_percent NUMERIC(8, 4),
    RTD_accuracy_ohm_offset NUMERIC(10, 6),
    RTD_max_power_mW NUMERIC(10, 3),

    -- PPS (秒脉冲)
    PPS_input_channel_count INT,
    PPS_output_channel_count INT,
    PPS_sync_accuracy_ns NUMERIC(12, 3),
    PPS_oscillator_frequency_Hz NUMERIC(15, 3),
    PPS_oscillator_stability_ppb NUMERIC(10, 3),
    PPS_logic_levels_supported pps_logic_level_enum[],  -- 多选：CMOS 和/或 RS422

    -- RFM (反射内存)
    RFM_memory_size_bytes BIGINT,
    RFM_FIFO_depth_bytes INT,
    RFM_baud_rate_bps NUMERIC(12, 0),
    RFM_fiber_transmission_distance_m NUMERIC(10, 3),
    RFM_fiber_mode rfm_fiber_mode_enum,  -- 单选：多模/单模

    -- FPGA
    FPGA_logic_cells INT,
    FPGA_flip_flops INT,
    FPGA_luts INT,
    FPGA_multipliers_MACCs INT,
    FPGA_block_ram_Mb NUMERIC(10, 3),
    FPGA_transceivers_count_and_speed VARCHAR(255),
    FPGA_fiber_channel_count INT,
    -- FPGA PS (Processing System)
    FPGA_PS_ARM_cores INT,
    FPGA_PS_CPU_frequency_Hz NUMERIC(15, 3),
    FPGA_PS_cache_L1_L2 VARCHAR(100),
    FPGA_PS_on_chip_ram_KB INT,
    FPGA_PS_external_memory_support VARCHAR(100),

    -- 运动控制
    Motion_control_axis_count INT,
    Motion_DA_channel_count INT,
    Motion_AD_channel_count INT,
    Motion_encoder_input_channel_count INT,
    Motion_enable_reset_channel_count INT,
    Motion_pulse_output_channel_count INT,
    Motion_pulse_output_type motion_pulse_output_enum,  -- 单选：差分/单端

    -- 板卡信息
    Bus_interface_type VARCHAR(100),
    Form_factor VARCHAR(50),
    Supported_series VARCHAR(100),

    -- 其他通用特性
    custom_voltage_range_min_V NUMERIC(10, 3),
    custom_voltage_range_max_V NUMERIC(10, 3),
    custom_current_range_min_mA NUMERIC(10, 3),
    custom_current_range_max_mA NUMERIC(10, 3),
    
    driver_support_linux BOOLEAN,
    driver_support_windows BOOLEAN,
    driver_support_realtime BOOLEAN,
    
    Protocol_analysis_support BOOLEAN,
    DPM_support BOOLEAN,
    Termination_resistor_ohm NUMERIC(10, 3),
    Coupler_port_count INT,
    Power_output_channel_count INT,
    Power_output_voltage_V NUMERIC(10, 6),
    Power_output_current_mA NUMERIC(12, 3),
    Input_overvoltage_protection_V NUMERIC(10, 3),
    Output_on_resistance_ohm NUMERIC(10, 6),

    -- 继电器特性
    Relay_type VARCHAR(50),
    Relay_bounce_time_ms NUMERIC(8, 3),
    Relay_max_current_mA NUMERIC(12, 3),
    Relay_max_voltage_VDC NUMERIC(10, 3)
);

-- 基础信息
COMMENT ON COLUMN hardware_specifications_1109.id IS '主键ID';
COMMENT ON COLUMN hardware_specifications_1109.category IS '产品类别（如数据采集卡、运动控制卡等）';
COMMENT ON COLUMN hardware_specifications_1109.type IS '产品子类型（如PCIe板卡、USB模块等）';
COMMENT ON COLUMN hardware_specifications_1109.model IS '型号';
COMMENT ON COLUMN hardware_specifications_1109.brand IS '品牌';
COMMENT ON COLUMN hardware_specifications_1109.price_cny IS '单价（人民币元）';
COMMENT ON COLUMN hardware_specifications_1109.quantity IS '采购数量';
COMMENT ON COLUMN hardware_specifications_1109.total_amount_cny IS '总金额（人民币元）';
COMMENT ON COLUMN hardware_specifications_1109.created_at IS '创建时间';
COMMENT ON COLUMN hardware_specifications_1109.brief_description IS '简要描述（原始文本）';
COMMENT ON COLUMN hardware_specifications_1109.detailed_description IS '详细描述（原始文本）';

-- A/D 模拟量输入
COMMENT ON COLUMN hardware_specifications_1109.AD_channel_count_single_ended IS '单端模拟输入通道数';
COMMENT ON COLUMN hardware_specifications_1109.AD_channel_count_differential IS '差分模拟输入通道数';
COMMENT ON COLUMN hardware_specifications_1109.AD_resolution_bits IS 'AD分辨率（位）';
COMMENT ON COLUMN hardware_specifications_1109.AD_sampling_rate_Hz IS '最大采样率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.AD_input_voltage_range_min_V IS '输入电压范围最小值（V）';
COMMENT ON COLUMN hardware_specifications_1109.AD_input_voltage_range_max_V IS '输入电压范围最大值（V）';
COMMENT ON COLUMN hardware_specifications_1109.AD_input_voltage_programmable IS '是否支持软件编程设置不同电压量程';
COMMENT ON COLUMN hardware_specifications_1109.AD_input_current_ranges_mA IS '支持的电流输入范围（mA），字符串形式如 "0-20,4-20"';
COMMENT ON COLUMN hardware_specifications_1109.AD_accuracy_voltage_percent_FS IS '电压测量精度（满量程百分比%）';
COMMENT ON COLUMN hardware_specifications_1109.AD_accuracy_current_percent_FS IS '电流测量精度（满量程百分比%）';
COMMENT ON COLUMN hardware_specifications_1109.AD_accuracy_description IS '精度补充说明（如温度漂移、线性度等）';
COMMENT ON COLUMN hardware_specifications_1109.AD_input_impedance_ohm IS '输入阻抗（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.AD_coupling_mode IS 'AD耦合方式（直流DC / 交流AC）';
COMMENT ON COLUMN hardware_specifications_1109.AD_input_modes IS '支持的AD输入模式（单端、差分，可多选）';
COMMENT ON COLUMN hardware_specifications_1109.AD_isolation_support IS '是否支持通道隔离';
COMMENT ON COLUMN hardware_specifications_1109.AD_channel_group_size IS '通道分组大小（例如每8通道为一组）';
COMMENT ON COLUMN hardware_specifications_1109.AD_group_configurable_voltage_current IS '组内是否可分别配置为电压或电流输入';
COMMENT ON COLUMN hardware_specifications_1109.AD_current_sampling_resistor_ohm IS '电流采样电阻阻值（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.AD_current_sampling_resistor_accuracy_percent IS '电流采样电阻精度（%）';

-- D/A 模拟量输出
COMMENT ON COLUMN hardware_specifications_1109.DA_channel_count IS 'DA输出通道数';
COMMENT ON COLUMN hardware_specifications_1109.DA_resolution_bits IS 'DA分辨率（位）';
COMMENT ON COLUMN hardware_specifications_1109.DA_update_rate_Hz IS '最大更新速率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.DA_output_voltage_min_V IS '输出电压最小值（V）';
COMMENT ON COLUMN hardware_specifications_1109.DA_output_voltage_max_V IS '输出电压最大值（V）';
COMMENT ON COLUMN hardware_specifications_1109.DA_output_current_min_mA IS '输出电流最小值（mA）';
COMMENT ON COLUMN hardware_specifications_1109.DA_output_current_max_mA IS '输出电流最大值（mA）';
COMMENT ON COLUMN hardware_specifications_1109.DA_accuracy_voltage_percent_FS IS '电压输出精度（满量程百分比%）';
COMMENT ON COLUMN hardware_specifications_1109.DA_accuracy_current_percent_FS IS '电流输出精度（满量程百分比%）';
COMMENT ON COLUMN hardware_specifications_1109.DA_slew_rate_V_per_us IS '电压压摆率（V/μs）';
COMMENT ON COLUMN hardware_specifications_1109.DA_slew_rate_mA_per_us IS '电流压摆率（mA/μs）';
COMMENT ON COLUMN hardware_specifications_1109.DA_isolation_support IS '是否支持DA输出隔离';
COMMENT ON COLUMN hardware_specifications_1109.DA_output_mode_programmable IS '是否支持软件编程切换输出模式（电压/电流）';
COMMENT ON COLUMN hardware_specifications_1109.DA_output_mode_configurable_switch IS '是否可通过硬件跳线/开关配置输出模式';

-- DIO 数字I/O
COMMENT ON COLUMN hardware_specifications_1109.DIO_total_channel_count IS '数字I/O总通道数';
COMMENT ON COLUMN hardware_specifications_1109.DI_channel_count IS '数字输入通道数';
COMMENT ON COLUMN hardware_specifications_1109.DO_channel_count IS '数字输出通道数';
COMMENT ON COLUMN hardware_specifications_1109.DIO_logic_level IS '逻辑电平标准（如5V CMOS/TTL）';
COMMENT ON COLUMN hardware_specifications_1109.DIO_isolation_voltage_V IS '隔离耐压（V）';
COMMENT ON COLUMN hardware_specifications_1109.DIO_interrupt_capability IS '是否支持中断功能';
COMMENT ON COLUMN hardware_specifications_1109.DIO_direction_group_size IS '方向配置分组大小（如每8位一组）';
COMMENT ON COLUMN hardware_specifications_1109.DIO_isolation_support IS '是否支持DIO隔离';
COMMENT ON COLUMN hardware_specifications_1109.DIO_configurable_as_counter IS '是否可配置为计数器';
COMMENT ON COLUMN hardware_specifications_1109.DIO_configurable_as_pwm IS '是否可配置为PWM输出';
COMMENT ON COLUMN hardware_specifications_1109.DIO_configurable_as_pulse_input IS '是否可配置为脉冲输入';
COMMENT ON COLUMN hardware_specifications_1109.DI_voltage_range_min_V IS '数字输入电压范围最小值（V）';
COMMENT ON COLUMN hardware_specifications_1109.DI_voltage_range_max_V IS '数字输入电压范围最大值（V）';
COMMENT ON COLUMN hardware_specifications_1109.DO_voltage_range_min_V IS '数字输出电压范围最小值（V）';
COMMENT ON COLUMN hardware_specifications_1109.DO_voltage_range_max_V IS '数字输出电压范围最大值（V）';
COMMENT ON COLUMN hardware_specifications_1109.DO_drive_current_mA IS '数字输出驱动电流（mA）';
COMMENT ON COLUMN hardware_specifications_1109.DO_sink_current_max_mA IS '数字输出灌电流最大值（mA）';
COMMENT ON COLUMN hardware_specifications_1109.DO_is_relay IS '数字输出是否为继电器类型';

-- PWM 脉宽调制
COMMENT ON COLUMN hardware_specifications_1109.PWM_output_channel_count IS 'PWM输出通道数';
COMMENT ON COLUMN hardware_specifications_1109.PWM_frequency_min_Hz IS 'PWM频率最小值（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.PWM_frequency_max_Hz IS 'PWM频率最大值（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.PWM_complementary_output_support IS '是否支持互补PWM输出';
COMMENT ON COLUMN hardware_specifications_1109.PWM_dead_zone_configurable IS '死区时间是否可配置';
COMMENT ON COLUMN hardware_specifications_1109.PWM_isolation_support IS '是否支持PWM输出隔离';

-- Encoder 编码器
COMMENT ON COLUMN hardware_specifications_1109.Encoder_quadrature_channel_count IS '正交编码器通道数（A/B/Z）';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_hall_channel_count IS '霍尔传感器通道数';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_channel_count_differential IS '差分编码器信号通道数';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_channel_count_single_ended IS '单端编码器信号通道数';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_counter_bits IS '计数器位宽（bit）';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_max_input_frequency_Hz IS '最大输入频率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_signal_types_supported IS '支持的编码器信号电平类型（RS-422、5V CMOS，可多选）';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_isolation_support IS '是否支持编码器信号隔离';
COMMENT ON COLUMN hardware_specifications_1109.Encoder_digital_debounce_support IS '是否支持数字去抖';

-- Counter 计数器
COMMENT ON COLUMN hardware_specifications_1109.Counter_channel_count IS '计数器通道数';
COMMENT ON COLUMN hardware_specifications_1109.Counter_bits IS '计数器位宽（bit）';
COMMENT ON COLUMN hardware_specifications_1109.Counter_max_input_frequency_Hz IS '计数器最大输入频率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.Counter_reference_clock_Hz IS '参考时钟频率（Hz）';

-- CAN 总线
COMMENT ON COLUMN hardware_specifications_1109.CAN_channel_count IS 'CAN通道数';
COMMENT ON COLUMN hardware_specifications_1109.CAN_baud_rate_min_bps IS 'CAN波特率最小值（bps）';
COMMENT ON COLUMN hardware_specifications_1109.CAN_baud_rate_max_bps IS 'CAN波特率最大值（bps）';
COMMENT ON COLUMN hardware_specifications_1109.CAN_FD_support IS '是否支持CAN FD';
COMMENT ON COLUMN hardware_specifications_1109.CAN_FD_baud_rate_min_bps IS 'CAN FD波特率最小值（bps）';
COMMENT ON COLUMN hardware_specifications_1109.CAN_FD_baud_rate_max_bps IS 'CAN FD波特率最大值（bps）';
COMMENT ON COLUMN hardware_specifications_1109.CAN_isolation_voltage_V IS 'CAN隔离耐压（V）';
COMMENT ON COLUMN hardware_specifications_1109.can_protocol_j1939_support IS '是否支持J1939协议';
COMMENT ON COLUMN hardware_specifications_1109.can_protocol_canopen_support IS '是否支持CANopen协议';
COMMENT ON COLUMN hardware_specifications_1109.can_protocol_dbc_support IS '是否支持DBC文件解析';
COMMENT ON COLUMN hardware_specifications_1109.can_protocol_uds_support IS '是否支持UDS诊断协议';

-- UART 串口
COMMENT ON COLUMN hardware_specifications_1109.UART_channel_count IS 'UART通道数';
COMMENT ON COLUMN hardware_specifications_1109.UART_interface_types_supported IS '支持的串口电气接口类型（RS-232/422/485，可多选）';
COMMENT ON COLUMN hardware_specifications_1109.UART_max_baud_rate_bps IS '最大波特率（bps）';
COMMENT ON COLUMN hardware_specifications_1109.UART_FIFO_depth_bytes IS 'FIFO深度（字节）';
COMMENT ON COLUMN hardware_specifications_1109.UART_isolation_support IS '是否支持UART隔离';

-- MIL-STD-1553B
COMMENT ON COLUMN hardware_specifications_1109.MIL1553_channel_count IS '1553B通道数';
COMMENT ON COLUMN hardware_specifications_1109.MIL1553_redundancy_support IS '是否支持双冗余总线';
COMMENT ON COLUMN hardware_specifications_1109.MIL1553_operation_modes_supported IS '支持的工作模式（BC/RT/BM，可多选）';
COMMENT ON COLUMN hardware_specifications_1109.MIL1553_multifunction_support IS '是否支持多功能（同一通道可配置为多种角色）';

-- ARINC429
COMMENT ON COLUMN hardware_specifications_1109.A429_tx_channel_count IS 'ARINC429发送通道数';
COMMENT ON COLUMN hardware_specifications_1109.A429_rx_channel_count IS 'ARINC429接收通道数';
COMMENT ON COLUMN hardware_specifications_1109.A429_baud_rate_options_bps IS '支持的波特率选项（如"12.5k,48k,100k"）';
COMMENT ON COLUMN hardware_specifications_1109.A429_FIFO_depth_bytes IS 'FIFO深度（字节）';

-- AFDX
COMMENT ON COLUMN hardware_specifications_1109.AFDX_channel_count IS 'AFDX通道数';
COMMENT ON COLUMN hardware_specifications_1109.AFDX_port_count IS 'AFDX端口数';
COMMENT ON COLUMN hardware_specifications_1109.AFDX_tx_buffer_depth_bytes IS '发送缓冲区深度（字节）';
COMMENT ON COLUMN hardware_specifications_1109.AFDX_rx_buffer_depth_bytes IS '接收缓冲区深度（字节）';
COMMENT ON COLUMN hardware_specifications_1109.AFDX_hardware_protocol_stack IS '是否集成硬件协议栈';

-- 其他工业总线协议支持标志
COMMENT ON COLUMN hardware_specifications_1109.Profinet_support IS '是否支持Profinet协议';
COMMENT ON COLUMN hardware_specifications_1109.EtherCat_support IS '是否支持EtherCAT协议';
COMMENT ON COLUMN hardware_specifications_1109.DeviceNet_support IS '是否支持DeviceNet协议';
COMMENT ON COLUMN hardware_specifications_1109.Profibus_DP_support IS '是否支持Profibus-DP协议';

-- SPI
COMMENT ON COLUMN hardware_specifications_1109.SPI_channel_count IS 'SPI通道数';
COMMENT ON COLUMN hardware_specifications_1109.SPI_master_slave_modes IS '主从模式配置（如"2主2从"）';
COMMENT ON COLUMN hardware_specifications_1109.SPI_data_width_bits IS '数据位宽（bit）';
COMMENT ON COLUMN hardware_specifications_1109.SPI_clock_frequency_Hz IS 'SPI时钟频率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.SPI_logic_level IS 'SPI逻辑电平标准';

-- SSI
COMMENT ON COLUMN hardware_specifications_1109.SSI_channel_count IS 'SSI通道数';
COMMENT ON COLUMN hardware_specifications_1109.SSI_data_width_bits_min IS 'SSI数据位宽最小值（bit）';
COMMENT ON COLUMN hardware_specifications_1109.SSI_data_width_bits_max IS 'SSI数据位宽最大值（bit）';
COMMENT ON COLUMN hardware_specifications_1109.SSI_baud_rate_options_Hz IS '支持的波特率列表（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.SSI_measurement_interval_us IS '测量间隔（微秒）';

-- EnDat
COMMENT ON COLUMN hardware_specifications_1109.Endat_channel_count IS 'EnDat通道数';
COMMENT ON COLUMN hardware_specifications_1109.Endat_version IS 'EnDat协议版本（如"2.2"）';
COMMENT ON COLUMN hardware_specifications_1109.Endat_resolution_bits_min IS '分辨率最小值（bit）';
COMMENT ON COLUMN hardware_specifications_1109.Endat_resolution_bits_max IS '分辨率最大值（bit）';
COMMENT ON COLUMN hardware_specifications_1109.Endat_baud_rate_options_Hz IS '支持的波特率列表（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.endat22_flag_bits_options IS 'EnDat 2.2 支持的标志位选项';
COMMENT ON COLUMN hardware_specifications_1109.endat22_recovery_time_min_us IS 'EnDat 2.2 最小恢复时间（微秒）';
COMMENT ON COLUMN hardware_specifications_1109.endat22_recovery_time_max_us IS 'EnDat 2.2 最大恢复时间（微秒）';

-- BISS-C
COMMENT ON COLUMN hardware_specifications_1109.BISSC_channel_count IS 'BISS-C通道数';
COMMENT ON COLUMN hardware_specifications_1109.BISSC_data_width_bits_min IS 'BISS-C数据位宽最小值（bit）';
COMMENT ON COLUMN hardware_specifications_1109.BISSC_data_width_bits_max IS 'BISS-C数据位宽最大值（bit）';
COMMENT ON COLUMN hardware_specifications_1109.BISSC_baud_rate_options_Hz IS '支持的波特率列表（Hz）';

-- SENT / PSI5
COMMENT ON COLUMN hardware_specifications_1109.SENT_channel_count IS 'SENT协议通道数';
COMMENT ON COLUMN hardware_specifications_1109.PSI5_channel_count IS 'PSI5协议通道数';

-- I2C
COMMENT ON COLUMN hardware_specifications_1109.I2C_channel_count IS 'I2C通道数';
COMMENT ON COLUMN hardware_specifications_1109.I2C_interface_type IS 'I2C接口类型（主Master / 从Slave）';
COMMENT ON COLUMN hardware_specifications_1109.i2c_standard_mode_rate_kbps IS '标准模式速率（kbps，通常100）';
COMMENT ON COLUMN hardware_specifications_1109.i2c_fast_mode_rate_kbps IS '快速模式速率（kbps，通常400）';
COMMENT ON COLUMN hardware_specifications_1109.i2c_fast_mode_plus_rate_Mbps IS '快速模式+速率（Mbps，通常1.0）';
COMMENT ON COLUMN hardware_specifications_1109.I2C_address_space_bytes IS 'I2C地址空间大小（字节）';

-- PCM / LVDS
COMMENT ON COLUMN hardware_specifications_1109.PCM_channel_count IS 'PCM通道数';
COMMENT ON COLUMN hardware_specifications_1109.LVDS_channel_count IS 'LVDS通道数';

-- RDC/SDC（旋变/自整角机）
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_channel_count IS 'RDC/SDC通道数';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_resolution_bits IS '分辨率（bit）';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_excitation_voltage_Vpp IS '激励电压峰峰值（Vpp）';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_excitation_frequency_min_Hz IS '激励频率最小值（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_excitation_frequency_max_Hz IS '激励频率最大值（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_input_signal_min_Vrms IS '输入信号最小有效值（Vrms）';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_input_signal_max_Vrms IS '输入信号最大有效值（Vrms）';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_coarse_fine_support IS '是否支持粗精组合测量';
COMMENT ON COLUMN hardware_specifications_1109.RDC_SDC_mode_configurable IS '是否支持模式配置（旋变/自整角机切换）';

-- LVDT/RVDT
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_channel_count IS 'LVDT/RVDT通道数';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_reference_voltage_V IS '参考电压（V）';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_reference_frequency_min_Hz IS '参考频率最小值（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_reference_frequency_max_Hz IS '参考频率最大值（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_output_voltage_min_V IS '输出电压最小值（V）';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_output_voltage_max_V IS '输出电压最大值（V）';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_accuracy_arcmin IS '精度（角分）';
COMMENT ON COLUMN hardware_specifications_1109.LVDT_RVDT_rdc_support IS '是否支持与RDC配合使用';

-- RTD（可编程电阻）
COMMENT ON COLUMN hardware_specifications_1109.RTD_channel_count IS 'RTD通道数';
COMMENT ON COLUMN hardware_specifications_1109.RTD_resolution_bits IS '分辨率（bit）';
COMMENT ON COLUMN hardware_specifications_1109.RTD_resistance_min_ohm IS '电阻输出最小值（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.RTD_resistance_max_ohm IS '电阻输出最大值（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.RTD_resolution_ohm IS '电阻分辨率（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.RTD_accuracy_percent IS '电阻精度（%）';
COMMENT ON COLUMN hardware_specifications_1109.RTD_accuracy_ohm_offset IS '电阻精度偏移量（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.RTD_max_power_mW IS '最大输出功率（mW）';

-- PPS（秒脉冲）
COMMENT ON COLUMN hardware_specifications_1109.PPS_input_channel_count IS 'PPS输入通道数';
COMMENT ON COLUMN hardware_specifications_1109.PPS_output_channel_count IS 'PPS输出通道数';
COMMENT ON COLUMN hardware_specifications_1109.PPS_sync_accuracy_ns IS '同步精度（纳秒）';
COMMENT ON COLUMN hardware_specifications_1109.PPS_oscillator_frequency_Hz IS '内部晶振频率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.PPS_oscillator_stability_ppb IS '晶振稳定性（十亿分之一，ppb）';
COMMENT ON COLUMN hardware_specifications_1109.PPS_logic_levels_supported IS '支持的PPS电平标准（5V CMOS、5V RS422，可多选）';

-- RFM（反射内存）
COMMENT ON COLUMN hardware_specifications_1109.RFM_memory_size_bytes IS '反射内存容量（字节）';
COMMENT ON COLUMN hardware_specifications_1109.RFM_FIFO_depth_bytes IS 'FIFO深度（字节）';
COMMENT ON COLUMN hardware_specifications_1109.RFM_baud_rate_bps IS '传输波特率（bps）';
COMMENT ON COLUMN hardware_specifications_1109.RFM_fiber_transmission_distance_m IS '光纤传输距离（米）';
COMMENT ON COLUMN hardware_specifications_1109.RFM_fiber_mode IS '光纤模式（多模 / 单模）';

-- FPGA
COMMENT ON COLUMN hardware_specifications_1109.FPGA_logic_cells IS 'FPGA逻辑单元数量';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_flip_flops IS 'FPGA触发器数量';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_luts IS 'FPGA查找表（LUT）数量';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_multipliers_MACCs IS 'FPGA乘法器/MACC数量';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_block_ram_Mb IS 'FPGA块RAM容量（Mb）';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_transceivers_count_and_speed IS '收发器数量及速率（如"4x10G"）';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_fiber_channel_count IS '光纤通道数';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_PS_ARM_cores IS 'FPGA硬核处理器ARM核心数';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_PS_CPU_frequency_Hz IS '处理器CPU频率（Hz）';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_PS_cache_L1_L2 IS 'L1/L2缓存配置';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_PS_on_chip_ram_KB IS '片上RAM容量（KB）';
COMMENT ON COLUMN hardware_specifications_1109.FPGA_PS_external_memory_support IS '支持的外部存储器类型（如DDR3/DDR4）';

-- 运动控制
COMMENT ON COLUMN hardware_specifications_1109.Motion_control_axis_count IS '运动控制轴数';
COMMENT ON COLUMN hardware_specifications_1109.Motion_DA_channel_count IS '运动控制DA通道数';
COMMENT ON COLUMN hardware_specifications_1109.Motion_AD_channel_count IS '运动控制AD通道数';
COMMENT ON COLUMN hardware_specifications_1109.Motion_encoder_input_channel_count IS '编码器输入通道数';
COMMENT ON COLUMN hardware_specifications_1109.Motion_enable_reset_channel_count IS '使能/复位信号通道数';
COMMENT ON COLUMN hardware_specifications_1109.Motion_pulse_output_channel_count IS '脉冲输出通道数';
COMMENT ON COLUMN hardware_specifications_1109.Motion_pulse_output_type IS '脉冲输出类型（差分 / 单端）';

-- 板卡信息
COMMENT ON COLUMN hardware_specifications_1109.Bus_interface_type IS '总线接口类型（如PCIe x4, USB3.0, PXIe等）';
COMMENT ON COLUMN hardware_specifications_1109.Form_factor IS '板卡外形规格（如全长、半长、Mini PCIe等）';
COMMENT ON COLUMN hardware_specifications_1109.Supported_series IS '所属产品系列';

-- 其他通用特性
COMMENT ON COLUMN hardware_specifications_1109.custom_voltage_range_min_V IS '自定义电压范围最小值（V）';
COMMENT ON COLUMN hardware_specifications_1109.custom_voltage_range_max_V IS '自定义电压范围最大值（V）';
COMMENT ON COLUMN hardware_specifications_1109.custom_current_range_min_mA IS '自定义电流范围最小值（mA）';
COMMENT ON COLUMN hardware_specifications_1109.custom_current_range_max_mA IS '自定义电流范围最大值（mA）';
COMMENT ON COLUMN hardware_specifications_1109.driver_support_linux IS '是否提供Linux驱动';
COMMENT ON COLUMN hardware_specifications_1109.driver_support_windows IS '是否提供Windows驱动';
COMMENT ON COLUMN hardware_specifications_1109.driver_support_realtime IS '是否支持实时系统（如VxWorks, RT-Linux）';
COMMENT ON COLUMN hardware_specifications_1109.Protocol_analysis_support IS '是否支持协议分析功能';
COMMENT ON COLUMN hardware_specifications_1109.DPM_support IS '是否支持分布式电源管理（DPM）';
COMMENT ON COLUMN hardware_specifications_1109.Termination_resistor_ohm IS '终端电阻阻值（Ω）';
COMMENT ON COLUMN hardware_specifications_1109.Coupler_port_count IS '耦合器端口数量';
COMMENT ON COLUMN hardware_specifications_1109.Power_output_channel_count IS '电源输出通道数';
COMMENT ON COLUMN hardware_specifications_1109.Power_output_voltage_V IS '电源输出电压（V）';
COMMENT ON COLUMN hardware_specifications_1109.Power_output_current_mA IS '电源输出电流（mA）';
COMMENT ON COLUMN hardware_specifications_1109.Input_overvoltage_protection_V IS '输入过压保护阈值（V）';
COMMENT ON COLUMN hardware_specifications_1109.Output_on_resistance_ohm IS '输出导通电阻（Ω）';

-- 继电器特性
COMMENT ON COLUMN hardware_specifications_1109.Relay_type IS '继电器类型（如电磁式、固态等）';
COMMENT ON COLUMN hardware_specifications_1109.Relay_bounce_time_ms IS '继电器触点弹跳时间（ms）';
COMMENT ON COLUMN hardware_specifications_1109.Relay_max_current_mA IS '继电器最大切换电流（mA）';
COMMENT ON COLUMN hardware_specifications_1109.Relay_max_voltage_VDC IS '继电器最大切换电压（VDC）';
