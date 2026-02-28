import cv2 
import face_recognition 
img_bgr = cv2.imread("test_face.jpg") 
if img_bgr is None: raise ValueError("test_face.jpg not found") 
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB) 
faces = face_recognition.face_locations(img_rgb) 
print("Shape:", img_rgb.shape) 
print("Number of faces detected:", len(faces)) 
