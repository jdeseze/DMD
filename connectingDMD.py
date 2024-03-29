# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 11:36:19 2021

@author: Jean
"""
import streamlit as st
import socket
from Lightcrafter import Lightcrafter
from PIL import Image
import numpy as np
import pycromanager as pm
#pip install pythonnet
import clr
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas
import time
import copy
from skimage import measure
from scipy import ndimage

def main():
    st.set_page_config(page_title="DMD", page_icon=":microscope:",layout="wide")
    
    #Initialize variables
    
    #dmdzone is tthe mask of the zone of the dmd in the field of view of the app (defined as 512,512)
    if 'dmd_zone' not in st.session_state:
        st.session_state.dmd_zone=np.array(Image.open('dmd_zone.png'))
        st.session_state.cropped_index=np.ix_((st.session_state.dmd_zone>0).any(1),(st.session_state.dmd_zone>0).any(0))
    
    if 'cropped_index' not in st.session_state:
            st.session_state.cropped_index=np.ix_((st.session_state.dmd_zone>0).any(1),(st.session_state.dmd_zone>0).any(0))
        
    if 'show_image' not in st.session_state:
        st.session_state['show_image']=False
    
    #dmd is what will be sent to the dmd
    if 'dmd' not in st.session_state:
        st.session_state.dmd=np.zeros((int(1140/2),912))
    
    c1,c2,c3=st.columns([1,2,1])
    with c1:
        st.session_state.soft=st.radio('Software',['Metamorph','Micromanager'])
        
        if st.session_state.soft=='Metamorph':
            clr.AddReference(r'D:\JEAN\DMD\Interop.MMAppLib.dll')
            import MMAppLib
            st.session_state.mm=MMAppLib.UserCallClass()
            
        if st.button('Connect DMD'):
            TCP_IP = '192.168.7.2'
            TCP_PORT = 0x5555
            if False:#st.session_state.Lstate:
                st.write('DMD already connected')
                st.session_state.cropped_index=np.ix_((st.session_state.dmd_zone>0).any(1),(st.session_state.dmd_zone>0).any(0))
                image_with_seg(np.zeros((512,512)),contour(st.session_state.dmd_zone))
            else:
                st.session_state.L=Lightcrafter(TCP_IP,TCP_PORT)
                st.session_state.Lstate=st.session_state.L.connect()
                time.sleep(1)
            
            if st.session_state.Lstate:
                st.write('DMD connected')
                st.session_state.L.setStaticColor(0xf,0xf,0xf)
                time.sleep(2)
                st.session_state.L.setdisplayModeStatic()
                st.session_state.cropped_index=np.ix_((st.session_state.dmd_zone>0).any(1),(st.session_state.dmd_zone>0).any(0))
                image_with_seg(np.zeros((512,512)),contour(st.session_state.dmd_zone))
            else: 
                st.write('Unable to connect DMD')
        
        if st.button('Send previous pattern to DMD'):
            send_previous_pattern()
            
        if st.button('Send pattern to DMD'):
            send_pattern()
        
        if st.button('Acquire'):
            acquire()
        
        st.session_state.drawing_mode = st.selectbox(
        "Drawing tool:", ("freedraw", "line", "rect", "circle", "transform")
        )
        st.session_state.stroke_width = st.slider("Stroke width: ", 1, 25, 3)
        
        if st.button('Define as DMD zone'):
            st.session_state.dmd_zone=copy.deepcopy(st.session_state.mask_act)
            #look at the index of the dmd_zone
            st.session_state.cropped_index=np.ix_((st.session_state.dmd_zone>0).any(1),(st.session_state.dmd_zone>0).any(0))
            image_with_seg(np.zeros((512,512)),contour(st.session_state.dmd_zone))
            #st.session_state.mask_act=np.zeros((512,512))

        if st.button('calibrate'):
            st.session_state.dmd=np.zeros((570,912))
            st.session_state.dmd[150:420,321:591]=1
            send_pattern()
            acquire()            
            'draw the square you see on the image'
            
            'calibration is done!'
                
                
        
    with c2:  
        if st.session_state.show_image:
            make_canvas()
            st.session_state.mask_act=np.mean(st.session_state.canvas_result.image_data,axis=2)>0
            plt.imshow(st.session_state.mask_act,cmap='gray')
            st.session_state.canvasfig.savefig('mask.png',bbox_inches="tight",pad_inches = 0)

            cropped_image=st.session_state.mask_act[st.session_state.cropped_index].astype(np.uint8).T
            st.session_state.dmd=np.array(Image.fromarray(cropped_image).resize((int(1140/2),912))).astype(np.uint8)
            im=Image.fromarray(st.session_state.dmd)
            #im.convert('L')
            im.save('test.bmp')
            
    with c3:
        if st.session_state.show_image:
            st.image(st.session_state.dmd.T*255,use_column_width=True,output_format='PNG')    
        if st.button('save zone'):
            st.session_state.dmd_zone.savefig('dmd_zone.png')
            Image.fromarray(st.session_state.cropped_index).save('dmd_zone.png')
        if st.button('save act'):
            Image.fromarray(st.session_state.dmd).save('activation.png') 
        

def acquire():
    if st.session_state.soft=='Metamorph':
        st.session_state.mm.RunJournal('C:/MM/app/mmproc/journals/s.JNL')
        pixvals=np.array(Image.open(r'C:\TEMP\tmp.tif'))
    else:
        bridge=pm.Bridge()
        core=bridge.get_core()
        core.snap_image()
        tagged_img=core.get_tagged_image()
        pixvals=np.reshape(tagged_img.pix,newshape=[tagged_img.tags['Height'], tagged_img.tags['Width']])
    contrasted = ((pixvals - pixvals.min()) / (pixvals.max()-pixvals.min())) 
    st.session_state.disp_image=contrasted
    st.session_state.img_to_save=pixvals
    st.session_state.show_image=True  

def send_pattern():

    if not st.session_state.Lstate:
        st.write('DMD not connected')
    else:
        im=Image.fromarray((st.session_state.dmd.T*255).astype(np.uint8)).resize((912,1140))
        im.save('D:/JEAN/DMD/test.bmp')
        st.write('...')
        with open(r'D:/JEAN/DMD/test.bmp','rb') as opened:
            tosend=np.fromfile(opened,np.uint8).flatten()

        t1=time.time()
        st.session_state.L.setdisplayModeStatic()
        t2=time.time()
        time.sleep(1)
        t3=time.time()
        st.session_state.L.setBMPImage(tosend)
        t4=time.time()

# =============================================================================
#         time.sleep(2)
#         st.session_state.L.setdisplayModePatternSequence()
# =============================================================================
        time.sleep(1)
        st.session_state.L.setdisplayPatternSequenceSettings()
        t5=time.time()
        t2-t1
        t3-t1
        t4-t1
        t5-t1


def send_previous_pattern():
    if not st.session_state.Lstate:
        st.write('DMD not connected')
    else:
        im=Image.fromarray(((np.array(Image.open('activation.png'))>0).T*255).astype(np.uint8)).resize((912,1140))
        #im=Image.open('activation.png')
        im.save('D:/JEAN/DMD/test1.bmp')
        st.write('...')
        with open(r'D:/JEAN/DMD/test1.bmp','rb') as opened:
            tosend=np.fromfile(opened,np.uint8).flatten()
        st.session_state.L.setdisplayModeStatic()
        time.sleep(1)
        st.session_state.L.setBMPImage(tosend)
        time.sleep(1)
        st.session_state.L.setdisplayPatternSequenceSettings()
    
def make_canvas():
    img=np.array(st.session_state.disp_image)

    size_fig=(512,512)
    st.session_state.canvasfig = plt.figure(figsize=size_fig, dpi=1)
    b=plt.imshow(img,cmap='gray')
    b.axes.axis('off')
    plt.tight_layout()
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    st.session_state.canvasfig.savefig('canvas.png',bbox_inches="tight",pad_inches = 0)
    bg_image = Image.open('canvas.png')
    size_img=size_fig
    st.session_state.canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=st.session_state.stroke_width,
        stroke_color="#000000",
        background_color="",
        background_image=bg_image,
        update_streamlit=True,
        height=size_img[1],
        width=size_img[0],
        drawing_mode=st.session_state.drawing_mode,
        key="canvas",
    )

def contour(binary):
    #img=(img/2^8).astype(np.uint8)
    label_img, cc_num = ndimage.label(binary)

    contours = measure.find_contours(label_img)
    if len(contours)>0:
        contour=contours[0]
    else:
        contour=np.array([None])
    return contour

def image_with_seg(img,contour):
    fig = plt.figure()
    #original image
    a=plt.imshow(img,cmap='gray')
    #find mask and contour
    if contour.any():        
        a.axes.plot(list(map(int,contour[:, 1])), list(map(int,contour[:, 0])), linewidth=2)
    a.axes.get_xaxis().set_visible(False)
    a.axes.get_yaxis().set_visible(False)
    return fig

if __name__ == "__main__":
    main()