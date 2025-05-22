from flask.cli import FlaskGroup
from services.web.project.__init__tmp import app, db, User, LPRDetection, socketio
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    #Drop and create the database.
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(User(username="admin", email="admin@bs4u-tech.com"))
    db.session.commit()


@cli.command("seed_lpr")
def seed_lpr():
    bangkok_tz = pytz_timezone("Asia/Bangkok")  # Set the timezone to Bangkok (UTC+7)
    db.session.add(LPRDetection(
        license_plate="ABC123",
        image_path="/media/abc123.jpg",
        #timestamp=datetime.now(timezone.utc),
        timestamp=datetime.now(bangkok_tz),
        location_lat=37.7749,
        location_lon=-122.4194,
        info="Sample detection"
    ))
    db.session.commit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:  # If there are CLI arguments, run the CLI
        cli()
    else:  # Otherwise, start the Socket.IO server
        socketio.run(app, host="0.0.0.0", port=5001)