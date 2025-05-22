import os
import base64
import eventlet
eventlet.monkey_patch() # must be called before importing socketio and flask_socketio

from flask import Flask, current_app, jsonify, session,send_from_directory, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from datetime import datetime
import subprocess
import logging
import paramiko #for ssh connection
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

SSH_password = os.getenv("SSH_PASSWORD")
# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
app.config.from_object('project.config.Config')
db = SQLAlchemy(app)
if not app.debug:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
app.logger.info("Server started and waiting for connections")


socketio = SocketIO(app, 
                    async_mode='eventlet', 
                    cors_allowed_origins=["http://lprserver.tail605477.ts.net:1337", "http://localhost:1337", "http://lprserver:1337"],
                    ping_timeout=20,     # seconds before dropping client
                    ping_interval=10     # how often to send ping
                    )
login_manager = LoginManager()
# Init extensions
db.init_app(app)
socketio.init_app(app, async_mode='eventlet')  # หรือ gevent


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return f'<User {self.username}>'


class LPRDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    location_lat = db.Column(db.Float, nullable=True)
    location_lon = db.Column(db.Float, nullable=True)
    info = db.Column(db.Text, nullable=True)

    def __init__(self, license_plate, image_path, timestamp, location_lat=None, location_lon=None, info=None):
        self.license_plate = license_plate
        self.image_path = image_path
        self.timestamp = timestamp
        self.location_lat = location_lat
        self.location_lon = location_lon
        self.info = info

    def __repr__(self):
        return f'<LPRDetection {self.license_plate}>'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)
@app.route('/media/<path:filename>')
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)

@app.route('/upload', methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['MEDIA_FOLDER'], filename))
    return """
            <!doctype html>
            <title>File Upload</title>
            <h1>File uploaded successfully</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
            <p><input type="file" name="file">
            <input type="submit" value="Upload">
            </form>
            """

@app.route('/health')
def health_check():
    return jsonify(status="The AI Camera healthy is GOOD")
@app.route('/status')
def status():
    return jsonify(status="The AI Camera is running")
@app.route('/info')
def info():
    return jsonify(info="This is a sample of The AI Camera  application.")
@app.route('/version')
def version():
    return jsonify(version="The AI Camera version 1.0.0")

@app.route('/runscript', methods=['POST'])
def send_order():
    try:
        # Trigger Python script execution (local example)
        result = subprocess.run(['python3', 'your_script.py'], capture_output=True, text=True)
        return jsonify({'status': 'success', 'output': result.stdout})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/remote_capture', methods=['POST'])
def run_remote_capture(edge_ip):
    
    data = request.get_json()
    edge_hostname = data.get('edge_hostname')

    if not edge_hostname:
        return jsonify({'status': 'error', 'error': 'Missing edge_hostname'}), 400

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(edge_hostname, username='camuser', password=SSH_password)
        stdin, stdout, stderr = ssh.exec_command('python3 /home/camuser/hailo/alpr_binary.py')
        output = stdout.read().decode()
        ssh.close()
        return jsonify({'status': 'success', 'output': output})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})
@app.route('/detections')
def list_detections():
    detections = LPRDetection.query.all()
    return render_template('detections_list.html', detections=detections)

@app.route('/detections/<int:detection_id>')
def detection_detail(detection_id):
    detection = LPRDetection.query.get_or_404(detection_id)
    return render_template('detection_detail.html', detection=detection)

@socketio.on('debug_event')
def handle_debug_event(data):
    current_app.logger.info(f"📩 >>> Received debug_event from client: {data}")
    response = {'status': 'received', 'echo': data}
    socketio.emit('debug_response', response)

@socketio.on('client_quit')
def handle_client_quit(data):
    current_app.logger.info(f"🚪 Client wants to disconnect: {data}")
    socketio.emit('quit_ack', {'status': 'ok'})  # optional: ยืนยันกลับไป

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    current_app.logger.info(f"🔗 >>> Client connected with session ID: {sid}")
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    current_app.logger.info(f"❌>>>  Client disconnected with session ID: {sid}")


#filename = secure_filename(file.filename)
#file.save(os.path.join(app.config['MEDIA_FOLDER'], filename))
# Socket.IO event to handle incoming LPR detection data
@socketio.on('lpr_detection')
def handle_lpr_detection(data):
    try:
        current_app.logger.info(f"📩 >>> Received lpr_detection event with data")
        # Extract data from the received JSON
        image_name = data.get('image_name', f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        #image_b64 = data['image_b64']
        image_binary = data.get('image_binary')
        # บันทึกไฟล์
        save_path = os.path.join(app.config['MEDIA_FOLDER'], image_name)
        # Convert absolute path to relative for database storage
        relative_path = f"media/{image_name}"
        with open(save_path , 'wb') as f:
            f.write(image_binary)
            
        license_plate = data.get('license_plate')
        current_app.logger.info(f"[✓] บันทึกภาพ LPR สำเร็จ และส่งทะเบียน: {license_plate} กลับมา")
        # Save to the database
        detection = LPRDetection(
            license_plate = data.get('license_plate'),
            image_path = relative_path,  # Store relative path
            timestamp = datetime.now(),
            location_lat = data.get('location_lat'),
            location_lon = data.get('location_lon'),
            info = data.get('info')
        )
        db.session.add(detection)
        db.session.commit()
        current_app.logger.info(f"[✓] บันทึกข้อมูล LPR สำเร็จ: {detection}")
        # ส่งข้อมูลกลับให้ client
        socketio.emit('lpr_response', {
            "status": "success",
            "message": "ภาพและข้อมูลถูกบันทึกเรียบร้อย",
            "saved_path": save_path
        })

        current_app.logger.info(f"Detection saved: {detection}")

        current_app.logger.info(f"[✓] บันทึกภาพและข้อมูล LPR สำเร็จ: {save_path}")

    except Exception as e:
        logging.error(f"Error handling lpr_detection event: {e}")
        current_app.logger.error(f"[ERROR] การบันทึกล้มเหลว: {e}")
        socketio.emit('lpr_response', {
            "status": "error",
            "message": str(e)
        })
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=1337, debug=True)
    app.logger.info(">>> Server running on port 1337")
 

