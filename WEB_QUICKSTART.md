# Web-Based Bayesian Belief Updating Experiment - Quick Start

## The experiment is now running! 🎉

### How to Access

Open your web browser and go to:
```
http://localhost:5000
```

Or click this link: [http://localhost:5000](http://localhost:5000)

### What Participants Will See

1. **Participant ID Entry** - Enter a unique ID to start
2. **Informed Consent** - Read and agree to participate
3. **Training Phase** - 10 practice trials with feedback
4. **Main Experiment**:
   - **RED JAR**: 40 trials of belief updating
   - **GREEN JAR**: 30 trials with a new jar
   - **Return to RED JAR**: 30 more trials with the original jar
5. **Thank You** - Automatic data save

### Features

- ✅ **Clean, professional interface**
- ✅ **Audio feedback** (ping/thunk sounds for drawing/replacing)
- ✅ **Visual sample history** with ball graphics
- ✅ **Running statistics** (black count, percentage)
- ✅ **Automatic data export** to CSV and JSON
- ✅ **Mobile responsive** design
- ✅ **No installation required** for participants

### Data Storage

All participant data is automatically saved in:
```
experiment_data/
├── participant_001_20251030_141234.json
├── participant_001_20251030_141234.csv
└── ...
```

### Starting the Server

The server is currently running. To start it again later:

```bash
python3 app.py
```

Then open http://localhost:5000 in your browser.

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

### Technical Details

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML/CSS/JavaScript (no external dependencies)
- **Audio**: Web Audio API (built into browsers)
- **Data**: JSON + CSV export

### Advantages Over Desktop Version

1. **No installation** - Participants just need a browser
2. **Cross-platform** - Works on Mac, Windows, Linux, tablets
3. **Remote testing** - Can be deployed to a server for online studies
4. **Better compatibility** - No Pygame/graphics driver issues
5. **Easier to maintain** - Standard web technologies

### Deploying Online (Optional)

To make this accessible over the internet:

1. Deploy to a platform like:
   - Heroku (free tier available)
   - PythonAnywhere
   - Google Cloud Run
   - AWS Elastic Beanstalk

2. Or use a tunneling service for quick testing:
   ```bash
   # Install ngrok
   # Then run:
   ngrok http 5000
   ```

### Browser Requirements

- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Audio support (for feedback sounds)
- Minimum screen width: 400px (mobile-friendly)

### Troubleshooting

**Port already in use:**
```bash
# Change port in app.py (last line):
app.run(debug=True, port=5001)  # Use different port
```

**Can't access from another computer:**
```bash
# Change to:
app.run(debug=True, host='0.0.0.0', port=5000)
# Then access via: http://YOUR_IP_ADDRESS:5000
```

**Audio not working:**
- The experiment will still work fine
- Visual feedback is provided
- Check browser audio permissions

### For Research Use

This experiment is ready for actual data collection. The interface matches the specification in your method section:

- ✅ Training with 11-urn display (0%, 10%, ..., 100%)
- ✅ Three-stage design (Red → Green → Red)
- ✅ Exact trial counts (40, 30, 30)
- ✅ Probability estimates + confidence ratings
- ✅ Sample history with visual display
- ✅ Audio feedback for drawing/replacement
- ✅ Initial estimate before samples
- ✅ Stage 3 retrieves prior belief state

### Questions?

The web version is simpler, more reliable, and easier to deploy than the Pygame version. Participants can complete the experiment from any device with a web browser.

Enjoy your experiment! 🧪
