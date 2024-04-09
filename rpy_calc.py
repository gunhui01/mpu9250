import math

gyro_rpy = [0, 0, 0]

### 로우 패스 필터 ###
def lpf(weight, pre_x, x):
    return weight * pre_x + (1 - weight) * x

### 하이 패스 필터 ###
def hpf(weight, pre_x, x):
    return x - lpf(weight, x, pre_x)

### ACC값을 통한 Roll, Pitch 계산 ###
def rp_acc(a_x, a_y, a_z):
    roll = math.degrees(math.atan2(a_y, a_z))
    pitch = math.degrees(math.atan2(a_x, a_z))
    return roll, pitch

### MAG값을 통한 Yaw 계산 ###
def y_mag(m_x, m_y):
    return math.degrees(math.atan2(m_y, m_x))

def rpy_return(rate, data):
    pre_data = [0, 0, 0]
    rpy = [0, 0, 0]

    rp_acc_list = rp_acc(data[0], data[1], data[2])

    gyro_rpy[0] += hpf(0.02, pre_data[0], rate * data[3])
    pre_data[0] = rate * data[3]

    gyro_rpy[1] += hpf(0.02, pre_data[1], rate * data[4])
    pre_data[1] = rate * data[4]

    gyro_rpy[2] += hpf(0.02, pre_data[2], rate * data[5])
    pre_data[2] = rate * data[5]

    #rpy[0] = 0.8 * gyro_rpy[0] + 0.2 * rp_acc_list[0]
    #rpy[1] = 0.8 * gyro_rpy[1] + 0.2 * rp_acc_list[1]
    rpy[0] = rp_acc_list[0]
    rpy[1] = rp_acc_list[1]
    rpy[2] = gyro_rpy[2]

    return rpy