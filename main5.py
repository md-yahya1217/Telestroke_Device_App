import cv2
for i in range(5):  # Check first 5 indices
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera found at index: {i}")
        
        # Show footage from the camera
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            cv2.imshow(f'Camera {i}', frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    else:
        print(f"No camera at index: {i}")


# import cv2

# cap = cv2.VideoCapture(0)  # Try using 0 for the default camera
# # or use cv2.VideoCapture(1) if you have multiple cameras

# if not cap.isOpened():
#     print("Error: Could not open webcam.")
# else:
#     print("Webcam opened successfully.")
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Error: Failed to capture frame.")
#             break
#         cv2.imshow("Webcam Feed", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# cap.release()
# cv2.destroyAllWindows()
