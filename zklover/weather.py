wth = {
    0: '晴',
    1: '多云',
    2: '阴',
    3: '阵雨',
    4: '雷阵雨',
    5: '雷阵雨伴有冰雹',
    6: '雨夹雪',
    7: '小雨',
    8: '中雨',
    9: '大雨',
    10: '暴雨',
    11: '大暴雨',
    12: '特大暴雨',
    13: '阵雪',
    14: '小雪',
    15: '中雪',
    16: '大雪',
    17: '暴雪',
    18: '雾',
    19: '冻雨',
    20: '沙尘暴',
    21: '小到中雨',
    22: '中到大雨',
    23: '大到暴雨',
    24: '暴雨到大暴雨',
    25: '大暴雨到特大暴雨',
    26: '小到中雪',
    27: '中到大雪',
    28: '大到暴雪',
    29: '浮尘',
    30: '扬沙',
    31: '强沙尘暴',
    53: '霾'
}
windDirect = {
    0: '北风',
    45: '东北风',
    90: '东风',
    135: '东南风',
    180: '南风',
    225: '西南风',
    270: '西风',
    315: '西北'
}


def windDri(win):
    if win in windDirect.keys():
        return windDirect[win]
    else:
        if 0 < win < 45:
            return '北偏东'
        if 45 < win < 90:
            return '东偏北'
        if 90 < win < 135:
            return '东偏南'
        if 135 < win < 180:
            return '南偏东'
        if 180 < win < 225:
            return '南偏西'
        if 225 < win < 270:
            return '西偏南'
        if 270 < win < 315:
            return '西偏北'
        if 315 < win < 360:
            return '北偏西'


def windlevel(speed):
    if speed <= 0.2:
        return "微风"
    elif 0.2 < speed <= 1.5:
        return "1级"
    elif 1.5 < speed <= 3.3:
        return "2级"
    elif 3.3 < speed <= 5.4:
        return "3级"
    elif 5.4 < speed <= 7.9:
        return "4级"
    elif 7.9 < speed <= 10.7:
        return "5级"
    elif 10.7 < speed <= 13.8:
        return "6级"
    elif 13.8 < speed <= 17.1:
        return "7级"
    elif 17.1 < speed <= 20.7:
        return "8级"
    elif 20.7 < speed <= 24.4:
        return "9级"
    elif 24.4 < speed <= 28.4:
        return "10级"
    elif 28.4 < speed <= 32.6:
        return "11级"
    elif 32.6 < speed <= 132:
        return "12级以上"
