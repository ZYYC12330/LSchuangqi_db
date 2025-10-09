import numpy as np
from scipy.optimize import linprog
import json

# 输入数据（每个分组代表一类需求的可选板卡）
input_data = [
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-SER-01",
          "price_cny": 60
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPCe-SER-02",
          "price_cny": 60
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-SIO02-16",
          "price_cny": 450
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-SIO02-8A",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-SIO03-16",
          "price_cny": 350
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            2,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-CAN",
          "price_cny": 60
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-CANFD-04",
          "price_cny": 80
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            2,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-CANFD-02",
          "price_cny": 60
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            10,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-CAN-10",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            2,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-CAN",
          "price_cny": 80
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-CAN-4",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-01",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-02",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            32,
            32,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DIO02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-Counter02",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-01",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            4,
            4,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-GTS-01",
          "price_cny": 120
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            8,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-GTS-02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            32,
            32,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DIO02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-ABZ-01",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-ABZ-02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-ABZ-03",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-01",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            32,
            0,
            0,
            0,
            0,
            16,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-07",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-AD-01",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-AD-02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-AD-03",
          "price_cny": 270
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AI-02",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AI-03",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-01",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-02",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-02",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DA-03",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DA-04",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-03",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            18,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-03",
          "price_cny": 240
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            8,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-GTS-02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-01",
          "price_cny": 120
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            24,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-FPGA-Analog-01",
          "price_cny": 260
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            32,
            0,
            0,
            0,
            0,
            16,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-07",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DA-04",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-02",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            18,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-03",
          "price_cny": 240
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            32,
            32,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DIO02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": []
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            96,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DI04",
          "price_cny": 210
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            48,
            48,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DIO04",
          "price_cny": 220
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-Endat-01",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-Endat-02",
          "price_cny": 280
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            64,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DIO64",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-01",
          "price_cny": 120
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            32,
            0,
            0,
            0,
            0,
            16,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-07",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            4,
            0,
            0,
            2,
            8,
            8,
            2,
            0,
            0,
            0,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DA-04",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-02",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            18,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-03",
          "price_cny": 240
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            32,
            32,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DIO02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            128,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DO128",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            64,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DIO64",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DO01",
          "price_cny": 110
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            96,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DO04",
          "price_cny": 220
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            48,
            48,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DIO04",
          "price_cny": 220
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            32,
            0
          ],
          "model": "Links-C3U-DO03",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DAQ-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            16,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-02",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DA-03",
          "price_cny": 150
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-DA-04",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-03",
          "price_cny": 180
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            16,
            0,
            0,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-05",
          "price_cny": 250
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-AO-01",
          "price_cny": 120
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            8,
            8,
            0,
            0,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-IPC-GTS-02",
          "price_cny": 190
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            16,
            24,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-FPGA-Analog-01",
          "price_cny": 260
        }
      ]
    },
    {
      "each_card": [
        {
          "matrix": [
            0,
            0,
            18,
            0,
            0,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "model": "Links-C3U-DAQ-03",
          "price_cny": 240
        }
      ]
    }
  ]

# 输入格式：21个元素的数组，对应21种通道类型
requirements_input = [
    8,   # analogInputChannels
    8,   # analogOutputChannels
    8,   # digitalInputChannels
    8,   # digitalOutputChannels
    0,   # digitalIOChannels
    16,  # serialPortChannels
    2,   # canBusChannels
    12,  # pwmOutputChannels
    2,   # encoderChannels
    0,   # ssiBusChannels
    0,   # spiBusChannels
    0,   # i2cBusChannels
    0,   # pcmLvdChannels
    0,   # bissCChannels
    0,   # afdxChannels
    0,   # ppsPulseChannels
    0,   # rtdResistanceChannels
    6,   # differentialInputChannels
    0,   # milStd1553BChannels
    0,   # timerCounterChannels
    0    # relayOutputChannels
]



# 通道类型名称（对应 matrix 的 21 个位置）
channel_types = [
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
]

# 提取所有板卡数据（扁平化处理）
all_cards = []
for group in input_data:
    all_cards.extend(group["each_card"])

n_cards = len(all_cards)
print(f"板卡总数: {n_cards}")
print("=" * 80)

# 构建资源矩阵（每行是一张板卡，每列是一种通道类型）
# A[i, j] 表示第 i 张板卡提供第 j 种通道的数量
resource_matrix = []
prices = []
models = []

for card in all_cards:
    models.append(card["model"])
    prices.append(card["price_cny"])
    resource_matrix.append(card["matrix"])

# 转换为 numpy 数组
A = np.array(resource_matrix)  # shape: (n_cards, 21)
prices = np.array(prices)

print("板卡信息:")
for i, (model, price) in enumerate(zip(models, prices)):
    print(f"  [{i}] {model:25s} - 价格{price:4d}")
print()

print("资源矩阵 (每行一张板卡):")
print("行数(板卡数):", A.shape[0], "列数(通道类型数):", A.shape[1])
print(A)
print()

# 设置需求约束（根据实际需求修改）
# 转换为 numpy 数组
b_requirements = np.array(requirements_input)

# 打印需求信息
print("需求向量:")
for i, (req, ch_type) in enumerate(zip(requirements_input, channel_types)):
    if req > 0:
        print(f"  [{i:2d}] {ch_type:30s}: {req:3d}")
print()

# 诊断：检查每种通道类型的可用性
print("需求可行性检查:")
print("-" * 80)
for i, channel_type in enumerate(channel_types):
    if b_requirements[i] > 0:
        # 计算该通道类型在所有板卡中的最大可用量
        max_available = A[:, i].sum()  # 所有板卡该通道的总和
        max_single_card = A[:, i].max()  # 单张板卡该通道的最大值
        status = "[OK]" if max_available >= b_requirements[i] else "[不足]"
        print(f"{status} {channel_type:25s}: 需求 {b_requirements[i]:3.0f}, "
              f"可用总量 {max_available:4.0f}, 单卡最大 {max_single_card:3.0f}")
print()

# 目标函数：最小化成本
c = prices

# 约束条件：A.T @ x >= b_requirements
# 即：sum(x[i] * A[i, j]) >= b_requirements[j] for all j
# 转换为 linprog 格式：-A.T @ x <= -b_requirements
A_ub = -A.T
b_ub = -b_requirements

# 变量边界：每种板卡数量 x[i] >= 0（整数约束需要用 integrality 参数）
bounds = [(0, None)] * n_cards

# 求解（添加整数约束，因为板卡数量必须是整数）
result = linprog(
    c=c, 
    A_ub=A_ub, 
    b_ub=b_ub, 
    bounds=bounds, 
    method='highs',
    integrality=[1] * n_cards  # 1 表示该变量必须是整数
)

print("=" * 80)
if result.success:
    print("[优化成功!]")
    print()
    print("最优采购方案:")
    total_cost = 0
    for i, quantity in enumerate(result.x):
        if quantity > 0.01:  # 只显示数量 > 0 的板卡
            cost = quantity * prices[i]
            print(f"  {models[i]:25s}: {int(quantity):2d} 块 × {prices[i]:4d}元 = {cost:6.0f}元")
            total_cost += cost
    print()
    print(f"总成本: {total_cost:.0f}元")
    print()
    
    # 验证满足的通道需求
    satisfied_channels = A.T @ result.x
    print("满足的通道需求:")
    has_output = False
    for i, channel_type in enumerate(channel_types):
        if b_requirements[i] > 0 or satisfied_channels[i] > 0.01:
            status = "[OK]" if satisfied_channels[i] >= b_requirements[i] else "[不足]"
            print(f"  {status} {channel_type:25s}: {satisfied_channels[i]:5.0f} (需求: {b_requirements[i]:5.0f})")
            has_output = True
    if not has_output:
        print("  (无有效通道需求)")
else:
    print("✗ 求解失败:", result.message)
