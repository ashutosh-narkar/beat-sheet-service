from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import openai
import os

app = Flask(__name__)

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:flaskpassword@db:3306/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Fetch OpenAI API Key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

openai.api_key = OPENAI_API_KEY


# Act Model (associated with a Beat)
class Act(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in seconds
    cameraAngle = db.Column(db.String(100), nullable=True)

    beat_id = db.Column(db.Integer, db.ForeignKey('beat.id'), nullable=False)
    beat = db.relationship('Beat', back_populates='acts')

    def __repr__(self):
        return f"<Act {self.id} - {self.description}>"


# Beat Model (associated with a BeatSheet)
class Beat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    beat_sheet_id = db.Column(db.Integer, db.ForeignKey('beat_sheet.id'), nullable=False)
    beat_sheet = db.relationship('BeatSheet', back_populates='beats')
    acts = db.relationship('Act', back_populates='beat', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Beat {self.id} - {self.description}>"


# BeatSheet Model
class BeatSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    beats = db.relationship('Beat', back_populates='beat_sheet', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<BeatSheet {self.id} - {self.title}>"


# Initialize the database
with app.app_context():
    db.create_all()


# Create a new beat sheet
@app.route('/beatsheet', methods=['POST'])
def create_beat_sheet():
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({'message': 'Title is required'}), 400

    new_beat_sheet = BeatSheet(title=title)
    db.session.add(new_beat_sheet)
    db.session.commit()
    return jsonify({'id': new_beat_sheet.id, 'title': new_beat_sheet.title}), 201


# Retrieve a beat sheet by its ID
@app.route('/beatsheet/<int:id>', methods=['GET'])
def get_beat_sheet(id):
    beat_sheet = BeatSheet.query.get_or_404(id)
    result = {
        'id': beat_sheet.id,
        'title': beat_sheet.title,
        'beats': []
    }
    for beat in beat_sheet.beats:
        result['beats'].append({
            'id': beat.id,
            'description': beat.description,
            'timestamp': beat.timestamp,
            'acts': []
        })
        for act in beat.acts:
            result['beats'][-1]['acts'].append({
                'id': act.id,
                'description': act.description,
                'timestamp': act.timestamp,
                'duration': act.duration,
                'cameraAngle': act.cameraAngle
            })
    return jsonify(result)


# Update a beat sheet by its ID
@app.route('/beatsheet/<int:id>', methods=['PUT'])
def update_beat_sheet(id):
    data = request.get_json()
    beat_sheet = BeatSheet.query.get_or_404(id)
    beat_sheet.title = data.get('title', beat_sheet.title)
    db.session.commit()
    return jsonify({'id': beat_sheet.id, 'title': beat_sheet.title})


# Delete a beat sheet by its ID
@app.route('/beatsheet/<int:id>', methods=['DELETE'])
def delete_beat_sheet(id):
    beat_sheet = BeatSheet.query.get_or_404(id)
    db.session.delete(beat_sheet)
    db.session.commit()
    return jsonify({'message': 'Beat sheet deleted successfully'})


# List all beat sheets
@app.route('/beatsheet', methods=['GET'])
def get_beat_sheets():
    beat_sheets = BeatSheet.query.all()
    result = []
    for beat_sheet in beat_sheets:
        result.append({
            'id': beat_sheet.id,
            'title': beat_sheet.title
        })
    return jsonify(result)


# Add a beat to a specific beat sheet
@app.route('/beatsheet/<int:id>/beat', methods=['POST'])
def create_beat(id):
    data = request.get_json()
    description = data.get('description')
    if not description:
        return jsonify({'message': 'Description is required'}), 400

    beat_sheet = BeatSheet.query.get_or_404(id)
    new_beat = Beat(
        description=description,
        beat_sheet=beat_sheet
    )
    db.session.add(new_beat)
    db.session.commit()
    return jsonify({
        'id': new_beat.id,
        'description': new_beat.description,
        'timestamp': new_beat.timestamp
    }), 201


# Update a beat in a specific beat sheet
@app.route('/beatsheet/<int:beat_sheet_id>/beat/<int:beat_id>', methods=['PUT'])
def update_beat(beat_sheet_id, beat_id):
    data = request.get_json()

    # Find the BeatSheet by ID
    beat_sheet = BeatSheet.query.get_or_404(beat_sheet_id)

    # Find the Beat by ID within the specified BeatSheet
    beat = Beat.query.filter_by(id=beat_id, beat_sheet_id=beat_sheet.id).first()

    if not beat:
        return jsonify({'message': 'Beat not found'}), 404

    # Update the beat's description
    beat.description = data.get('description', beat.description)

    # Update the beat's timestamp to the current time
    beat.timestamp = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'id': beat.id,
        'description': beat.description,
        'timestamp': beat.timestamp
    })


# Delete a beat from a specific beat sheet.
@app.route('/beatsheet/<int:beat_sheet_id>/beat/<int:beat_id>', methods=['DELETE'])
def delete_beat(beat_sheet_id, beat_id):
    # Find the BeatSheet by ID
    beat_sheet = BeatSheet.query.get_or_404(beat_sheet_id)

    # Find the Beat by ID within the specified BeatSheet
    beat = Beat.query.filter_by(id=beat_id, beat_sheet_id=beat_sheet.id).first()

    if not beat:
        return jsonify({'message': 'Beat not found'}), 404

    # Delete the beat
    db.session.delete(beat)
    db.session.commit()

    return jsonify({'message': 'Beat deleted successfully'}), 200


# Add an act to a specific beat
@app.route('/beatsheet/<int:beat_sheet_id>/beat/<int:beat_id>/act', methods=['POST'])
def add_act_to_beat(beat_sheet_id, beat_id):
    data = request.get_json()

    # Find the BeatSheet by ID
    beat_sheet = BeatSheet.query.get_or_404(beat_sheet_id)

    # Find the Beat by ID within the specified BeatSheet
    beat = Beat.query.filter_by(id=beat_id, beat_sheet_id=beat_sheet.id).first()

    if not beat:
        return jsonify({'message': 'Beat not found'}), 404

    # Create a new Act
    new_act = Act(
        description=data['description'],
        duration=data['duration'],
        cameraAngle=data.get('cameraAngle'),
        beat=beat
    )

    # Add the Act to the database
    db.session.add(new_act)
    db.session.commit()

    return jsonify({
        'id': new_act.id,
        'description': new_act.description,
        'timestamp': new_act.timestamp,
        'duration': new_act.duration,
        'cameraAngle': new_act.cameraAngle
    }), 201


# Update an act in a specific beat
@app.route('/beatsheet/<int:beat_sheet_id>/beat/<int:beat_id>/act/<int:act_id>', methods=['PUT'])
def update_act_in_beat(beat_sheet_id, beat_id, act_id):
    data = request.get_json()

    # Find the BeatSheet by ID
    beat_sheet = BeatSheet.query.get_or_404(beat_sheet_id)

    # Find the Beat by ID within the specified BeatSheet
    beat = Beat.query.filter_by(id=beat_id, beat_sheet_id=beat_sheet.id).first()

    if not beat:
        return jsonify({'message': 'Beat not found'}), 404

    # Find the Act by ID within the specified Beat
    act = Act.query.filter_by(id=act_id, beat_id=beat.id).first()

    if not act:
        return jsonify({'message': 'Act not found'}), 404

    # Update Act fields
    act.description = data.get('description', act.description)
    act.duration = data.get('duration', act.duration)
    act.cameraAngle = data.get('cameraAngle', act.cameraAngle)
    act.timestamp = datetime.utcnow()  # Update timestamp to current time

    db.session.commit()

    return jsonify({
        'id': act.id,
        'description': act.description,
        'timestamp': act.timestamp,
        'duration': act.duration,
        'cameraAngle': act.cameraAngle
    })


# Delete an act from a specific beat
@app.route('/beatsheet/<int:beat_sheet_id>/beat/<int:beat_id>/act/<int:act_id>', methods=['DELETE'])
def delete_act_in_beat(beat_sheet_id, beat_id, act_id):
    # Find the BeatSheet by ID
    beat_sheet = BeatSheet.query.get_or_404(beat_sheet_id)

    # Find the Beat by ID within the specified BeatSheet
    beat = Beat.query.filter_by(id=beat_id, beat_sheet_id=beat_sheet.id).first()

    if not beat:
        return jsonify({'message': 'Beat not found'}), 404

    # Find the Act by ID within the specified Beat
    act = Act.query.filter_by(id=act_id, beat_id=beat.id).first()

    if not act:
        return jsonify({'message': 'Act not found'}), 404

    # Delete the Act
    db.session.delete(act)
    db.session.commit()

    return jsonify({'message': 'Act deleted successfully'}), 200


# Suggest the next beat or act
@app.route('/suggestion/next', methods=['POST'])
def suggest_next_beat_or_act():

    data = request.get_json()
    beat_sheet_id = data.get('beat_sheet_id')

    if not beat_sheet_id:
        return jsonify({'message': 'beat_sheet_id is required'}), 400

    beat_sheet = BeatSheet.query.get(beat_sheet_id)
    if not beat_sheet:
        return jsonify({"error": "Beat sheet not found"}), 404

    beats = [
        {
            "description": beat.description,
            "acts": [
                {
                    "description": act.description,
                    "duration": act.duration,
                    "camera_angle": act.cameraAngle,
                }
                for act in beat.acts
            ],
        }
        for beat in beat_sheet.beats
    ]

    # Construct prompt messages
    messages = [
        {"role": "system", "content": "Given the following beats and acts in a screenplay:"},
        {
            "role": "user",
            "content": f"Here is a beat sheet:\n{beats}\nSuggest the next beat or act to continue the story.",
        },
    ]

    # Call OpenAI to get the suggestion
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )

        response_dict = response.to_dict()

        # Extract the suggestion from OpenAI response
        suggestion = response_dict['choices'][0]['message']['content']
        return jsonify({'suggestion': suggestion}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_beats_and_acts(beat_sheet_id):
    beat_sheet = BeatSheet.query.get_or_404(beat_sheet_id)
    beats_and_acts = []

    for beat in beat_sheet.beats:
        beat_info = {
            'beat_description': beat.description,
            'acts': []
        }
        for act in beat.acts:
            beat_info['acts'].append({
                'description': act.description,
                'duration': act.duration,
                'cameraAngle': act.cameraAngle
            })
        beats_and_acts.append(beat_info)

    return beats_and_acts


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
