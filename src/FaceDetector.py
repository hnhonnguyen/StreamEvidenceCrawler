from deepface import DeepFace
import time
import cv2
from PIL import Image
import os
from typing import List

class FaceDetector:
    def format_image(self, path: str) -> None:
        for r, _, f in os.walk(path):
            for file in f:
                exact_path = os.path.join(r, file)
                _, ext = os.path.splitext(exact_path)
                
                if ext.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                
                with Image.open(exact_path) as img:  # lazy
                    if img.format.lower() not in ["jpeg", "png"]:
                        img.save(exact_path.replace(ext, ".jpeg"))
    
    def draw_bounding_box(self, img, label, x, y, w, h):
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.8
        
        font_thickness = 1
        
        # Calculate text size to position the label correctly
        text_size, _ = cv2.getTextSize(label, font, font_scale, font_thickness)
        text_width, text_height = text_size

        if text_width > w:
            # Calculate how many characters fit in the width minus the length of "..."
            max_chars = len(label) * (w - cv2.getTextSize("...", font, font_scale, font_thickness)[0][0]) // text_width
            label = label[:max_chars] + "..."
        
        # Draw filled rectangle as the background for the label text
        cv2.rectangle(img, (x, y - text_height - 5), (x + w, y - 1), (0, 0, 255), cv2.FILLED)
        
        # Draw label text in white color
        cv2.putText(img, label, (x, y - 5), font, font_scale, (255, 255, 255), font_thickness)

    def write_images_side_by_side(self, img1, img2):

        # Resize images to have the same height
        height1, width1 = img1.shape[:2]
        height2, width2 = img2.shape[:2]

        if height1 != height2:
            # Resize img2 to the height of img1
            img2 = cv2.resize(img2, (int(width2 * height1 / height2), height1))

        # Concatenate images horizontally
        combined_image = cv2.hconcat([img1, img2])

        cv2.imwrite(f"label_1.jpg", combined_image)

    def face_extractor(self, img_path):
        start_time = time.time()
        result = DeepFace.extract_faces(img_path = img_path, detector_backend="yunet")
        duration = time.time() - start_time

        img = cv2.imread(img_path)
        label = img_path.split('/')[-1].split('.')[0].upper()
        for face in result:
            x, y, w, h = face['facial_area'].get('x'), face['facial_area'].get('y'), face['facial_area'].get('w'), face['facial_area'].get('h')
            self.draw_bounding_box(img, label, x, y, w, h)
        return img

    def face_verify(self, img1_path, img2_path):
        result = DeepFace.verify(img1_path = img1_path, img2_path = img2_path, detector_backend='yunet')
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)

        facial_areas_1 = result['facial_areas']["img1"]
        x1, y1, w1, h1 = facial_areas_1.get('x'), facial_areas_1.get('y'), facial_areas_1.get('w'), facial_areas_1.get('h')
        self.draw_bounding_box(img1, "VERIFIED", x1, y1, w1, h1)

        facial_areas_2 = result['facial_areas']["img2"]
        x2, y2, w2, h2 = facial_areas_2.get('x'), facial_areas_2.get('y'), facial_areas_2.get('w'), facial_areas_2.get('h')
        self.draw_bounding_box(img2, "VERIFIED", x2, y2, w2, h2)   
        return img1, img2

    def face_find(self, img_path):
        result = DeepFace.find(img_path = img_path, db_path= "/Users/hnhonnguyen/dev/StreamEvidenceCrawler/face_db", detector_backend='yunet', refresh_database=True)
        result = [df.to_dict() for df in result if len(df.to_dict()["identity"])>0]
        img = cv2.imread(img_path)
        for face in result:
            for i in face["identity"]:
                label = face['identity'][i].split("/")[-2]
                x, y, w, h = face["source_x"][i], face["source_y"][i], face["source_w"][i], face["source_h"][i]
                self.draw_bounding_box(img, label, x, y, w, h)
        return img