
from Crypto.Random import get_random_bytes
from cpake import generate_kyber_keys, encrypt, decrypt
from params import KYBER_512SK_BYTES, KYBER_768SK_BYTES, KYBER_1024SK_BYTES, KYBER_SYM_BYTES, KYBER_SS_BYTES, \
    KYBER_INDCPA_SECRETKEY_BYTES_K512, KYBER_INDCPA_PUBLICKEYBYTES_K512, \
    KYBER_INDCPA_SECRETKEY_BYTES_K768, KYBER_INDCPA_PUBLICKEYBYTES_K768, \
    KYBER_INDCPA_SECRETKEY_BYTES_K1024, KYBER_INDCPA_PUBLICKEYBYTES_K1024
from Crypto.Hash import SHA3_256, SHA3_512, SHAKE256
from util import cast_to_byte
from ccakem import kem_keygen512, kem_encaps512, kem_decaps512, kem_keygen768, kem_encaps768, kem_decaps768, \
    kem_keygen1024, kem_encaps1024, kem_decaps1024
    
def intlist(x):
    y = bytearray.fromhex(x)
    return [ cast_to_byte(i) for i in y]

def cast(x):
    return [ cast_to_byte(i) for i in x]


def kem_keygen512_fips203(rnd, z):
    """
    generate kyber keys for security level 512
    :input random number rnd(d in fips203) and z
    :return: tuple of (private_key(dk in FIPS203), public key(ek in FIPS203)), each a byte array
    :return H_pk only for test your own implementation
    """
    
    params_k = 2
    sk_, pk = generate_kyber_keys(params_k,rnd)

    md = SHA3_256.new()
    md.update(bytearray([x & 0xFF for x in pk]))
    H_pk = md.digest()
    H_pk = [ cast_to_byte(x) for x in H_pk ]
    pkh = [0 for x in range(0, len(H_pk))]
    for i in range(0, len(H_pk)):
        pkh[i] = H_pk[i]

    z = [ cast_to_byte(x) for x in z]

    sk = sk_[:] + pk[:] + H_pk[:] + z[:]

    return (sk, pk, H_pk)


def kem_encaps512_fips203(pubkey, m):
    """
    enc for security level 512
    : input public key(ek in FIPS203) and message(m in FIPS203)
    :return: tuple of (shared secret(K in FIPS203) and cipher(c in FIPS203)), each a byte array
    """

    params_k = 2

    m = [ cast_to_byte(x) for x in m ]

    md = SHA3_256.new()
    md.update(bytearray([x & 0xFF for x in pubkey]))
    Hpk = md.digest()
    Hpk = [ cast_to_byte(x) for x in Hpk ]

    #m = Hm + Hpk
    m = m + Hpk

    md512 = SHA3_512.new()
    md512.update(bytearray([x & 0xFF for x in m]))
    kr = md512.digest()
    kr = [ cast_to_byte(x) for x in kr]
    K = kr[0:KYBER_SYM_BYTES]          # k for fips203
    #print(K)
    r = [ kr[i + KYBER_SYM_BYTES] for i in range(0, len(kr) - KYBER_SYM_BYTES)]
    #c = encrypt(Hm, pubkey, r, params_k)
    c = encrypt(m, pubkey, r, params_k)

    md = SHA3_256.new()
    md.update(bytearray([x & 0xFF for x in c]))
    Hc = md.digest()
    Hc = [ cast_to_byte(x) for x in Hc ]
    KHc = K + Hc

    xof = SHAKE256.new()
    xof.update(bytearray([ x & 0xFF for x in KHc]))
    shared_secret = xof.read(KYBER_SYM_BYTES)
    shared_secret = [ cast_to_byte(x) for x in shared_secret]
    return K, c


def kem_decaps512_fips203(private_key, ciphertext):
    """

    :param private_key(dk in FIPS203):
    :param ciphertext(c in FIPS203):
    :return: (shared_secret(K in FIPS203))
    """
    params_k = 2
    sk = private_key[0: KYBER_INDCPA_SECRETKEY_BYTES_K512]
    pk = private_key[KYBER_INDCPA_SECRETKEY_BYTES_K512:KYBER_INDCPA_SECRETKEY_BYTES_K512+KYBER_INDCPA_PUBLICKEYBYTES_K512]
    z = private_key[KYBER_512SK_BYTES - KYBER_SYM_BYTES:]
    h = private_key[KYBER_512SK_BYTES - 2 * KYBER_SYM_BYTES:KYBER_512SK_BYTES - KYBER_SYM_BYTES]
    m_ = decrypt(ciphertext, sk, params_k)   #m'=K-PKE.Decrypt(dkpke,c)

    md512 = SHA3_512.new()
    md512.update(bytearray([ x & 0xFF for x in (m_[:] + h[:])]))
    K_r_ = md512.digest()    #(k',r') = G(m'||h)
    
    K_r_ = [ cast_to_byte(x) for x in K_r_ ]
    K_ = K_r_[0:KYBER_SYM_BYTES]  #k'
    r_ = K_r_[-KYBER_SYM_BYTES:]    #r'
    
    zc = z + ciphertext
    
    cmp = encrypt(m_, pk, r_, params_k)
    
    if(cmp == ciphertext):
        sharedSecretFixedLength = K_
        print("decaps correct")
    else:
        temp_buf = z[:] + ciphertext   
        xof = SHAKE256.new()
        xof.update(bytearray([ x & 0xFF for x in tmp_buf]))
        sharedSecretFixedLength = xof.read(KYBER_SS_BYTES)
        sharedSecretFixedLength = [cast_to_byte(x) for x in sharedSecretFixedLength]
    
    return sharedSecretFixedLength



############### test key generation of kyber512 ##############################

rnd = "7c9935a0b07694aa0c6d10e4db6b1add2fd81a25ccb148032dcd739936737f2d"  # the random number d that used in my verilog implementation (in hex)
rnd = bytearray.fromhex(rnd)  # trans. rnd into the form that the python model can use

z = "8626ed79d451140800e03b59b956f8210e556067407d13dc90fa9e8b872bfb8f"# the random number z that used in my verilog implementation
z = bytearray.fromhex(z)

h_verilog = "7ffad1bc8af73b7e874956b81c2a2ef0bfabe8dc93d77b2fbc9e0c64efa01e84" # the H(ek) that generated by my verilog implementation
h_test = intlist(h_verilog) # trans. h_verilog into the form that the python model used

priv, pub, h = kem_keygen512_fips203(rnd,z)  # key generation based on the input data
print("h(ek) generated by python model=",h)
print("h(ek) generated by verilog=",h_test)
assert(h == h_test)


############## test kem-encapsulation of kyber512 ############################### 
m=  "147c03f7a5bebba406c8fae1874d7f13c80efe79a3a9a874cc09fe76f6997615"# the message m that used in my verilog implementation
m = bytearray.fromhex(m)

k_verilog = "c608777086ed9ffdf92cd4f1c999aedd0b42e5e8ef6732f4111246481e260463"# the shared secret K that generated by my verilog implementation
k_test = intlist(k_verilog)

# c generated by my verilog implementation
c_test="7549998d469e2e479002305b09b44dbadbc2457ffd3125f6d31b0f27b803d581071c1dc6181196fe76df78de20dda609cf1b7cb7a352c4dd9c2cfc18801f036fe40f8f7e6f3dd73f387130be387b1713418f83d93dc7f8074a032455c46f857c6b6b35429c790065420d742252ee53f53f6e64a9b78a49bc29b8ce84831a01c3429e346960dc559526d97853c36631b4773285fafe8e3ca4255a8723ae4f02ddd85a4781b9f4186d67a83b5d9eddc3ae7cd4096c33f4d97fe02030ecb6a1a8ad9b19d3eb32f1b8f271b30353e9e19dd183f06b54c3cb02ef166282752aa11c8158e48bbc6830171ca7ddb75a35e46c35321abe6a742032c772a16b3d1cddfc6f2801e2b817302dbc94f333c0cb91e1cebd5ec61e49fa5a14aaa393755fc3e6f4b8c5c4fa4baa07a08c4f3394626358a15e690ee1e4829b111c17241aee37d5c832f4847688fe5b5d1b19e8e04d9d1937001987f3b4b83549c3e530e4119d164b20ef9d3a72f74c044a974591228b41e680ec5640a97234c2c6017c95e91be2bd498547d57a5222b8162a3546656d59980d51af595bf5f23a632f6d8544b81074aed34c0352ba560deafb07441a55a9376342e50a0ec2537228255a4b5d03c92957f4ea3507b4baadce53ccdfb7364ffc1817b58c50ef28e322e1b945e0eb9b1233975c30a5545368682714bf502b61e1d0457a9753e10de0f1bf35ec3a3f470a3c69ccb04d2d98fab3a0b6729a9875e1db533c96b41e3d98628a6f8cf668406c5f038e6b7b242fdf86a7f1e697aeb136114167b13f89f231bcec7a4166b39eab4a3709237822050c49c92595a237f2eb483b9e1dd6124bed5eb9b7b5121296376b7d2014a77560ca65833d8beb4d6ae68efd7a11acc7de87d82be1ad573ae9f6f0766fd786387d1a8c12d1c8a296b4f72634f70577688848e576851f13be48df335d4acd89793a6c6c0655fc39bc9e1e27b4a500f708cd4a9f2ec672ba5bf8ad23998d4c0c958f290f2a6c4e6cd8c0cdc85f5716ec98a4c8995d378cc6e2a1e8b82800ddf03b3226a2e7817771e509b4955ee2bed4217bdf0630b5840f2524ab"
c_test = intlist(c_test)

K_for_fips203, cipher = kem_encaps512_fips203(pub,m) # encaps.
print("k for fips203 generated by python=",K_for_fips203)
print("k generated by verilog=",k_test)
assert(K_for_fips203 == k_test)

print("c_test generated my verilog=",c_test)
print("cipher or fips203 generated by python model=",cipher)
assert(c_test == cipher)

############ test kem-decaps of kyber512  #####################################
k_verilog = "c608777086ed9ffdf92cd4f1c999aedd0b42e5e8ef6732f4111246481e260463"# the shared secret K that generated by my verilog implementation
k_test = intlist(k_verilog)

K_ = kem_decaps512_fips203(priv, cipher)
print("k' generated by decaps of python model=",K_)
assert(K_for_fips203 == K_)










