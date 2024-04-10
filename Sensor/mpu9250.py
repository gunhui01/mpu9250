import os
import os.path
import numpy as np
import smbus
import time
import warnings

from Sensor.rpy_calc import *
from Sensor.weather import *

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

class Mpu:
    def __init__(self, i2cbus, mpu_status):
        self.i2c = smbus.SMBus(i2cbus)
        self.i2cbus = i2cbus
        self.mpu_status = mpu_status

        if(mpu_status == "hi"): self.MPU = 0x69
        elif(mpu_status == "lo"): self.MPU = 0x68
        else:
            print("MPU9250 상태 입력 오류!\nAD0 핀이 3.3V에 연결되어 있으면 hi, Ground에 연결되어 있으면 lo를 입력하세요.\n")
            exit()

        ### 센서 연결 확인, 초기 설정 ###
        print("==========<" + str(self.i2cbus) + ", " + self.mpu_status.upper() + ">==========")
        if(self.read_one_byte(self.MPU, MPU_WAI) == 0x71):
            print("[MPU9250] 연결 확인.")
        else:
            print("[MPU9250] 연결 실패!")
            exit()

        self.write_data(self.MPU, INT_PIN_CFG, 0b10)
        print("[MPU9250] Bypass 설정 성공.")

        if(self.read_one_byte(AK, AK_WAI) == 0x48):
            print("[AK8963] 연결 확인.")
        else:
            print("[AK8963] 연결 실패!")
            exit()

        ### csv 파일 생성 확인, 없을 시 생성 ###
        self.dir_name = os.path.dirname(os.path.realpath(__file__))

        if not os.path.isfile(self.dir_name + "/i2c" + str(i2cbus) + '_' + mpu_status + ".csv"):
            os.system("touch " + self.dir_name + "/i2c" + str(i2cbus) + '_' + mpu_status + ".csv")
            os.system("echo timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z >> " + self.dir_name + "/i2c" + str(i2cbus) + '_' + mpu_status + ".csv")
        
        self.csv = open(self.dir_name + "/i2c" + str(i2cbus) + '_' + mpu_status + ".csv", 'a')

        ### 센서 조정 ###
        self.calibration_data = self.calibration()

    def __del__(self):
        ### 종료시 센서 설정 ###
        print("==========<" + str(self.i2cbus) + ", " + self.mpu_status.upper() + ">==========")
        self.write_data(AK, CNTL_1, 0b0)
        print("[AK8963] 센서 종료 설정 완료.")
        self.write_data(self.MPU, INT_PIN_CFG, 0b0)
        print("[MPU9250] 센서 종료 설정 완료.")

        self.csv.close()
        print("파일 닫기 완료.")

    def calibration(self):
        calibration_data = [0, 0, 0]

        print("센서 조정을 시작합니다. 센서를 움직이지 않게 고정하세요.")
        for i in range(10): calibration_data[0] += self.read_mpu_data(GYRO_X)
        for i in range(10): calibration_data[1] += self.read_mpu_data(GYRO_Y)
        for i in range(10): calibration_data[2] += self.read_mpu_data(GYRO_Z)

        for i in range(3): calibration_data[i] /= 10
        print("센서 조정 완료.")

        return calibration_data

    ### MPU9250에서 가속도, 자이로 값 받아옴 ###
    def read_mpu_data(self, reg):
        data_list = self.i2c.read_i2c_block_data(self.MPU, reg, 2)
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

    ### csv 파일에 데이터 씀 ###
    def agm_data_out(self):
        self.csv.write(time.strftime("%Y.%m.%d %H:%M:%S") + ',')
        self.csv.write(str(self.read_mpu_data(ACCEL_X)) + ',')
        self.csv.write(str(self.read_mpu_data(ACCEL_Y)) + ',')
        self.csv.write(str(self.read_mpu_data(ACCEL_Z)) + ',')
        self.csv.write(str(self.read_mpu_data(GYRO_X)) + ',')
        self.csv.write(str(self.read_mpu_data(GYRO_Y)) + ',')
        self.csv.write(str(self.read_mpu_data(GYRO_Z)) + ',')
        self.write_data(AK, CNTL_1, 0b1111)
        self.csv.write(str(self.read_ak_data(MAG_X, ASA_X)) + ',')
        self.csv.write(str(self.read_ak_data(MAG_Y, ASA_Y)) + ',')
        self.csv.write(str(self.read_ak_data(MAG_Z, ASA_Z)) + '\n')
        self.write_data(AK, CNTL_1, 0b10110)
    
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

        return a_x, a_y, a_z, g_x, g_y, g_z, m_x, m_y, m_z
    
    def agm_weather_data_return(self, api_key, station_id):
        agm_weather_data = list(self.agm_data_return())

        weather_data = weather_return(api_key, station_id)
        agm_weather_data.append(weather_data["temperature"])
        agm_weather_data.append(weather_data["humidity"])
        agm_weather_data.append(weather_data["wind_direction"])
        agm_weather_data.append(weather_data["wind_speed"])
        agm_weather_data.append(weather_data["pressure"])

        return agm_weather_data
    
    def calibrationed_agm_data_return(self):
        raw_data = self.agm_data_return()
        calibrationed_data = list(raw_data)
        #calibrationed_data[6] -= 24.3 # MAG_X offset
        #calibrationed_data[7] -= 1.4 # MAG_Y offset
        for i in range(3, 6): calibrationed_data[i] -= self.calibration_data[i - 3]
        return calibrationed_data