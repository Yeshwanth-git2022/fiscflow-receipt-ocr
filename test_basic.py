"""Quick test to verify library imports and basic functionality."""
from fiscflow_ocr import ReceiptOCR

# Test 1: Initialize client
print("Test 1: Initializing ReceiptOCR client...")
ocr = ReceiptOCR(
    provider='google_vision',
    credentials_path='credentials/fiscflowai-service-account-key.json'
)
print("✓ Client initialized successfully")

# Test 2: Verify extractor is set up
print("\nTest 2: Checking extractor configuration...")
assert ocr.extractor is not None, "Extractor not initialized"
print(f"✓ Using extractor: {type(ocr.extractor).__name__}")

# Test 3: Check Vision API client
print("\nTest 3: Verifying Vision API client...")
assert hasattr(ocr.extractor, 'client'), "Vision API client not found"
print("✓ Vision API client is ready")

print("\n✅ All basic tests passed!")
print("\nNext step: Test with a real receipt image using examples/basic_usage.py")
