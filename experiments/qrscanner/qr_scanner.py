import cv2
import sys
import zxingcpp
import numpy as np

def main():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    # Try to set higher resolution for better detail
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Webcam started ({width}x{height}).")
    print("Using Targeted Scanning Zone. Place the QR code inside the central box.")
    print("Press 'q' in the window to exit.")

    # Define a larger target zone to ensure we don't clip the "quiet zone"
    box_size = int(min(width, height) * 0.7)
    x1 = (width - box_size) // 2
    y1 = (height - box_size) // 2
    x2 = x1 + box_size
    y2 = y1 + box_size

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # 1. Prepare ROI and Full Frame in Grayscale
            gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            roi_gray = gray_full[y1:y2, x1:x2]

            frame_count += 1
            if frame_count % 30 == 0:
                print("Scanning... Center the QR code in the box.", end="\r")

            # --- Detection Strategy ---
            # 1. Prepare different versions of the ROI for the detector
            # 1a. Raw Grayscale
            # 1b. Contrast Enhanced (CLAHE)
            # 1c. Adaptive Threshold (converts to pure black/white - great for QR)
            
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            roi_clahe = clahe.apply(roi_gray)
            roi_thresh = cv2.adaptiveThreshold(roi_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            # Try variants in order of speed/likelihood
            results = zxingcpp.read_barcodes(roi_gray, formats=zxingcpp.BarcodeFormat.QRCode)
            
            if not results:
                results = zxingcpp.read_barcodes(roi_clahe, formats=zxingcpp.BarcodeFormat.QRCode, try_rotate=True)
            
            if not results:
                results = zxingcpp.read_barcodes(roi_thresh, formats=zxingcpp.BarcodeFormat.QRCode, try_rotate=True)

            if not results:
                # Full frame fallback
                results = zxingcpp.read_barcodes(gray_full, formats=zxingcpp.BarcodeFormat.QRCode)

            # --- UI FEEDBACK ---
            # Mirror the frame FIRST
            preview_frame = cv2.flip(frame, 1)

            # Draw the target box on the MIRRORED frame so the text is readable
            cv2.rectangle(preview_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(preview_frame, "KEEP QR INSIDE THIS BOX", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            for result in results:
                print("\n" + "!"*40)
                print(f"SUCCESS: QR Code detected!")
                print(f"Data: {result.text}")
                print("!"*40)
                
                cap.release()
                cv2.destroyAllWindows()
                return

            cv2.imshow('QR Scanner (Press q to quit)', preview_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nScanning cancelled by user.")
                break
    except KeyboardInterrupt:
        print("\nScanning interrupted.")
    finally:
        if cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
