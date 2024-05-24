import os, smbus, time
import numpy as np
from data.rpy_calc import *
from config.config_loader import MAX_I2C_BUS_COUNT

### MPU9250 레지스터 ###
INT_PIN_CFG = 0x37
ACCEL_X = 0x3b
ACCEL_Y = 0x3d
ACCEL_Z = 0x3f
GYRO_X = 0x43
GYRO_Y = 0x45
GYRO_Z = 0x47
MPU_WAI = 0x75

### AK8963 레지스터 ###
AK = 0x0C
MAG_X = 0x03
MAG_Y = 0x05
MAG_Z = 0x07
CNTL_1 = 0x0A
ASA_X = 0x10
ASA_Y = 0x11
ASA_Z = 0x12
AK_WAI = 0x00

def str_mpu_addr(mpu_addr):
    if mpu_addr == 0x68:
        return "lo"
    elif mpu_addr == 0x69:
        return "hi"
    else:
        return "error"
    
def is_mpu_connected(i2cbus, mpu_addr):
    try:
        i2c = smbus.SMBus(i2cbus)
        if i2c.read_byte_data(mpu_addr, MPU_WAI) == 0x71:
            return True
        else: 
            return False
    except Exception as e:
        return False
    
class Mpu:
    def __init__(self, i2cbus, mpu_addr):
        self.i2c = smbus.SMBus(i2cbus)
        self.i2cbus = i2cbus
        self.mpu_addr = mpu_addr
        self.sensor_id = f"i2c{i2cbus}_{str_mpu_addr(mpu_addr)}"

        ### 센서 초기 설정 ###
        print(f"==========<{self.sensor_id}>==========")

        self.write_data(self.mpu_addr, INT_PIN_CFG, 0b10)
        print("  [MPU9250] Bypass setting complete.")

        if(self.read_one_byte(AK, AK_WAI) == 0x48):
            print("  [AK8963] Connected.")
        else:
            print("  [AK8963] Connection Failed!")

        ### 센서 조정 ###
        self.calibration_data = self.calibration()

    ### str 출력 시 출력 형식 지정 ###
    def __str__(self): 
        return f"i2c{self.i2cbus}_{self.mpu_addr}"

    ### 종료시 센서 설정 ###
    def __del__(self):
        try:
            # print(f"==========<{self.sensor_id}>==========")
            if is_mpu_connected(self.i2cbus, self.mpu_addr):
                self.write_data(self.mpu_addr, INT_PIN_CFG, 0b0)
                self.write_data(AK, CNTL_1, 0b0)
            # print("Sensor shut down.")
        except OSError:
            pass

    ### MPU9250에서 가속도, 자이로 값 받아옴 ###
    def read_mpu_data(self, reg):
        data_list = self.i2c.read_i2c_block_data(self.mpu_addr, reg, 2)
        raw = np.int16((data_list[0] << 8) | data_list[1])
        if(reg <= ACCEL_Z and reg >= ACCEL_X):
            ### ±2g : 16384 | ±4g : 8192 | ±8g : 4096 | ±16g : 2048 ###
            data = raw / 17042
            return data
        else:
            ### ±250dps : 131 | ±500dps : 65.5 | ±1000dps : 32.8 | ±2000dps : 16.4 ###
            data = raw / 131
            return data

    ### AK8963에서 지자기 값 받아옴 ###
    def read_ak_data(self, h_reg, asa_reg):
        data_list = self.i2c.read_i2c_block_data(AK, h_reg, 2)
        h = np.int16((data_list[1] << 8) | data_list[0]) * 0.15
        asa = self.i2c.read_i2c_block_data(AK, asa_reg, 1)[0]
        data = h * ((((asa - 128) * 0.5) / 128) + 1) # AK8963 데이터시트 8.3.11.
        return data

    ### 1Byte 읽음 ###
    def read_one_byte(self, adr, reg):
        return int.from_bytes(self.i2c.read_i2c_block_data(adr, reg, 1))

    ### 1Byte 씀 ###
    def write_data(self, adr, reg, com):
        command = [int(com)]
        self.i2c.write_i2c_block_data(adr, reg, command)
    
    ### 센서 데이터 반환 ###
    def agm_data_return(self):
        # ACCEL_X | ACCEL_Y | ACCEL_Z |  GYRO_X |  GYRO_Y |  GYRO_Z |  MAG_X  |  MAG_Y  |  MAG_Z  #
        #    0    |    1    |    2    |    3    |    4    |    5    |    6    |    7    |    8    #

        a_x = self.read_mpu_data(ACCEL_X)
        a_y = self.read_mpu_data(ACCEL_Y)
        a_z = self.read_mpu_data(ACCEL_Z)

        g_x = self.read_mpu_data(GYRO_X)
        g_y = self.read_mpu_data(GYRO_Y)
        g_z = self.read_mpu_data(GYRO_Z)

        self.write_data(AK, CNTL_1, 0b1111)
        m_x = self.read_ak_data(MAG_X, ASA_X)
        m_y = self.read_ak_data(MAG_Y, ASA_Y)
        m_z = self.read_ak_data(MAG_Z, ASA_Z)
        self.write_data(AK, CNTL_1, 0b10110)

        # 각 변수를 리스트로 반환
        return [a_x, a_y, a_z, g_x, g_y, g_z, m_x, m_y, m_z]
    
    ### 센서 데이터를 문자열로 변환하여 반환하는 함수 ###
    def agm_data_return_str(self):
        return ','.join(map(str, self.agm_data_return()))
    
        ### GYRO 센서 조정 ###
    def calibration(self):
        calibration_data = [0, 0, 0]

        #print("센서 조정을 시작합니다. 센서를 움직이지 않게 고정하세요.")
        for i in range(10): calibration_data[0] += self.read_mpu_data(GYRO_X)
        for i in range(10): calibration_data[1] += self.read_mpu_data(GYRO_Y)
        for i in range(10): calibration_data[2] += self.read_mpu_data(GYRO_Z)

        for i in range(3): calibration_data[i] /= 10
        #print("센서 조정 완료.")

        return calibration_data

    ### GYRO 센서 보정 후 데이터 반환 ###
    def calibrated_agm_data_return(self):
        calibrated_data = self.agm_data_return()

        for i in range(3, 6): calibrated_data[i] -= self.calibration_data[i - 3]
        return calibrated_data
    
        #calibrated_data[6] -= 24.3 # MAG_X offset
        #calibrated_data[7] -= 1.4 # MAG_Y offset

### 연결된 센서 확인 ###
active_sensors = []
print("=====< Connected Sensor >=====")
for i2cbus in range(1, MAX_I2C_BUS_COUNT+1):
    bus_status = []
    for mpu_addr in (0x68, 0x69):
        if is_mpu_connected(i2cbus, mpu_addr):
            active_sensors.append([i2cbus, mpu_addr])
            bus_status.append(str_mpu_addr(mpu_addr))
    if bus_status:
        print(f"  BUS {i2cbus} : {', '.join(bus_status)}")

sensors = []
for i in active_sensors:
    sensor = Mpu(i[0], i[1])
    sensors.append(sensor)