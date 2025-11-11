"""
Flask Web Server for Bayesian Belief Updating Experiment
Professor Bob Rehder Lab, NYU Psychology Department
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import csv
from datetime import datetime
from pathlib import Path
import random

app = Flask(__name__)

# Store experiment data in memory (in production, use a database)
experiment_data = {}

@app.route('/')
def index():
    """Serve the main experiment page"""
    return render_template('experiment.html')

@app.route('/api/start_experiment', methods=['POST'])
def start_experiment():
    """Initialize a new experiment session"""
    data = request.json
    participant_id = data.get('participant_id')

    if not participant_id:
        return jsonify({'error': 'Participant ID required'}), 400

    # Generate random probabilities for the jars
    red_jar_prob = random.random()
    green_jar_prob = random.random()

    # Initialize experiment data
    experiment_data[participant_id] = {
        'participant_id': participant_id,
        'timestamp': datetime.now().isoformat(),
        'red_jar_probability': red_jar_prob,
        'green_jar_probability': green_jar_prob,
        'training_trials': [],
        'red_jar_stage1': {
            'samples': [],
            'estimates': [],
            'confidences': []
        },
        'green_jar_stage2': {
            'samples': [],
            'estimates': [],
            'confidences': []
        },
        'red_jar_stage3': {
            'samples': [],
            'estimates': [],
            'confidences': []
        }
    }

    return jsonify({
        'success': True,
        'participant_id': participant_id
    })

@app.route('/api/draw_ball', methods=['POST'])
def draw_ball():
    """Draw a ball from the specified jar"""
    data = request.json
    participant_id = data.get('participant_id')
    jar_type = data.get('jar_type')  # 'red' or 'green'

    if participant_id not in experiment_data:
        return jsonify({'error': 'Invalid participant ID'}), 400

    # Get the appropriate probability
    if jar_type == 'red':
        probability = experiment_data[participant_id]['red_jar_probability']
    else:
        probability = experiment_data[participant_id]['green_jar_probability']

    # Draw a ball (random with replacement)
    ball_color = 'black' if random.random() < probability else 'white'

    return jsonify({
        'ball_color': ball_color
    })

@app.route('/api/submit_trial', methods=['POST'])
def submit_trial():
    """Submit trial data"""
    data = request.json
    participant_id = data.get('participant_id')
    stage = data.get('stage')  # 'red_jar_stage1', 'green_jar_stage2', 'red_jar_stage3'
    ball_color = data.get('ball_color')
    estimate = data.get('estimate')
    confidence = data.get('confidence')

    if participant_id not in experiment_data:
        return jsonify({'error': 'Invalid participant ID'}), 400

    # Store the data
    experiment_data[participant_id][stage]['samples'].append(ball_color)
    experiment_data[participant_id][stage]['estimates'].append(estimate)
    experiment_data[participant_id][stage]['confidences'].append(confidence)

    return jsonify({'success': True})

@app.route('/api/submit_training', methods=['POST'])
def submit_training():
    """Submit training trial data"""
    data = request.json
    participant_id = data.get('participant_id')
    trial_num = data.get('trial_num')
    result = data.get('result')

    if participant_id not in experiment_data:
        return jsonify({'error': 'Invalid participant ID'}), 400

    experiment_data[participant_id]['training_trials'].append({
        'trial': trial_num,
        'result': result
    })

    return jsonify({'success': True})

@app.route('/api/get_stage_data', methods=['POST'])
def get_stage_data():
    """Get data from a specific stage (for returning to red jar)"""
    data = request.json
    participant_id = data.get('participant_id')
    stage = data.get('stage')

    if participant_id not in experiment_data:
        return jsonify({'error': 'Invalid participant ID'}), 400

    stage_data = experiment_data[participant_id][stage]

    return jsonify({
        'samples': stage_data['samples'],
        'estimates': stage_data['estimates'],
        'confidences': stage_data['confidences']
    })

@app.route('/api/export_data', methods=['POST'])
def export_data():
    """Export experiment data"""
    data = request.json
    participant_id = data.get('participant_id')

    if participant_id not in experiment_data:
        return jsonify({'error': 'Invalid participant ID'}), 400

    # Create data directory
    data_dir = Path('experiment_data')
    data_dir.mkdir(exist_ok=True)

    participant_data = experiment_data[participant_id]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_file = data_dir / f'participant_{participant_id}_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(participant_data, f, indent=2)

    # Save CSV
    csv_file = data_dir / f'participant_{participant_id}_{timestamp}.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['participant_id', 'stage', 'jar_color', 'trial',
                        'sample_color', 'cumulative_black', 'cumulative_total',
                        'probability_estimate', 'confidence', 'true_probability'])

        # Write data for each stage
        for stage_name in ['red_jar_stage1', 'green_jar_stage2', 'red_jar_stage3']:
            stage_data = participant_data.get(stage_name)
            if stage_data and stage_data['samples']:
                jar_color = 'red' if 'red' in stage_name else 'green'
                stage_num = stage_name.split('_')[-1]
                true_prob = participant_data['red_jar_probability'] if jar_color == 'red' else participant_data['green_jar_probability']

                cumulative_black = 0
                for trial in range(len(stage_data['samples'])):
                    sample = stage_data['samples'][trial]
                    if sample == 'black':
                        cumulative_black += 1

                    estimate = stage_data['estimates'][trial] if trial < len(stage_data['estimates']) else ''
                    confidence = stage_data['confidences'][trial] if trial < len(stage_data['confidences']) else ''

                    writer.writerow([
                        participant_id, stage_num, jar_color, trial + 1,
                        sample, cumulative_black, trial + 1,
                        estimate, confidence, true_prob
                    ])

    return jsonify({
        'success': True,
        'json_file': str(json_file),
        'csv_file': str(csv_file)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
