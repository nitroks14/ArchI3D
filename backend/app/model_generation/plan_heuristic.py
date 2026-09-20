"""
Heuristique V1 de detection de pieces a partir d'une image de plan 2D.

Principe simplifie (documente comme limitation connue - la vectorisation fine de plans est
prevue en V2) :
1. Binarisation du plan (les murs/traits sont supposes plus sombres que le fond).
2. Recherche des contours "trous" (RETR_CCOMP) a l'interieur du contour exterieur du batiment :
   chaque trou suffisamment grand est considere comme une piece.
3. Conversion de la bounding box pixel -> metres via un facteur d'echelle fourni par
   l'utilisateur (pas de detection automatique d'echelle en V1).
4. OCR de la zone de chaque piece pour tenter de lire son label (cf room_naming.py).
"""
import cv2
import numpy as np

from app.ocr.service import extract_text_from_image

MIN_ROOM_AREA_RATIO = 0.005  # ignore le bruit trop petit (en fraction de la surface totale)
MAX_ROOM_AREA_RATIO = 0.6  # ignore les contours quasi aussi grands que le plan entier


class DetectedRoom:
    def __init__(self, x_px: int, y_px: int, w_px: int, h_px: int, ocr_text: str):
        self.x_px, self.y_px, self.w_px, self.h_px = x_px, y_px, w_px, h_px
        self.ocr_text = ocr_text


def detect_rooms(image_bytes: bytes) -> list[DetectedRoom]:
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image de plan illisible (format non reconnu par OpenCV)")

    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    total_area = image.shape[0] * image.shape[1]
    min_area = total_area * MIN_ROOM_AREA_RATIO
    max_area = total_area * MAX_ROOM_AREA_RATIO

    rooms: list[DetectedRoom] = []
    if hierarchy is None:
        return rooms

    for idx, contour in enumerate(contours):
        has_parent = hierarchy[0][idx][3] != -1
        area = cv2.contourArea(contour)
        if not has_parent or area < min_area or area > max_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        crop = image[y : y + h, x : x + w]
        ok, encoded = cv2.imencode(".png", crop)
        ocr_text = extract_text_from_image(encoded.tobytes()) if ok else ""
        rooms.append(DetectedRoom(x, y, w, h, ocr_text))

    if not rooms:
        # Repli : aucune piece detectee (plan trop simple/complexe pour l'heuristique) ->
        # on traite le plan entier comme une seule piece generique, a affiner via le
        # questionnaire. Evite un flux bloque en V1.
        h, w = image.shape
        rooms.append(DetectedRoom(0, 0, w, h, ""))

    return rooms
