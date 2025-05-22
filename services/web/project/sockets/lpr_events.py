from flask_socketio import Namespace, emit
from flask import current_app
from datetime import datetime
from app.extensions import db
from app.models.detection import LPRDetection
import os

class LPRNamespace(Namespace):
    def on_connect(self):
        current_app.logger.info(f'[LPR] Connected: {self}')

    def on_disconnect(self):
        current_app.logger.info(f'[LPR] Disconnected: {self}')

    def on_lpr_detection(self, data):
        try:
            image_name = data.get('image_name', f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            image_binary = data.get('image_binary')
            save_path = os.path.join(current_app.config['MEDIA_FOLDER'], image_name)

            with open(save_path, 'wb') as f:
                f.write(image_binary)

            detection = LPRDetection(
                license_plate = data.get('license_plate'),
                image_path = f"media/{image_name}",
                timestamp = datetime.now(),
                location_lat = data.get('location_lat'),
                location_lon = data.get('location_lon'),
                info = data.get('info')
            )
            db.session.add(detection)
            db.session.commit()

            emit('lpr_response', {
                "status": "success",
                "message": "Detection saved",
                "detection": {
                    "id": detection.id,
                    "license_plate": detection.license_plate,
                    "image_path": detection.image_path
                }
            }, broadcast=True)

        except Exception as e:
            current_app.logger.error(f"LPR Error: {e}")
            emit('lpr_response', {"status": "error", "message": str(e)})
