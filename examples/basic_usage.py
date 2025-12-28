"""Basic usage example for fiscflow-receipt-ocr."""
from fiscflow_ocr import ReceiptOCR


def main():
    # Initialize OCR client
    ocr = ReceiptOCR(
        provider='google_vision',
        credentials_path='credentials/fiscflowai-service-account-key.json'
    )

    # Extract from local file
    result = ocr.extract('receipt.jpg')

    # Print results
    print(f"Merchant: {result['merchant']}")
    print(f"Total: ${result['total']:.2f}")
    print(f"Date: {result['date']}")
    print(f"\nItems ({len(result['items'])}):")

    for item in result['items']:
        print(f"  - {item['name']}: {item['quantity']} x ${item['price']:.2f} = ${item['total_price']:.2f}")

    print(f"\nRaw OCR confidence: {result['confidence']:.2f}")


if __name__ == '__main__':
    main()
