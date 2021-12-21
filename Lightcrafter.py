# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 14:53:22 2021

@author: Jean

PREVIOUS AUTHOR (matlab): Jan Winter, TU Berlin, FG Lichttechnik j.winter@tu-berlin.de
LICENSE: free to use at your own risk. Kudos appreciated.
"""
import socket
import numpy as np

def convert_bits(a):
    bnr = bin(a).replace('0b','')
    x = bnr[::-1] #this reverses an array
    while len(x) < 8:
        x += '0'
    bnr = x[::-1]
    return bnr    

class Lightcrafter:
        
    def __init__(self,tcp_ip,port):
        self.tcp_ip=tcp_ip
        self.port=port
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)

    def connect(self):
        TCP_IP = self.tcp_ip
        TCP_PORT = self.port
        try:
            self.socket.connect((TCP_IP, TCP_PORT))
        except:
            return False
        return True

    def disconnect(self):
        try:
            self.socket.close()
        except:
            pass
    
    def createHeader(self):
        return np.uint8(np.zeros(6))
    
    def appPayloadLengthToHeaderForPayload( self, header, payload ):
        payloadLength = len(payload)
        payloadLengthMSB = int(payloadLength/256)
        payloadLengthLSB = np.mod(payloadLength,256)
        
        header[4] = np.uint8( payloadLengthLSB ) #payloadLength LSB
        header[5] = np.uint8( payloadLengthMSB ) #payloadLength MSB
        
        return header
    
    def appChecksum( self,packet):
        checksum = np.mod( np.sum( packet ), 256 )
        return np.append(packet,checksum)
    
    def setdisplayModeStatic( self):
        header = self.createHeader()
        header[0] = np.uint8( 0x02 )	#packet type
        header[1] = np.uint8( 0x01 ) #CMD1
        header[2] = np.uint8( 0x01 ) #CMD2
        header[3] = np.uint8( 0x00 ) #flags
        header[4] = np.uint8( 0x01 ) #payloadLength LSB
        header[5] = np.uint8( 0x00 ) #payloadLength MSB
        payload = np.uint8( 0x00 ) #payload
        packet = self.appChecksum(np.append(header,payload) )
        #packet
        self.sendData( packet)
    
    def setdisplayModeInternalPattern(self):
        header = self.createHeader()
        header[0] = np.uint8( 0x02 )	#packet type
        header[1] = np.uint8( 0x01 ) #CMD1
        header[2] = np.uint8( 0x01 ) #CMD2
        header[3] = np.uint8( 0x00 ) #flags
        header[4] = np.uint8( 0x01 ) #payloadLength LSB
        header[5] = np.uint8( 0x00 ) #payloadLength MSB
        payload = np.uint8( 0x01 ) #payload
        packet = self.appChecksum( np.append(header,payload) )
        #packet
        self.sendData( packet)

    def setdisplayModePatternSequence(self):
        header = self.createHeader()
        header[0] = np.uint8( 0x02 )	#packet type
        header[1] = np.uint8( 0x01 ) #CMD1
        header[2] = np.uint8( 0x01 ) #CMD2
        header[3] = np.uint8( 0x00 ) #flags
        header[4] = np.uint8( 0x01 ) #payloadLength LSB
        header[5] = np.uint8( 0x00 ) #payloadLength MSB
        payload = np.uint8( 0x04 ) #payload
        packet = self.appChecksum( np.append(header,payload) )
        #packet
        self.sendData( packet)
    
    def setdisplayPatternSequenceSettings(self,bit_depth=1,nb_pattern=4):
        header = self.createHeader()
        header[0] = np.uint8( 0x02 )	#packet type
        header[1] = np.uint8( 0x04 ) #CMD1
        header[2] = np.uint8( 0x00 ) #CMD2
        header[3] = np.uint8( 0x00 ) #flags
        
        exp=[0x11,0x10,0x01,0x10]
        trig=[0x00,0x00,0x00,0x00]+[0x00,0x00,0x00,0x00]
        payload = np.uint8( [0x01,0x04,0x01,0x00]+trig+exp+[0x02]) #payload
        
        self.appPayloadLengthToHeaderForPayload(header, payload)
        packet = self.appChecksum( np.append(header,payload) )
        #packet
        self.sendData( packet)
    
    def setPattern( self, pattern):
        #self.setdisplayModeInternalPattern()
        
        header = self.createHeader()
        header[0] = np.uint8( 0x02 )	#packet type
        header[1] = np.uint8( 0x01 ) #CMD1
        header[2] = np.uint8( 0x03 ) #CMD2
        header[3] = np.uint8( 0x00 ) #flags
        header[4] = np.uint8( 0x01 ) #payloadLength LSB
        header[5] = np.uint8( 0x00 ) #payloadLength MSB
        payload = np.uint8( pattern ) #payload
        packet = self.appChecksum( np.append(header,payload) )
        #packet
        self.sendData( packet)
    
    def setStaticColor( self, R, G, B):
        self.setdisplayModeStatic()
        
        header = self.createHeader()
        header[0] = np.uint8( 0x02 )	#packet type
        header[1] = np.uint8( 0x01 ) #CMD1
        header[2] = np.uint8( 0x06 ) #CMD2
        header[3] = np.uint8( 0x00 ) #flags
        header[4] = np.uint8( 0x03 ) #payloadLength LSB
        header[5] = np.uint8( 0x00 ) #payloadLength MSB
        
        payload = np.uint8( np.array([R,G,B]) ) #payload

        packet = self.appChecksum( np.append(header,payload) )
        #packet
        self.sendData( packet)
            
    
    def setBMPImage( self, imageData):
        #self.setdisplayModeStatic()
        
        MAX_PAYLOAD_SIZE = 512*32
        numberOfChunks = np.ceil( imageData.size / 65535 )
        #print(numberOfChunks)
# =============================================================================
#         for i in range(int(numberOfChunks)):
#             currentLength = imageData.size
#             if( currentLength > MAX_PAYLOAD_SIZE ):
#                 chunkArray.append(imageData[0 : MAX_PAYLOAD_SIZE])
#                 imageData = imageData[MAX_PAYLOAD_SIZE :]
#             else:
#                 chunkArray.append(imageData[0:])
#             
#         for currentChunkIndex in range(int(numberOfChunks)):
#             
#             currentChunk = chunkArray[currentChunkIndex]
# =============================================================================
        for currentChunkIndex in range(int(numberOfChunks)):
            
            currentLength = imageData.size
            
            if( currentLength > MAX_PAYLOAD_SIZE ):
                currentChunk=imageData[0 : MAX_PAYLOAD_SIZE]
                imageData = imageData[MAX_PAYLOAD_SIZE :]
            else:
                currentChunk=imageData           
            
            
            header = self.createHeader()
            header[0] = np.uint8( 0x02 )	#packet type
            header[1] = np.uint8( 0x01 ) #CMD1
            header[2] = np.uint8( 0x05 ) #CMD2
            header = self.appPayloadLengthToHeaderForPayload( header, currentChunk )
            
            #app flag
            if( numberOfChunks == 1 ):
                header[3] = np.uint8( 0x00 ) #flags
            else:
                if( currentChunkIndex == 0 ):
                    #print('FIRST CHUNK')
                    header[3] = np.uint8( 0x01 ) #flags
                elif( currentChunkIndex == numberOfChunks-1 ):
                    #print('LAST CHUNK')
                    header[3] = np.uint8( 0x03 ) #flags
                else:
                    #print('OTHER CHUNK')
                    header[3] = np.uint8( 0x02 ) #flags
            
            packet = self.appChecksum(np.append(header,currentChunk))
            self.sendData( packet)

    def sendData( self, packet):
        #limit packet size
        MAX_SIZE = 65535#512*8
        buffer = packet
        #print(packet)
        while buffer.any():
            if( len(buffer) > MAX_SIZE ):
                currentPacket = buffer[0 : MAX_SIZE]
                buffer = buffer[MAX_SIZE:]        
            else:
                currentPacket = buffer
                buffer = np.array([])

            #print(bytes(list(currentPacket)))
            self.socket.send(bytes(list(currentPacket))) 
            #print('wrote some data')
