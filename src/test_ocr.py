"""
OCR Proof-of-Concept Test Script
Tests PaddleOCR on D4 screenshots and evaluates accuracy
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

try:
    from paddleocr import PaddleOCR
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: Missing dependencies. Please install:")
    print(f"  pip install paddlepaddle paddleocr opencv-python")
    print(f"\nDetails: {e}")
    sys.exit(1)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def load_image(image_path):
    """Load and display image info"""
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    height, width = img.shape[:2]
    print(f"  Image: {image_path.name}")
    print(f"  Size: {width}x{height} pixels")
    print(f"  Size: {os.path.getsize(image_path) / 1024:.1f} KB")

    return img


def initialize_ocr():
    """Initialize PaddleOCR"""
    print_section("Initializing PaddleOCR")

    try:
        ocr = PaddleOCR(
            use_textline_orientation=True,  # Enable angle classification (replaces use_angle_cls)
            lang='en',                       # English language
        )
        print("  ✓ PaddleOCR initialized successfully")
        print("  Using standard English model (not D4-custom)")
        return ocr
    except Exception as e:
        print(f"  ✗ Failed to initialize OCR: {e}")
        return None


def preprocess_image(img):
    """
    Apply preprocessing to improve OCR accuracy
    Returns original and preprocessed versions
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Increase contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

    # Convert back to BGR for PaddleOCR
    preprocessed = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    return preprocessed


def run_ocr(ocr, img, use_preprocessing=False):
    """Run OCR on image"""
    start_time = datetime.now()

    if use_preprocessing:
        img = preprocess_image(img)

    result = ocr.ocr(img, cls=True)

    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    return result, elapsed_ms


def parse_ocr_results(result):
    """Parse OCR results into structured format"""
    if not result or not result[0]:
        return []

    extracted_text = []
    for line in result[0]:
        # line format: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], (text, confidence)]
        bbox = line[0]
        text, confidence = line[1]

        extracted_text.append({
            'text': text,
            'confidence': confidence,
            'bbox': bbox,
            'position': {
                'x': int(bbox[0][0]),
                'y': int(bbox[0][1]),
                'width': int(bbox[2][0] - bbox[0][0]),
                'height': int(bbox[2][1] - bbox[0][1])
            }
        })

    return extracted_text


def analyze_results(extracted_text):
    """Analyze OCR results"""
    if not extracted_text:
        print("  ✗ No text extracted")
        return

    total_lines = len(extracted_text)
    avg_confidence = sum(item['confidence'] for item in extracted_text) / total_lines
    min_confidence = min(item['confidence'] for item in extracted_text)
    max_confidence = max(item['confidence'] for item in extracted_text)

    print(f"\n  Results:")
    print(f"    Lines extracted: {total_lines}")
    print(f"    Avg confidence: {avg_confidence:.1%}")
    print(f"    Min confidence: {min_confidence:.1%}")
    print(f"    Max confidence: {max_confidence:.1%}")

    # Show low confidence lines
    low_conf = [item for item in extracted_text if item['confidence'] < 0.8]
    if low_conf:
        print(f"\n  ⚠ Low confidence lines ({len(low_conf)}):")
        for item in low_conf[:5]:  # Show first 5
            print(f"    [{item['confidence']:.1%}] {item['text']}")


def display_extracted_text(extracted_text, limit=50):
    """Display extracted text"""
    print(f"\n  Extracted Text (first {limit} lines):")
    print("  " + "-" * 66)

    for i, item in enumerate(extracted_text[:limit], 1):
        conf_marker = "✓" if item['confidence'] > 0.9 else "⚠" if item['confidence'] > 0.7 else "✗"
        print(f"  {i:2d}. [{item['confidence']:.0%}] {conf_marker} {item['text']}")


def save_results(image_name, extracted_text, processing_time, output_dir):
    """Save results to JSON file"""
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{image_name}_{timestamp}_ocr.json"

    results = {
        'image': image_name,
        'timestamp': timestamp,
        'processing_time_ms': processing_time,
        'total_lines': len(extracted_text),
        'avg_confidence': sum(item['confidence'] for item in extracted_text) / len(extracted_text) if extracted_text else 0,
        'extracted_text': extracted_text
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ Results saved to: {output_file}")
    return output_file


def test_single_image(ocr, image_path, output_dir):
    """Test OCR on a single image"""
    print_section(f"Testing: {image_path.name}")

    try:
        # Load image
        img = load_image(image_path)

        # Run OCR
        print("\n  Running OCR...")
        result, elapsed_ms = run_ocr(ocr, img, use_preprocessing=True)
        print(f"  Processing time: {elapsed_ms:.0f}ms")

        # Parse results
        extracted_text = parse_ocr_results(result)

        # Analyze
        analyze_results(extracted_text)

        # Display
        display_extracted_text(extracted_text, limit=30)

        # Save
        save_results(image_path.stem, extracted_text, elapsed_ms, output_dir)

        return extracted_text

    except Exception as e:
        print(f"  ✗ Error processing image: {e}")
        return None


def main():
    """Main test workflow"""
    print("\n" + "█" * 70)
    print("█" + " " * 20 + "DIABLO 4 OCR TEST" + " " * 27 + "█")
    print("█" * 70)

    # Setup paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    screenshots_dir = project_dir / "data" / "screenshots"
    output_dir = project_dir / "data" / "ocr_results"

    # Check for screenshots
    if not screenshots_dir.exists():
        print(f"\n⚠ Screenshot directory not found: {screenshots_dir}")
        print(f"\nPlease create the directory and add your D4 screenshots:")
        print(f"  1. Create: {screenshots_dir}")
        print(f"  2. Copy your 4 D4 tooltip screenshots there")
        print(f"  3. Run this script again")
        return

    # Find screenshots
    image_extensions = ['.png', '.jpg', '.jpeg']
    screenshots = [
        f for f in screenshots_dir.iterdir()
        if f.suffix.lower() in image_extensions
    ]

    if not screenshots:
        print(f"\n⚠ No screenshots found in: {screenshots_dir}")
        print(f"\nSupported formats: {', '.join(image_extensions)}")
        return

    print(f"\nFound {len(screenshots)} screenshot(s)")
    for img in screenshots:
        print(f"  - {img.name}")

    # Initialize OCR
    ocr = initialize_ocr()
    if not ocr:
        return

    # Test each image
    results = {}
    for image_path in screenshots:
        extracted = test_single_image(ocr, image_path, output_dir)
        if extracted:
            results[image_path.name] = extracted

    # Summary
    print_section("Test Summary")
    print(f"  Images processed: {len(results)}/{len(screenshots)}")
    print(f"  Results saved to: {output_dir}")

    if results:
        total_lines = sum(len(text) for text in results.values())
        avg_lines = total_lines / len(results)
        print(f"  Total text lines: {total_lines}")
        print(f"  Avg per image: {avg_lines:.0f}")

    print("\n  Next steps:")
    print("  1. Review the OCR output in the JSON files")
    print("  2. Identify accuracy issues (missed text, wrong text)")
    print("  3. Consider if we need the custom D4 model")
    print("  4. Build post-processing pipeline with affix fuzzy-matching")


if __name__ == "__main__":
    main()
