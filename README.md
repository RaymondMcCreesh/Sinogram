# Sinogram

This code converts a sinogram into the captured image using the following steps.
 1) The coloured sinogram is seperated into 3 channels Red,Green,Blue.
 2) Each colour channel is reconstructed without a filter using back
propogation. 
 3) The colour channels are converted to frequency domain using fft.
 4) Each channel is ramp filtered.
 5) All channels are converted to the spatial domain using inverse fft.
 6) The channels are then back projected.
 7) They are rescaled to an 8 bit image and cropped accordingly
 8) The colour channels are resconstructed back to 1 image.
 10) Steps 3-8 are repeated for a hamming window filter and a Hann
window filter.

<img width=“964” alt=“java 8 and prio java 8  array review example” src="https://github.com/RaymondMcCreesh/Sinogram/blob/main/Sinogram.py">
