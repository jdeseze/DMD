# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 15:14:30 2021

@author: Jean
"""

from Lightcrafter import Lightcrafter
from PIL import Image
import numpy as np

TCP_IP = '192.168.7.2'
TCP_PORT = 0x5555

mask=np.zeros((1140,912))
#mask[0:100,0:100]=255
mask=mask.astype(np.uint8)
im=Image.fromarray(mask)
#im.convert('L')
im.save('test.bmp')
with open(r'D:/JEAN/DMD/test8.bmp','rb') as opened:
    tosend=np.fromfile(opened,np.uint8).flatten()

L=Lightcrafter(TCP_IP,TCP_PORT)
L.connect()
L.setStaticColor(0xf,0xf,0xf)

L.setdisplayModeInternalPattern()
L.setPattern(0x7)

L.setdisplayModeStatic()
L.setBMPImage(tosend)

L.setdisplayModePatternSequence()
L.setdisplayPatternSequenceSettings()



#L.disconnect()


# =============================================================================
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 
# # =============================================================================
# # MESSAGE = b'\x04\x01\x01\x50'
# # MESSAGE = b'\x02\x01\x01\x00\x01\x00\x01\x06'
# # 
# # =============================================================================
# s.settimeout(1)
# s.connect((TCP_IP, TCP_PORT))
# 
# MESSAGE=bytes([2,1,3,0,1,0,1,8])
# s.send(MESSAGE)
# 
# MESSAGE = b'\x02\x01\x03\x00\x01\x00\x01\x08'
# s.send(MESSAGE)
# 
# try:
#     data = s.recv(BUFFER_SIZE)
#     s.close()
#     print("received data:"+str(data))
# except:
#     print('time out')
#     s.close()
# 
# =============================================================================

