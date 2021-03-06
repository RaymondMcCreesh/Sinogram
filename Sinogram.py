
#################################################################
# Imports
#################################################################

import numpy as np 
import imutils
from skimage.transform import rotate ## Image rotation routine
import scipy.fftpack as fft          ## Fast Fourier Transform
import imageio                       ## Used to save images
import math

#################################################################
# Functions
#################################################################

#Converts the sinogram single channel 
#to frequency domain using fast fourier transform
def ch_fft(channel):
    #Build 1-d FFTs of an array of projections, each projection 1 row of the array.
    return fft.rfft(channel, axis = 1)

# Filter the projections of each channel
# using a ramp filter
def ramp_filter(ch_proj):
    #Ramp filter a 2-d array of 1-d FFTs (1-d FFTs along the rows).
    ramp  =  np.floor(np.arange(0.5, ch_proj.shape[1]//2 + 0.1, 0.5))
    return ch_proj * ramp

# Applied Hamming windowed ramp filter to channel passed in.
def hamming_window(ch_proj): 
    ramp  =  np.floor(np.arange(0.5, ch_proj.shape[1]//2 + 0.1, 0.5))
    window_filter = ramp
    
    # Initialise variables for hamming window
    c = 0.54
    N = ch_proj.shape[1]  # length of input channel = 658
    hamming = np.zeros(N//2) # Array of zeros of length 329
    
    # Create hamming window for N/2 elements
    for i in range(N//2):
        hamming[i] = (c+((1-c)*math.cos(math.pi*(i/((N/2)-1)))))
    # Multiply Hamming window by corresponding Ramp filter values
    for i in range(1,(N//2)):
        window_filter[(i*2)-1] = ramp[(i*2)-1]*hamming[i]
        window_filter[i*2] = ramp[i*2]*hamming[i]
        
    window_filter[-1] = ramp[-1]*hamming[-1]
    
    # return input channel times windowed ramp filter
    return ch_proj*window_filter

# Applies Hann windowed ramp filter to channel passed in
def hann_window(ch_proj):
    ramp  =  np.floor(np.arange(0.5, ch_proj.shape[1]//2 + 0.1, 0.5))
    window_filter = ramp
    
    # Initialise variables for hamming window
    c = 0.5
    N = ch_proj.shape[1]  # length of input channel = 658
    hann = np.zeros(N//2) # Array of zeros of length 329
    
    # Create Hann window for N/2 elements
    for i in range(N//2):
        hann[i] = (c+(c*math.cos(math.pi*(i/((N/2)-1)))))
    
    # Multiplies Hann window values by corresponding ramp filter values
    for i in range(1,(N//2),1):
        window_filter[(i*2)-1] = ramp[(i*2)-1]*hann[i]
        window_filter[i*2] = ramp[i*2]*hann[i]
    
    window_filter[-1] = ramp[-1]*hann[-1]

    # return input channel times windowed ramp filter
    return ch_proj*window_filter

# Return channel using inverse fast fourier transform
# to the spatial domain
def inverse_fft(channel):
    return fft.irfft(channel, axis = 1)

# Returns the reconstructed image 
# by back projecting the filtered projections
def back_projection(channel):
    
    #laminogram equal to images height
    laminogram = np.zeros((channel.shape[1],channel.shape[1]))
    dTheta = 180.0 / channel.shape[0]
    
    #rotate image and plot values on linogram
    for i in range(channel.shape[0]):
        arr = np.tile(channel[i],(channel.shape[1],1))
        temp = rotate(arr, dTheta*i)
        laminogram +=  temp
    return laminogram

# Crops image into square
def crop(channel):
    #square length =  diameter/square root(2)
    side = int(channel.shape[0]/math.sqrt(2))
    new_ch = []
    
    #width start and end points
    s_width = int((channel.shape[0]/2)-side/2)
    e_width = int((channel.shape[0]/2)+side/2)

    #height start and end points
    s_height = int((channel.shape[1]/2)-side/2)
    e_height = int((channel.shape[1]/2)+side/2)

    #cropping channel 
    for i in channel[s_width:e_width]:
        new_ch.append(i[s_height:e_height])
    new_ch = np.reshape(new_ch,(side,side))
    return new_ch

# Rescales channel to 8bit channel
def ch_rescale(channel):
    cr_ch = crop(channel)
    chi,clo = cr_ch.max(),cr_ch.min()
    chnorm = 255*(cr_ch-clo)/(chi-clo)
    ch8bit = np.floor(chnorm).astype('uint8')
    return ch8bit

# Applies inverse fast fourier transform and back projection to each channel
# input to the function. Channels then scaled and cropped.
def reconstruction(r_cha, g_cha, b_cha, filter_type):
    #Converting colour channels to spacial domain using inverse FFT
    spatial_dom_red = inverse_fft(r_cha)
    spatial_dom_green = inverse_fft(g_cha)
    spatial_dom_blue = inverse_fft(b_cha)
    
    #Back projecting colour channels
    recon_im_red = back_projection(spatial_dom_red)
    recon_im_green = back_projection(spatial_dom_green)
    recon_im_blue = back_projection(spatial_dom_blue)
    
    # Display back projected images including edge artifacts
    imutils.imshow(recon_im_red, title = "Red channel backprojections for " + filter_type )
    imutils.imshow(recon_im_green, title = "Green channel backprojections for " + filter_type)
    imutils.imshow(recon_im_blue, title = "Blue channel backprojections for " + filter_type)    
    
    #Rescaling channels to 8 bit and cropping image
    red_scaled= ch_rescale(recon_im_red)
    green_scaled= ch_rescale(recon_im_green)
    blue_scaled= ch_rescale(recon_im_blue)
    
    return red_scaled, green_scaled, blue_scaled

# Calculates the mean squared error between the two input images. Images
# must be the same size
def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more similar
	return err

## Statements
##Import coloured image (RGB)
print("Original Sinogram")
sinogram = imutils.imread('sinogram.png',greyscale = False)
imutils.imshow(sinogram, title = "Original Sinogram image")
imageio.imwrite('originalSinogramImage.png', sinogram)

##splitting the image into 3 colours
red = sinogram[:,:,0]
green = sinogram[:,:,1]
blue = sinogram[:,:,2]

#Reshaping the colours to give rows
red = np.reshape(red,(360,658))
green = np.reshape(green,(360,658))
blue = np.reshape(blue,(360,658))

#################################################################
#Reconstruction of each colour channel without any filtering
#################################################################

print("Reconstruction with no filtering")
unfiltered_red = back_projection(red)
unfiltered_green = back_projection(green)
unfiltered_blue = back_projection(blue)

# Display back projected images including edge artifacts
imutils.imshow(unfiltered_red, title = "Red channel Backprojection without filtering")
imutils.imshow(unfiltered_green, title = "Green channel Backprojection without filtering")
imutils.imshow(unfiltered_blue, title = "Blue channel Backprojection without filtering") 

#Rescaling channels to 8 bit and cropping image
red_rescaled =  ch_rescale(unfiltered_red)
green_rescaled = ch_rescale(unfiltered_green)
blue_rescaled = ch_rescale(unfiltered_blue)

imutils.imshow(red_rescaled, title = "Red channel without filtering, cropped and scaled to 8-bit")
imutils.imshow(green_rescaled, title = "Blue channel without filtering, cropped and scaled to 8-bit")
imutils.imshow(blue_rescaled, title = "Blue channel without filtering, cropped and scaled to 8-bit")

#Reconstruct all channels to one image
print("Reconstructed coloured image\n\n")
image = np.dstack((red_rescaled,green_rescaled,blue_rescaled))
imutils.imshow(image, title = "Reconstruction without filtering")

#################################################################
#Reconstruction of each colour channel with simple rampfiltering
#################################################################

print("Performing simple ramp filtered reconstruction")
#Convert channels to Frequency domain
red_fft = ch_fft(red)
green_fft = ch_fft(green)
blue_fft = ch_fft(blue)

#Ramp channels
red_filt = ramp_filter(red_fft)
green_filt = ramp_filter(green_fft)
blue_filt = ramp_filter(blue_fft)

#Rescaling channels to 8 bit and cropping image
red_rescaled, green_rescaled, blue_rescaled = reconstruction(red_filt, green_filt, blue_filt, "ramp filter")

imutils.imshow(red_rescaled, title = "Red channel ramp filtering, cropped and scaled to 8-bit")
imutils.imshow(green_rescaled, title = "Green channel rampfiltering, cropped and scaled to 8-bit")
imutils.imshow(blue_rescaled, title = "Blue channel ramp filtering, cropped and scaled to 8-bit")

#Reconstruct all channels to one image
print("Simple ramp filtered reconstruction complete.\n\n")
image_ramp=np.dstack((red_rescaled,green_rescaled,blue_rescaled))
imutils.imshow(image_ramp, title = "Reconstruction with ramp filtering")

#################################################################
#Reconstruction of each colour channel with Hamming window filter
#################################################################

print("Performing Hamming window ramp filtered reconstruction")
#Convert channels to Frequency domain
red_fft = ch_fft(red)
green_fft = ch_fft(green)
blue_fft = ch_fft(blue)

#Hamming window channels
red_filt = hamming_window(red_fft)
green_filt = hamming_window(green_fft)
blue_filt = hamming_window(blue_fft)

#Rescaling channels to 8 bit and cropping image
red_rescaled, green_rescaled, blue_rescaled = reconstruction(red_filt, green_filt, blue_filt, "Hamming windowed filter")

imutils.imshow(red_rescaled, title = "Red channel Hamming window filtering, cropped and scaled to 8-bit")
imutils.imshow(green_rescaled, title = "Green channel: Hamming window filtering, cropped and scaled to 8-bit")
imutils.imshow(blue_rescaled, title = "Blue channel Hamming window filtering, cropped and scaled to 8-bit")

#Reconstruct all channels to one image
print("Hamming window ramp filtered reconstruction complete.\n\n")
image_hamming=np.dstack((red_rescaled,green_rescaled,blue_rescaled))
imutils.imshow(image_hamming, title = "Reconstruction with Hamming windowed ramp filtering")

#################################################################
#Reconstruction of each colour channel with Hann window filter
#################################################################

print("Performing Hann window ramp filtered reconstruction")
#Convert channels to Frequency domain
red_fft = ch_fft(red)
green_fft = ch_fft(green)
blue_fft = ch_fft(blue)

#Hann window channels
red_filt = hann_window(red_fft)
green_filt = hann_window(green_fft)
blue_filt = hann_window(blue_fft)

#Rescaling channels to 8 bit and cropping image
red_rescaled, green_rescaled, blue_rescaled = reconstruction(red_filt, green_filt, blue_filt, "Hann windowed filter")

imutils.imshow(red_rescaled, title = "Red channel Hann window filtering, cropped and scaled to 8-bit")
imutils.imshow(green_rescaled, title = "Green channel Hann window filtering, cropped and scaled to 8-bit")
imutils.imshow(blue_rescaled, title = "Blue channel Hann window filtering, cropped and scaled to 8-bit")

#Reconstruct all channels to one image
print("Hann window ramp filtered reconstruction complete.\n\n")
image_hann=np.dstack((red_rescaled,green_rescaled,blue_rescaled))
imutils.imshow(image_hann, title = "Reconstruction with Hann windowed ramp filtering")

# Calculate the mean squared error and display absolute difference between Hamming and Hann
print("Mean squared error between Hamming and Hann windowed ramp filters: ")
print(mse(image_hamming, image_hann))
image_diff = abs(image_hamming - image_hann)
imutils.imshow(image_diff, title = "Pixels differences between Hamming and Hann filter reconstruction")
