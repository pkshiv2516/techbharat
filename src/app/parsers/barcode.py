from typing import Optional
try:
    from pyzbar.pyzbar import decode
    _HAS_PYZBAR = True
except Exception:
    _HAS_PYZBAR = False
from PIL import Image
from io import BytesIO




def decode_barcode(image_bytes: bytes) -> Optional[str]:
    if not _HAS_PYZBAR:
        return None
    im = Image.open(BytesIO(image_bytes)).convert('RGB')
    res = decode(im)
    for r in res:
        val = r.data.decode('utf-8')
        if val.isdigit() and 6 <= len(val) <= 14:
            return val
    return None