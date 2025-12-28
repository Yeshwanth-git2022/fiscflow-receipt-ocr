# Getting Started with FiscFlow Receipt OCR

## Quick Setup

### 1. Create New Git Repository

```bash
cd /home/yesh/workspace/fiscflow-receipt-ocr
git init
git add .
git commit -m "Initial commit: FiscFlow Receipt OCR library"

# Create GitHub repo and push
gh repo create fiscflow-receipt-ocr --public --source=. --remote=origin
git push -u origin main
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### 3. Configure Google Vision API

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# Or pass directly to ReceiptOCR
ocr = ReceiptOCR(credentials_path='/path/to/credentials.json')
```

### 4. Test the Library

```bash
# Run basic example
python examples/basic_usage.py

# Run tests
pytest tests/ -v

# Check code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

---

## Development Workflow

### Create a Feature Branch

```bash
git checkout -b feature/ml-ner-extraction
```

### Add Your Changes

```bash
# Edit files...
git add .
git commit -m "feat: add NER-based item extraction"
```

### Run Tests

```bash
pytest tests/ -v --cov=fiscflow_ocr
```

### Push and Create PR

```bash
git push origin feature/ml-ner-extraction
gh pr create --title "Add NER extraction" --body "Implements ML-based item extraction"
```

---

## Integrating with FiscFlowAI

### Option 1: Install from Local Path (Development)

```bash
# In FiscFlowAI project
cd /home/yesh/workspace/fiscflowai
pip install -e ../fiscflow-receipt-ocr
```

### Option 2: Install from Git (Testing)

```python
# requirements.txt
fiscflow-receipt-ocr @ git+https://github.com/yourusername/fiscflow-receipt-ocr.git
```

### Option 3: Install from PyPI (Production)

```bash
pip install fiscflow-receipt-ocr
```

### Update FiscFlowAI Code

```python
# Before (old code in FiscFlowAI)
from app.services.receipt_service import ReceiptService

receipt_service = ReceiptService()
result = receipt_service.process_receipt_image(image_bytes)

# After (using library)
from fiscflow_ocr import ReceiptOCR

ocr = ReceiptOCR(provider='google_vision')
result = ocr.extract(image_bytes)
```

---

## ML Model Development

### Set Up Jupyter for Research

```bash
# Install Jupyter
pip install -e ".[dev]"

# Start Jupyter
jupyter notebook
```

### Create Training Notebook

```python
# notebooks/01_ner_training.ipynb

# 1. Load training data
import json
with open('data/receipts.json') as f:
    receipts = json.load(f)

# 2. Prepare NER examples
examples = []
for receipt in receipts:
    examples.append({
        'text': receipt['raw_text'],
        'entities': receipt['annotations']
    })

# 3. Train spaCy NER model
import spacy
from spacy.training import Example

nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add labels
ner.add_label("ITEM_NAME")
ner.add_label("PRICE")
ner.add_label("QUANTITY")

# Train
for i in range(30):
    for text, annot in examples:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annot)
        nlp.update([example])

# Save model
nlp.to_disk("models/receipt_ner_v1")
```

### Test Trained Model

```python
# Load model
from fiscflow_ocr import ReceiptOCR

ocr = ReceiptOCR(
    provider='ml_enhanced',
    model_path='models/receipt_ner_v1'
)

result = ocr.extract('receipt.jpg')
```

---

## Adding a New OCR Provider

### 1. Create Extractor Class

```python
# src/fiscflow_ocr/extractors/aws_textract.py

from .base import BaseExtractor
from ..models.receipt import Receipt

class AWSTextractExtractor(BaseExtractor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import boto3
        self.client = boto3.client('textract')

    def extract(self, image_bytes: bytes) -> Receipt:
        # Call AWS Textract API
        response = self.client.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['TABLES', 'FORMS']
        )

        # Parse response and create Receipt object
        receipt = Receipt()
        # ... extraction logic ...
        return receipt
```

### 2. Register Provider

```python
# src/fiscflow_ocr/client.py

PROVIDERS = {
    'google_vision': GoogleVisionExtractor,
    'aws_textract': AWSTextractExtractor,  # Add this
    ...
}
```

### 3. Test New Provider

```python
ocr = ReceiptOCR(provider='aws_textract')
result = ocr.extract('receipt.jpg')
```

---

## Publishing to PyPI

### 1. Build Package

```bash
pip install build twine
python -m build
```

### 2. Test on TestPyPI

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ fiscflow-receipt-ocr
```

### 3. Publish to PyPI

```bash
twine upload dist/*
```

### 4. Install from PyPI

```bash
pip install fiscflow-receipt-ocr
```

---

## Next Steps

### Week 1-2: Foundation
- [x] Create library structure
- [ ] Write comprehensive tests
- [ ] Add more examples
- [ ] Set up CI/CD (GitHub Actions)

### Week 3-4: ML Research
- [ ] Collect training dataset (100+ receipts)
- [ ] Annotate receipts for NER
- [ ] Train initial spaCy model
- [ ] Evaluate accuracy

### Month 2: Advanced Features
- [ ] Implement Vision Transformer (DONUT)
- [ ] Add AWS Textract support
- [ ] Build feedback collection system
- [ ] Set up retraining pipeline

### Month 3: Production Ready
- [ ] Optimize performance
- [ ] Add comprehensive docs
- [ ] Publish to PyPI
- [ ] Integrate into FiscFlowAI

---

## Resources

- **spaCy NER Tutorial**: https://spacy.io/usage/training#ner
- **DONUT Paper**: https://arxiv.org/abs/2111.15664
- **LayoutLM**: https://github.com/microsoft/unilm/tree/master/layoutlm
- **Google Vision API**: https://cloud.google.com/vision/docs

---

## Support

Questions? Open an issue or reach out:
- GitHub Issues: https://github.com/yourusername/fiscflow-receipt-ocr/issues
- Email: support@fiscflow.ai
- Discord: [Join our community](https://discord.gg/fiscflow)

Happy coding! 🚀
