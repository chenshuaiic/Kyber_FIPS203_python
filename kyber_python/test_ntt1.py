from poly import poly_from_bytes
from params import KYBER_N, KYBER_Q, KYBER_POLY_COMPRESSED_BYTES_768, \
    KYBER_POLY_COMPRESSED_BYTES_1024, KYBER_POLY_BYTES, KYBER_SYM_BYTES, \
    KYBER_ETAK512, KYBER_ETAK768_1024, KYBER_POLYVEC_COMPRESSED_BYTES_K512, \
    KYBER_POLYVEC_COMPRESSED_BYTES_K768, KYBER_POLYVEC_COMPRESSED_BYTES_K1024
import struct

n = 256
q = 3329


def dec_to_hex(num):
    base = [str(x) for x in range(10)] +[chr(x) for x in range(ord('a'),ord("a")+6)] # 前者把 0 ~ 9 转换成字符串存进列表 base 里，后者把 A ~ F 存进列表
    l = []
    if num<0:
       return "-"+dec_to_hex(abs(num))
    while True:
        num,rem = divmod(num,16) # 求商 和 留余数
        l.append(base[rem])
        if num == 0:
            return "".join(l[::-1])


coefficients = [0, 1, 0, 1, 3, 3328, 1, 1, 1, 3327, 3328, 0, 1, 3328, 1, 3328, 1, 2, 0, 0, 1, 2, 0, 2, 3327, 0, 0, 1, 3328, 1, 1, 3326, 3328, 2, 3328, 3327, 0, 3328, 1, 1, 2, 1, 0, 3328, 1, 2, 0, 1, 3328, 3328, 3328, 1, 0, 0, 2, 1, 3327, 0, 3327, 3328, 1, 1, 0, 1, 0, 0, 0, 3328, 1, 3328, 3328, 3328, 2, 0, 0, 1, 3327, 3328, 0, 0, 2, 0, 1, 0, 0, 3328, 1, 0, 3328, 1, 1, 1, 3327, 2, 3327, 1, 1, 1, 3328, 2, 1, 2, 2, 1, 3328, 3327, 2, 1, 1, 3327, 2, 1, 3328, 2, 1, 0, 0, 3328, 3328, 1, 1, 3328, 1, 3328, 0, 3327, 0, 3327, 3326, 1, 3328, 1, 1, 1, 0, 0, 3328, 3328, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 3327, 0, 3326, 0, 0, 3328, 0, 0, 3328, 1, 1, 3328, 2, 0, 2, 0, 3328, 0, 0, 0, 3328, 0, 3328, 3328, 1, 0, 0, 0, 0, 0, 1, 0, 3328, 0, 1, 0, 1, 3328, 1, 3328, 3328, 0, 0, 3327, 0, 1, 3327, 3328, 2, 2, 3328, 3328, 0, 0, 3328, 1, 3327, 3328, 1, 1, 3328, 2, 3327, 3327, 1, 2, 3328, 3328, 1, 1, 1, 0, 1, 1, 2, 0, 3328, 3328, 1, 2, 3328, 2, 1, 3328, 1, 3328, 1, 1, 0, 0, 3328, 3328, 3328, 3327, 3328, 3327, 3328, 0, 0, 1, 0, 3328, 1, 1, 3327, 3328, 1, 1] 
    
    
#b=poly_from_bytes(coefficients)
b=dec_to_hex(q)
print(b)

with open("test_file.txt","w") as f:
    for i in range(0,256):
        b=dec_to_hex(coefficients[i])
        f.writelines(b+"\n")


'''
with open("test_file","wb") as f:
    for i in range(0,256):
        b=hex(coefficients[i])
        #lin=['%02X' % i for i in b]
        #s=struct.pack('B',coefficients[i])
        #c=bytes().fromhex(lin).decode('gb18030',"ignore")
        #for x in b:
        #s=struct.pack('B',x)
        f.write(hex(ord(coefficients[i])))
'''
