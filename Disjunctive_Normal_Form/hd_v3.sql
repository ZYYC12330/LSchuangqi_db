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
CREATE TABLE hardware_specifications (
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
    AD_current_sampling_resistor_accuracy_percent NUMERIC(8, 4)

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
