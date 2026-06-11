import cv2
import zxingcpp
import sys

def check_qr(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return

    # Try to decode with zxingcpp (which is very robust)
    results = zxingcpp.read_barcodes(img)
    
    if not results:
        print("Diagnostic: No barcode/QR code detected in this image file.")
        # Try with some basic processing just in case
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results = zxingcpp.read_barcodes(gray, try_rotate=True, try_harder=True)
    
    if results:
        for result in results:
            print(f"Success! Detected {result.format}")
            print(f"Data: {result.text}")
    else:
        print("Diagnostic: The image was processed but no valid QR structure was found.")
        print("Observation: The image appears to be missing 'Timing Patterns' (the alternating black/white lines between finder patterns).")

if __name__ == "__main__":
    # The image path from the user's message
    path = "../.gemini/tmp/wip/images/clipboard-1781200946016.png"
    check_qr(path)
