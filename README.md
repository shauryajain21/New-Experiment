# Bayesian Belief Updating Experiment

**Saanika Banga | Professor Bob Rehder | NYU Psychology Department**

This program implements a multi-stage experiment investigating belief formation and updating under uncertainty, with a focus on Bayesian belief updating and prior retrieval.

## Overview

The experiment consists of:
1. **Training Phase**: 10 trials familiarizing participants with binomial sampling
2. **Stage 1 - Red Jar**: 40 trials of sequential belief updating
3. **Stage 2 - Green Jar**: 30 trials with a new jar
4. **Stage 3 - Return to Red Jar**: 30 trials testing prior belief retrieval

## Requirements

- Python 3.7 or higher
- Pygame library
- NumPy (for audio generation)

## Installation

1. Install Python dependencies:
```bash
pip install pygame numpy
```

2. Ensure you have the experiment file:
```bash
python bayesian_experiment.py
```

## Running the Experiment

1. Start the program:
```bash
python bayesian_experiment.py
```

2. Enter the participant ID when prompted

3. Read and agree to the informed consent

4. Follow the on-screen instructions for each phase

## Experiment Flow

### Training Phase
- Participants see a sample of balls and two candidate urns
- Task: Identify which urn generated the sample
- Immediate feedback provided
- 10 trials total

### Main Experiment

#### Stage 1: Red Jar (40 trials)
1. Participant provides initial probability estimate (expected ~50%)
2. For each trial:
   - Press SPACEBAR to draw a ball
   - Audio feedback: "ping" (draw) and "thunk" (replacement)
   - Enter probability estimate (0-100%)
   - Enter confidence rating (0-10)
   - Submit response
3. All previous balls remain visible

#### Stage 2: Green Jar (30 trials)
- Red jar is set aside
- New jar introduced with different probability
- Same procedure as Stage 1
- 30 trials

#### Stage 3: Return to Red Jar (30 trials)
- Green jar set aside
- Original red jar returns
- Previous sample history restored
- 30 additional trials
- Tests prior belief retrieval

## Data Output

Data is automatically saved in the `experiment_data/` directory with two formats:

### 1. JSON File
Complete structured data including:
- Participant ID and timestamp
- Training trial results
- All three stages with samples, estimates, and confidences
- True probabilities for each jar

### 2. CSV File
Trial-by-trial flattened data with columns:
- `participant_id`: Participant identifier
- `stage`: Stage number (stage1, stage2, stage3)
- `jar_color`: red or green
- `trial`: Trial number within stage
- `sample_color`: Color of drawn ball (black/white)
- `cumulative_black`: Running count of black balls
- `cumulative_total`: Total balls drawn so far
- `probability_estimate`: Participant's probability estimate (0-100)
- `confidence`: Confidence rating (0-10)
- `true_probability`: Actual probability of the jar

## Key Features

### Visual Design
- Color-coded jars (Red/Green) with visual distinction
- Sample history displayed as ball sequence
- Running statistics (black/total, percentage)
- Clear instructions at each stage

### Audio Feedback
- "Ping" sound when ball is drawn
- "Thunk" sound when ball is replaced
- Reinforces the with-replacement sampling procedure

### Data Integrity
- Random sampling with replacement ensures constant jar composition
- True probabilities randomly selected for ecological validity
- All responses timestamped and linked to trial sequence

### User Interface
- Spacebar to draw balls (self-paced)
- Text input for numerical responses
- Visual feedback on current state
- Previous estimate/confidence displayed

## Experimental Design Notes

### Sampling Procedure
- **With Replacement**: Each ball is returned to the jar after drawing
- **Random Generation**: Ball color determined by jar's true probability
- **Non-predetermined**: Sequences are genuinely random for each participant

### Key Measurements
1. **Probability Estimates**: Primary DV for belief updating analysis
2. **Confidence Ratings**: Metacognitive measure of certainty
3. **Sample Sequences**: Allows post-hoc Bayesian model comparison
4. **Response Times**: Implicitly captured in trial progression

### Stage 3 Design
The return to the Red Jar tests whether participants:
- Retrieve their prior belief state from Stage 1
- Resume updating from that point
- Or start fresh (failure to retrieve prior)

## Troubleshooting

### Audio Issues
If audio doesn't work:
- The experiment will continue without audio
- Visual feedback still provided
- Check system audio settings and Pygame mixer support

### Display Issues
If urns don't display properly:
- Ensure screen resolution is at least 1400x900
- Try full-screen mode if available
- Check graphics driver support for Pygame

### Data Not Saving
- Ensure write permissions in experiment directory
- Check that `experiment_data/` folder is created
- Verify disk space availability

## Customization

You can modify the following parameters in the code:

```python
# Number of trials per stage
TRAINING_TRIALS = 10  # Line in _run_training()
RED_STAGE1_TRIALS = 40  # Line in run()
GREEN_STAGE_TRIALS = 30
RED_STAGE3_TRIALS = 30

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900

# Sample display limits
visible_samples = self.samples[-30:]  # Show last 30 balls
```

## Citation

If you use this experiment program, please cite:

```
Banga, S., & Rehder, B. (2025). Bayesian Belief Updating Experiment [Computer software].
New York University, Department of Psychology.
```

## Contact

For questions about this experiment:
- Saanika Banga: [email]
- Professor Bob Rehder: [email]
- NYU Psychology Department

## License

This software is provided for academic research purposes.
