"""Small synthetic tests; do not require private PDF fixtures or live OCR."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import fitz
from PIL import Image

from extract_to_txt import extract_text_from_page, extract_text_from_pdf


class ExtractorTests(unittest.TestCase):
    def test_embedded_text_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "fixture.pdf"
            output_path = Path(tmp) / "fixture.txt"
            document = fitz.open()
            page = document.new_page()
            page.insert_text((72, 72), "SYNTHETIC PDF TEST RECORD")
            document.save(input_path)
            document.close()

            with patch("extract_to_txt.pytesseract.image_to_string") as ocr:
                extract_text_from_pdf(input_path, output_path)

            result = output_path.read_text(encoding="utf-8")
            self.assertIn("SYNTHETIC PDF TEST RECORD", result)
            ocr.assert_not_called()

    def test_empty_text_layer_invokes_ocr_fallback(self):
        stream = io.BytesIO()
        Image.new("RGB", (30, 20), "white").save(stream, format="PNG")
        page = Mock()
        page.get_text.return_value = ""
        page.get_pixmap.return_value.tobytes.return_value = stream.getvalue()

        with patch("extract_to_txt.pytesseract.image_to_string", return_value="MOCK OCR") as ocr:
            result = extract_text_from_page(page)

        self.assertEqual(result, "MOCK OCR")
        ocr.assert_called_once()


if __name__ == "__main__":
    unittest.main()
