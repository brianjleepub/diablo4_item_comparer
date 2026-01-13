# D4 OCR Research: d4-item-tooltip-ocr Project

## Project Overview
- **Repository**: https://github.com/mxtsdev/d4-item-tooltip-ocr
- **Author**: mxtsdev
- **Technology**: PaddleOCR with custom-trained model

## Key Findings

### 1. Custom Model
- **Model Name**: `en_PP-OCRv3_rec-d4_tooltip`
- **Type**: PaddleOCR Recognition model (fine-tuned for D4 tooltips)
- **Location**: `paddleocr-models/en_PP-OCRv3_rec-d4_tooltip/`
- **Purpose**: Specifically trained on Diablo 4 tooltip text for higher accuracy

### 2. Dependencies
```
numpy==1.23.5
opencv_contrib_python==4.6.0.66
opencv_python==4.6.0.66
opencv_python_headless==4.6.0.66
paddlepaddle==2.5.0
paddleocr==2.6.1.3
python_Levenshtein==0.21.1  # For fuzzy string matching
```

**Note**: These are older versions. Current versions as of 2026:
- PaddleOCR: 3.x (significant API changes)
- PaddlePaddle: 2.6.x+

### 3. How to Use Custom Models

PaddleOCR allows loading custom models with:

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    det_model_dir='/path/to/detection/model',      # Text detection
    rec_model_dir='/path/to/recognition/model',    # Text recognition (D4 custom)
    rec_char_dict_path='/path/to/char_dict.txt'    # Character dictionary
)

result = ocr.ocr('screenshot.png', cls=True)
```

**Key Parameters:**
- `det_model_dir` - Detection model (finds text regions)
- `rec_model_dir` - Recognition model (reads text) ← **This is where D4 custom model goes**
- `rec_char_dict_path` - Character set the model was trained on

### 4. Their Pipeline

```
Input Image
    ↓
Tooltip Detection (optional --find-tooltip flag)
    ↓
PaddleOCR with Custom D4 Model
    ↓
Text Extraction
    ↓
Structured JSON Output
    {
        "name": "Item Name",
        "type": "Helm",
        "item_power": 800,
        "affixes": [...],
        "aspect": {...},
        "stats": {...},
        "sockets": [...]
    }
```

## What We Can Learn/Reuse

### ✅ Can Use:
1. **Their custom model** - If we can clone their repo, we get the trained model
2. **Their approach** - PaddleOCR with custom recognition model is proven
3. **Their dependencies** - Know what works (though we'll use newer versions)
4. **Their output structure** - Good template for our JSON format

### ❌ Cannot Use:
1. **Training methodology** - Not documented
2. **Accuracy metrics** - Not published
3. **Preprocessing details** - Code not examined yet

## Our Implementation Strategy

### Option A: Use Their Model Directly
**Pros:**
- Pre-trained for D4 tooltips
- Should have higher accuracy out of the box
- Saves training time

**Cons:**
- Need to clone their repo for model files
- Locked to their model's capabilities
- PaddleOCR 2.6.1.3 (older version)

**How:**
```bash
git clone https://github.com/mxtsdev/d4-item-tooltip-ocr.git
# Use their model directory
rec_model_dir='d4-item-tooltip-ocr/paddleocr-models/en_PP-OCRv3_rec-d4_tooltip'
```

### Option B: Start with Standard PaddleOCR
**Pros:**
- Latest version (3.x)
- No external dependencies
- Simpler setup
- Can train our own model later

**Cons:**
- Lower initial accuracy
- May struggle with D4-specific fonts/symbols
- More post-processing needed

**How:**
```bash
pip install paddlepaddle paddleocr
# Use built-in English model
ocr = PaddleOCR(use_angle_cls=True, lang='en')
```

### Option C: Hybrid Approach (RECOMMENDED)
1. **Start with standard PaddleOCR (Option B)** to test our screenshots
2. **Add robust post-processing** using our affix database (1,186 affixes)
3. **Clone their model (Option A)** if accuracy is insufficient
4. **Train our own model** as Phase 2 improvement

**Rationale:**
- Quick start with standard model
- Validates our preprocessing pipeline
- Database fuzzy-matching can compensate for OCR errors
- Can always upgrade to custom model later

## Next Steps

### Immediate (Testing Phase):
1. Install PaddleOCR (latest version)
2. Test on user's 4 D4 screenshots
3. Measure accuracy and identify problem areas
4. Evaluate if we need the custom model

### If Standard OCR Insufficient:
1. Clone d4-item-tooltip-ocr repository
2. Extract their custom model
3. Test with their model on same screenshots
4. Compare results

### Post-Processing Strategy:
Regardless of OCR choice, we need:
- Fuzzy matching against our 1,186 affixes
- Number extraction and validation
- Range parsing `[min - max]`
- Color detection for affix types
- Confidence scoring per field

## References
- [d4-item-tooltip-ocr Repository](https://github.com/mxtsdev/d4-item-tooltip-ocr)
- [PaddleOCR Custom Model Usage](https://github.com/PaddlePaddle/PaddleOCR/discussions/13705)
- [PaddleOCR Documentation](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/OCR.html)
- [Training Custom PaddleOCR Models](https://hackernoon.com/ocr-fine-tuning-from-raw-data-to-custom-paddle-ocr-model)
