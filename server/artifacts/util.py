import joblib
import json
import numpy as np
import base64
import os
import sys
import traceback

# Initialize global variables
__class_name_to_number = {}
__class_number_to_name = {}
__model = None
__face_cascade = None
__eye_cascade = None

# Handle OpenCV import
try:
    import cv2
except ImportError:
    # For Vercel deployment - use a special version for serverless
    import importlib.util
    spec = importlib.util.find_spec('cv2')
    if spec is None:
        # Try to install opencv-python-headless if it's not installed
        os.system('pip install opencv-python-headless')
        import cv2
    else:
        import cv2

# Import wavelet module
try:
    from wavelet import w2d
except ImportError:
    # Adjust import path if needed
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from wavelet import w2d

def classify_image(image_base64_data, file_path=None):
    try:
        # Ensure model is loaded
        if __model is None:
            load_saved_artifacts()
            
        # Process image
        imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)
        
        if len(imgs) == 0:
            return [{"error": "No face detected with two eyes. Please try another image."}]

        result = []
        for img in imgs:
            try:
                scalled_raw_img = cv2.resize(img, (32, 32))
                img_har = w2d(img, 'db1', 5)
                scalled_img_har = cv2.resize(img_har, (32, 32))
                combined_img = np.vstack((scalled_raw_img.reshape(32 * 32 * 3, 1), scalled_img_har.reshape(32 * 32, 1)))

                len_image_array = 32*32*3 + 32*32

                final = combined_img.reshape(1,len_image_array).astype(float)
                prediction = __model.predict(final)[0]
                probabilities = __model.predict_proba(final)[0]
                
                result.append({
                    'class': class_number_to_name(prediction),
                    'class_probability': np.around(probabilities*100,2).tolist(),
                    'class_dictionary': __class_name_to_number
                })
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                result.append({"error": f"Error processing image: {str(e)}"})
                
        return result
    except Exception as e:
        print(f"Classification error: {str(e)}")
        traceback.print_exc()
        return [{"error": f"Classification error: {str(e)}"}]

def class_number_to_name(class_num):
    try:
        return __class_number_to_name[class_num]
    except:
        return "Unknown"

def load_saved_artifacts():
    print("Loading saved artifacts...")
    global __class_name_to_number
    global __class_number_to_name
    global __model
    global __face_cascade
    global __eye_cascade

    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        
        # List files in directory for debugging
        print(f"Files in directory: {os.listdir(current_dir)}")
        
        # Load class dictionary
        dict_path = os.path.join(current_dir, "class_dictionary.json")
        print(f"Loading class dictionary from: {dict_path}")
        
        with open(dict_path, "r") as f:
            __class_name_to_number = json.load(f)
            __class_number_to_name = {v:k for k,v in __class_name_to_number.items()}
        
        # Load model
        model_path = os.path.join(current_dir, 'saved_model.pkl')
        print(f"Loading model from: {model_path}")
        
        if __model is None:
            with open(model_path, 'rb') as f:
                __model = joblib.load(f)
        
        # Load cascades
        face_cascade_path = os.path.join(current_dir, 'opencv/haarcascades/haarcascade_frontalface_default.xml')
        eye_cascade_path = os.path.join(current_dir, 'opencv/haarcascades/haarcascade_eye.xml')
        
        print(f"Loading face cascade from: {face_cascade_path}")
        print(f"Loading eye cascade from: {eye_cascade_path}")
        
        __face_cascade = cv2.CascadeClassifier(face_cascade_path)
        __eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        
        print("Loaded saved artifacts successfully")
    except Exception as e:
        print(f"Error loading artifacts: {str(e)}")
        traceback.print_exc()
        raise

def get_cv2_image_from_base64_string(b64str):
    try:
        if ',' in b64str:
            encoded_data = b64str.split(',')[1]
        else:
            encoded_data = b64str
            
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding base64 image: {str(e)}")
        traceback.print_exc()
        return None

def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    try:
        global __face_cascade
        global __eye_cascade
        
        # Ensure cascades are loaded
        if __face_cascade is None or __eye_cascade is None:
            load_saved_artifacts()
        
        # Get image
        if image_path:
            img = cv2.imread(image_path)
        else:
            img = get_cv2_image_from_base64_string(image_base64_data)
            
        if img is None:
            print("Failed to load image")
            return []
            
        # Process image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = __face_cascade.detectMultiScale(gray, 1.3, 5)

        cropped_faces = []
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = __eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                cropped_faces.append(roi_color)
                
        return cropped_faces
    except Exception as e:
        print(f"Error in face detection: {str(e)}")
        traceback.print_exc()
        return []
