import numpy as np
import cv2
import traceback

# Handle PyWavelets import
try:
    import pywt
except ImportError:
    import os
    os.system('pip install PyWavelets')
    import pywt

def w2d(img, mode='haar', level=1):
    try:
        imArray = img
        # Convert to grayscale
        imArray = cv2.cvtColor(imArray, cv2.COLOR_RGB2GRAY)
        # Convert to float
        imArray = np.float32(imArray)
        imArray /= 255
        
        # Compute coefficients
        coeffs = pywt.wavedec2(imArray, mode, level=level)

        # Process Coefficients
        coeffs_H = list(coeffs)
        coeffs_H[0] *= 0

        # Reconstruction
        imArray_H = pywt.waverec2(coeffs_H, mode)
        imArray_H *= 255
        imArray_H = np.uint8(imArray_H)

        return imArray_H
    except Exception as e:
        print(f"Error in wavelet transform: {str(e)}")
        traceback.print_exc()
        # Return original grayscale image as fallback
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return gray
