
import numpy as np
import struct
from matplotlib import pyplot as pl
from scipy import misc
from scipy import ndimage
#import pylab
#from pylab import *
#import Image



bound = 121*68*3 #THIS IS THE SIZE OF AND IMAGE 16*121*16*68*3 WHICH IS (1080,1920,3)rgb IMAGE

with open("capture/test-004.imv", 'rb') as f:
    data = f.read() #some 10 frames can be excluded while loading m_v file

size = data.__sizeof__()
ratio = int(size/bound)

def f(data):
    global ratio
    'returns generator by converting byte to right format'
    #one place for optimization -----------------loop can be reduced here by excluding first 10 frames
    for i in xrange(len(data)/4):
        base = i*4
        yield struct.unpack('b', data[base])
        yield struct.unpack('b', data[base+1])
        yield struct.unpack('h', data[base+2:base+4])

arr = f(data)
finalarr = [i[0] for i in arr]#i[0] taking first element of the tuple
ratio = int(len(finalarr)/bound) #taking number of frames to process
m_v = np.array(finalarr, dtype=int) #assigning the array to the np array
m_voriginal = m_v
frame=m_v.reshape((ratio,68,121,3))

def find_appropriate_frame(imax,jmax,add_thresmin,add_thresmax,sat_thres,frame_max,frame,lower_limit,minarea_lower_limit):
    maxsize=np.zeros(frame_max,dtype=int)
    i,j,count,frame_no,tmpj,totalarea=imax-1,0,0,0,0,0
    #start of third loop
    while True:
        #start of second loop
        while True:

            length=0
            #start of first loop
            while True:

                i_test,j_test,sat_test=frame[frame_no,i,j]
                if abs(i_test)+abs(j_test)>add_thresmin and abs(i_test)+abs(j_test)<add_thresmax and sat_test<sat_thres:

                    if count is not 1:
                        tmpj,count,j=j,1,j+1

                    else:
                        j+=1

                else:

                    if count is not 0:
                        count=0

                        if length<j-tmpj:
                            length=j-tmpj

                        j+=1

                    else:
                        j+=1

                if j==jmax:
                    #print jmax
                    break

            #break of first loop
            if count is not 0:
                count=0
                if length<jmax-tmpj:
                    length=jmax-tmpj


            totalarea+=length
            if i==0 and totalarea<minarea_lower_limit:
                break

            i,j,length=i-1,0,0

            if i==-1:
                break
            #end of second loop
        maxsize[frame_no]=totalarea
        totalarea=0
        frame_no,i,j=frame_no+1,imax-1,0

        if frame_no==frame_max:
            break
        #end of third loop
    real_maxarr = maxsize.copy()
    print maxsize
    #comparision to remove outliers
    area_max = 0
    count_max = 0
    for x in range(len(maxsize)-1):
        if abs(maxsize[x+1] - maxsize[x])>500:
            real_maxarr[x+1] = 0
            #maxsize[x+1] = 0
        elif (real_maxarr[x]>area_max):
            area_max = real_maxarr[x]
            count_max = x
    print count_max
    #maxsize.sort()
    #maxsize = maxsize[:len(maxsize)-5] #this is for excluding 5 most probables random maximum value
    #count = 0
    #for x in range(len(maxsize)+5):
    #    if(maxsize.max() == real_maxarr[x]):
    #        break
    #    else:
    #        count +=1
    #print count
    #return count,maxsize.max()
    return count_max,area_max

def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng

def f_median(arr_index_collector):
    length = len(arr_index_collector)
    #print length
    if not length % 2:
        return int((arr_index_collector[length / 2] + arr_index_collector[length / 2 - 1]) / 2.0)
        #median.append(val)
    return int(arr_index_collector[length / 2])
        #median.append(val)
def total_img(frame):
        lena = misc.imread('capture\stills-004\still-00'+str(frame+1)+'.jpg')
        pl.imshow(lena)
        pl.show()
def plot_frame(frame_number):
    #frame_number = 21
    my_frame = frame[frame_number].copy()
    sad   = my_frame[:,:,2]
    x_val = my_frame[:,:,0]
    y_val = my_frame[:,:,1]
    #ploting the given function
    x_val = x_val.reshape(x_val.size)
    y_val = y_val.reshape(y_val.size)
    sad = sad.reshape(sad.size)
    #ret,frame = cv2.threshold(img,127,255,cv2.THRESH_BINARY) #binary reading technique of an image


    lena = misc.imread('capture\stills-004\still-00'+str(frame_number+1)+'.jpg')
    lena_orig = lena.copy()

    ####################THIS IS FOR NOISE REDUCTION TECHNIQUE WHICH IS CURRENTLY NOT USED##############
    #noisy = lena + 0.4 * lena.std() * np.random.random(lena.shape)
    #gauss_denoised = ndimage.gaussian_filter(noisy, 2)
    #med_denoised = ndimage.median_filter(noisy, 3)
    #########################################################
    ####################### FINDING THE REQUIRED PROTION OF THE IMAGE ##################
    array_index_collector = []
    median = []
    val = 0
    for i in xrange(35,40):
        for j in xrange(20,120):
            if(sad[121*i+j]<300) or (abs(x_val[121*i+j])<1) or (abs(y_val[121*i+j])<1):
                #for k in xrange(16):
                #    for l in xrange(16):
                #        try:
                #            lena[16*i+k][16*j+l] = [0, 0, 0]
                #        except IndexError as e:
                #           pass
                #           #print "Index error"
            #storing the value of i and j
                continue
            else:
                array_index_collector.append(j)
        #print array_index_collector
        if not array_index_collector:
            continue
        val = f_median(array_index_collector)
        median.append(val)
    #print median
    if not median:
        print "No moving object detected in the given frame"
    else:
        val = f_median(median)
    ###############################################

    cropped_image = lena_orig[0:1080/2,16*(val-15):16*(val+15)]#THE VALUE LIKE 15 CAN BE ADJUSTED ACCORDING TO THE SITUATION
    pl.imshow(cropped_image)
    pl.show()

required_frame,area_size = find_appropriate_frame(68, 121, 0, 121, 500, ratio, frame,34,10)
print area_size
if area_size < 100 :
    print "no motion detected"
else:
    #total_img(required_frame)
    plot_frame(required_frame)
