"""
Bayesian Belief Updating Experiment
Professor Bob Rehder Lab
NYU Psychology Department

This program implements a multi-stage experiment investigating
belief formation and updating under uncertainty.
"""

import pygame
import random
import csv
import json
from datetime import datetime
from pathlib import Path
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
LIGHT_RED = (255, 200, 200)
LIGHT_GREEN = (200, 255, 200)
BLUE = (50, 50, 200)

# Fonts
TITLE_FONT = pygame.font.Font(None, 48)
LARGE_FONT = pygame.font.Font(None, 36)
MEDIUM_FONT = pygame.font.Font(None, 28)
SMALL_FONT = pygame.font.Font(None, 24)

class AudioManager:
    """Manages audio feedback for the experiment"""

    def __init__(self):
        self.enabled = True
        try:
            # Create simple audio tones
            self.draw_sound = self._create_tone(440, 0.1)  # A4 note for draw
            self.replace_sound = self._create_tone(220, 0.15)  # A3 note for replace
        except:
            print("Audio initialization failed. Continuing without audio.")
            self.enabled = False

    def _create_tone(self, frequency, duration):
        """Create a simple sine wave tone"""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = []
        for i in range(n_samples):
            value = int(32767.0 * 0.3 *
                       pygame.math.Vector2(1, 0).rotate(
                           360.0 * frequency * i / sample_rate).x)
            buf.append([value, value])
        sound = pygame.sndarray.make_sound(pygame.array.array('h',
                                          [item for sublist in buf for item in sublist]))
        return sound

    def play_draw(self):
        """Play 'ping' sound for ball draw"""
        if self.enabled:
            try:
                self.draw_sound.play()
            except:
                pass

    def play_replace(self):
        """Play 'thunk' sound for ball replacement"""
        if self.enabled:
            try:
                self.replace_sound.play()
            except:
                pass

class Urn:
    """Represents an urn with a specific probability of drawing a black ball"""

    def __init__(self, probability):
        """
        Args:
            probability (float): Probability of drawing a black ball (0.0 to 1.0)
        """
        self.probability = probability
        self.black_balls = int(probability * 100)
        self.white_balls = 100 - self.black_balls

    def draw_ball(self):
        """
        Draw a ball from the urn (with replacement)

        Returns:
            str: 'black' or 'white'
        """
        return 'black' if random.random() < self.probability else 'white'

    def draw_visual(self, screen, x, y, width, height, label=None, color=None):
        """
        Draw the urn visualization

        Args:
            screen: Pygame screen surface
            x, y: Top-left coordinates
            width, height: Dimensions
            label: Optional label text
            color: Optional border color (default: black)
        """
        border_color = color if color else BLACK

        # Draw urn container
        pygame.draw.rect(screen, WHITE, (x, y, width, height))
        pygame.draw.rect(screen, border_color, (x, y, width, height), 3)

        # Calculate ball display
        balls_per_row = 10
        ball_size = min(width // (balls_per_row + 1), height // 12)
        padding = 5

        # Draw balls
        ball_count = 0
        for row in range(10):
            for col in range(balls_per_row):
                if ball_count < 100:
                    ball_x = x + padding + col * (ball_size + 2)
                    ball_y = y + padding + row * (ball_size + 2)

                    # Determine ball color
                    ball_color = BLACK if ball_count < self.black_balls else WHITE
                    pygame.draw.circle(screen, ball_color,
                                     (ball_x + ball_size // 2, ball_y + ball_size // 2),
                                     ball_size // 2)
                    pygame.draw.circle(screen, GRAY,
                                     (ball_x + ball_size // 2, ball_y + ball_size // 2),
                                     ball_size // 2, 1)
                    ball_count += 1

        # Draw label
        if label is not None:
            label_surface = MEDIUM_FONT.render(str(label), True, BLACK)
            label_rect = label_surface.get_rect(centerx=x + width // 2, top=y + height + 5)
            screen.blit(label_surface, label_rect)

class Ball:
    """Represents a drawn ball in the sample sequence"""

    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.size = 20

    def draw(self, screen):
        """Draw the ball"""
        ball_color = BLACK if self.color == 'black' else WHITE
        pygame.draw.circle(screen, ball_color, self.position, self.size)
        pygame.draw.circle(screen, GRAY, self.position, self.size, 2)

class InputBox:
    """Text input box for numerical responses"""

    def __init__(self, x, y, width, height, label, min_val=0, max_val=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = ''
        self.active = False
        self.min_val = min_val
        self.max_val = max_val

    def handle_event(self, event):
        """Handle keyboard input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True  # Signal submission
            elif event.unicode.isdigit() or event.unicode == '.':
                self.text += event.unicode

        return False

    def draw(self, screen):
        """Draw the input box"""
        # Draw label
        label_surface = MEDIUM_FONT.render(self.label, True, BLACK)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))

        # Draw box
        color = BLUE if self.active else GRAY
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, color, self.rect, 2)

        # Draw text
        text_surface = MEDIUM_FONT.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def get_value(self):
        """Get the numerical value, or None if invalid"""
        try:
            value = float(self.text)
            if self.min_val <= value <= self.max_val:
                return value
        except ValueError:
            pass
        return None

    def clear(self):
        """Clear the input"""
        self.text = ''
        self.active = False

class Button:
    """Clickable button"""

    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def handle_event(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        """Draw the button"""
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        text_surface = MEDIUM_FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class TrainingTrial:
    """Represents a single training trial"""

    def __init__(self, screen, audio_manager):
        self.screen = screen
        self.audio = audio_manager

        # Select two random urns from the 11-urn set
        available_probs = [i / 100 for i in range(0, 101, 10)]
        selected = random.sample(available_probs, 2)

        self.urn_a = Urn(selected[0])
        self.urn_b = Urn(selected[1])

        # The true source is randomly selected
        self.true_urn = random.choice([self.urn_a, self.urn_b])

        # Generate sample (5-10 balls)
        sample_size = random.randint(5, 10)
        self.sample = [self.true_urn.draw_ball() for _ in range(sample_size)]

        self.result = None  # Will store 'correct' or 'incorrect'

    def run(self):
        """Run the training trial"""
        running = True

        # Create buttons for selection
        button_a = Button(300, 650, 200, 60, f"Urn A ({int(self.urn_a.probability * 100)}%)", RED)
        button_b = Button(900, 650, 200, 60, f"Urn B ({int(self.urn_b.probability * 100)}%)", GREEN)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if button_a.handle_event(event):
                    self.result = 'correct' if self.true_urn == self.urn_a else 'incorrect'
                    running = False

                if button_b.handle_event(event):
                    self.result = 'correct' if self.true_urn == self.urn_b else 'incorrect'
                    running = False

            # Draw everything
            self.screen.fill(WHITE)

            # Title
            title = TITLE_FONT.render("Training Trial", True, BLACK)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

            # Instructions
            inst = SMALL_FONT.render("Which urn was the source of this sample?", True, BLACK)
            self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 80))

            # Draw sample balls
            sample_y = 120
            ball_spacing = 35
            start_x = SCREEN_WIDTH // 2 - (len(self.sample) * ball_spacing) // 2

            sample_label = MEDIUM_FONT.render("Sample:", True, BLACK)
            self.screen.blit(sample_label, (start_x - 100, sample_y))

            for i, ball_color in enumerate(self.sample):
                ball = Ball(ball_color, (start_x + i * ball_spacing, sample_y + 20))
                ball.draw(self.screen)

            # Draw the two candidate urns
            self.urn_a.draw_visual(self.screen, 250, 200, 250, 400,
                                  f"Urn A\n{int(self.urn_a.probability * 100)}% Black", RED)
            self.urn_b.draw_visual(self.screen, 850, 200, 250, 400,
                                  f"Urn B\n{int(self.urn_b.probability * 100)}% Black", GREEN)

            # Draw buttons
            button_a.draw(self.screen)
            button_b.draw(self.screen)

            pygame.display.flip()

        # Show feedback
        self._show_feedback()

        return self.result

    def _show_feedback(self):
        """Show feedback on the response"""
        feedback_duration = 1500  # ms
        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < feedback_duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(WHITE)

            if self.result == 'correct':
                feedback_text = LARGE_FONT.render("Correct!", True, GREEN)
            else:
                feedback_text = LARGE_FONT.render("Incorrect", True, RED)
                correct_text = MEDIUM_FONT.render(
                    f"The correct answer was {'A' if self.true_urn == self.urn_a else 'B'}",
                    True, BLACK)
                self.screen.blit(correct_text,
                               (SCREEN_WIDTH // 2 - correct_text.get_width() // 2, 400))

            self.screen.blit(feedback_text,
                           (SCREEN_WIDTH // 2 - feedback_text.get_width() // 2, 350))

            pygame.display.flip()

class MainExperimentStage:
    """Represents one stage of the main experiment (Red, Green, or Return to Red)"""

    def __init__(self, screen, audio_manager, jar_color, num_trials,
                 jar_probability=None, previous_data=None):
        """
        Args:
            screen: Pygame screen
            audio_manager: AudioManager instance
            jar_color: 'red' or 'green'
            num_trials: Number of trials for this stage
            jar_probability: True probability (if None, randomly selected)
            previous_data: Data from previous stage (for returning to jar)
        """
        self.screen = screen
        self.audio = audio_manager
        self.jar_color = jar_color
        self.num_trials = num_trials

        # Create or restore urn
        if jar_probability is None:
            self.urn = Urn(random.random())
        else:
            self.urn = Urn(jar_probability)

        # Sample history
        if previous_data:
            self.samples = previous_data['samples']
            self.estimates = previous_data['estimates']
            self.confidences = previous_data['confidences']
            self.current_trial = len(self.samples)
        else:
            self.samples = []
            self.estimates = []
            self.confidences = []
            self.current_trial = 0

        self.waiting_for_draw = True
        self.waiting_for_estimate = False

        # Input boxes
        self.estimate_input = InputBox(SCREEN_WIDTH // 2 - 150, 650, 150, 40,
                                      "Probability (0-100%):", 0, 100)
        self.confidence_input = InputBox(SCREEN_WIDTH // 2 + 50, 650, 150, 40,
                                        "Confidence (0-10):", 0, 10)

        # Submit button
        self.submit_button = Button(SCREEN_WIDTH // 2 - 75, 720, 150, 50, "Submit")

        # Initial estimate flag
        self.need_initial_estimate = (self.current_trial == 0 and not previous_data)

    def run(self):
        """Run this stage of the experiment"""
        clock = pygame.time.Clock()

        # Get initial estimate if this is a new jar
        if self.need_initial_estimate:
            self._get_initial_estimate()
            self.need_initial_estimate = False

        while self.current_trial < self.num_trials:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle spacebar for drawing ball
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.waiting_for_draw:
                        self._draw_ball()

                # Handle input boxes
                if self.waiting_for_estimate:
                    self.estimate_input.handle_event(event)
                    self.confidence_input.handle_event(event)

                    if self.submit_button.handle_event(event):
                        self._submit_response()

            # Draw everything
            self._draw_screen()

            pygame.display.flip()
            clock.tick(FPS)

        # Return data for potential later retrieval
        return {
            'samples': self.samples,
            'estimates': self.estimates,
            'confidences': self.confidences,
            'true_probability': self.urn.probability
        }

    def _get_initial_estimate(self):
        """Get the initial probability estimate before any samples"""
        waiting = True

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.estimate_input.handle_event(event)

                if self.submit_button.handle_event(event):
                    estimate = self.estimate_input.get_value()
                    if estimate is not None:
                        self.estimates.append(estimate)
                        self.estimate_input.clear()
                        waiting = False

            self.screen.fill(WHITE)

            # Title
            color = RED if self.jar_color == 'red' else GREEN
            title = TITLE_FONT.render(f"{self.jar_color.upper()} JAR", True, color)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

            # Instructions
            inst1 = MEDIUM_FONT.render("A jar has been randomly selected from all possible jars.",
                                      True, BLACK)
            inst2 = MEDIUM_FONT.render("What is your initial estimate of the probability",
                                      True, BLACK)
            inst3 = MEDIUM_FONT.render("of drawing a black ball? (Before seeing any samples)",
                                      True, BLACK)

            self.screen.blit(inst1, (SCREEN_WIDTH // 2 - inst1.get_width() // 2, 200))
            self.screen.blit(inst2, (SCREEN_WIDTH // 2 - inst2.get_width() // 2, 250))
            self.screen.blit(inst3, (SCREEN_WIDTH // 2 - inst3.get_width() // 2, 290))

            # Draw jar representation
            jar_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 250)
            pygame.draw.rect(self.screen, WHITE, jar_rect)
            pygame.draw.rect(self.screen, color, jar_rect, 4)

            question_mark = TITLE_FONT.render("?", True, GRAY)
            self.screen.blit(question_mark,
                           (jar_rect.centerx - question_mark.get_width() // 2,
                            jar_rect.centery - question_mark.get_height() // 2))

            # Input
            self.estimate_input.draw(self.screen)
            self.submit_button.draw(self.screen)

            pygame.display.flip()

    def _draw_ball(self):
        """Draw a ball from the urn"""
        ball_color = self.urn.draw_ball()
        self.samples.append(ball_color)
        self.audio.play_draw()

        # Wait a moment, then play replace sound
        pygame.time.wait(150)
        self.audio.play_replace()

        self.waiting_for_draw = False
        self.waiting_for_estimate = True

    def _submit_response(self):
        """Submit the estimate and confidence rating"""
        estimate = self.estimate_input.get_value()
        confidence = self.confidence_input.get_value()

        if estimate is not None and confidence is not None:
            self.estimates.append(estimate)
            self.confidences.append(confidence)

            self.estimate_input.clear()
            self.confidence_input.clear()

            self.current_trial += 1
            self.waiting_for_estimate = False
            self.waiting_for_draw = True

    def _draw_screen(self):
        """Draw the main experiment screen"""
        self.screen.fill(WHITE)

        # Title with jar color
        color = RED if self.jar_color == 'red' else GREEN
        bg_color = LIGHT_RED if self.jar_color == 'red' else LIGHT_GREEN

        # Background banner
        pygame.draw.rect(self.screen, bg_color, (0, 0, SCREEN_WIDTH, 100))

        title = TITLE_FONT.render(f"{self.jar_color.upper()} JAR - Trial {self.current_trial + 1}/{self.num_trials}",
                                 True, color)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Instructions
        if self.waiting_for_draw:
            inst = MEDIUM_FONT.render("Press SPACEBAR to draw a ball", True, BLACK)
        else:
            inst = MEDIUM_FONT.render("Enter your estimate and confidence, then submit",
                                     True, BLACK)
        self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 120))

        # Sample history
        history_y = 180
        history_label = SMALL_FONT.render(f"Sample History ({len(self.samples)} balls):",
                                         True, BLACK)
        self.screen.blit(history_label, (50, history_y))

        # Draw sample balls (show last 30 to fit on screen)
        visible_samples = self.samples[-30:] if len(self.samples) > 30 else self.samples
        ball_size = 15
        ball_spacing = 30
        balls_per_row = 30

        for i, ball_color in enumerate(visible_samples):
            row = i // balls_per_row
            col = i % balls_per_row
            x = 50 + col * ball_spacing
            y = history_y + 40 + row * ball_spacing

            color_val = BLACK if ball_color == 'black' else WHITE
            pygame.draw.circle(self.screen, color_val, (x, y), ball_size)
            pygame.draw.circle(self.screen, GRAY, (x, y), ball_size, 2)

        # Summary statistics
        if len(self.samples) > 0:
            black_count = sum(1 for s in self.samples if s == 'black')
            proportion = (black_count / len(self.samples)) * 100

            stats_y = 180
            stats = SMALL_FONT.render(
                f"Black: {black_count}/{len(self.samples)} ({proportion:.1f}%)",
                True, BLACK)
            self.screen.blit(stats, (SCREEN_WIDTH - 250, stats_y))

        # Draw jar visualization in center
        jar_y = 280
        jar_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, jar_y, 150, 300)
        pygame.draw.rect(self.screen, WHITE, jar_rect)
        pygame.draw.rect(self.screen, color, jar_rect, 5)

        jar_label = LARGE_FONT.render("?", True, GRAY)
        self.screen.blit(jar_label,
                        (jar_rect.centerx - jar_label.get_width() // 2,
                         jar_rect.centery - jar_label.get_height() // 2))

        # Input boxes (only show when waiting for estimate)
        if self.waiting_for_estimate:
            self.estimate_input.draw(self.screen)
            self.confidence_input.draw(self.screen)
            self.submit_button.draw(self.screen)

        # Show most recent estimate and confidence
        if len(self.estimates) > 0:
            recent_est = SMALL_FONT.render(
                f"Last estimate: {self.estimates[-1]:.1f}%", True, DARK_GRAY)
            self.screen.blit(recent_est, (50, SCREEN_HEIGHT - 100))

        if len(self.confidences) > 0:
            recent_conf = SMALL_FONT.render(
                f"Last confidence: {self.confidences[-1]:.1f}/10", True, DARK_GRAY)
            self.screen.blit(recent_conf, (50, SCREEN_HEIGHT - 70))

class DataCollector:
    """Handles data collection and export"""

    def __init__(self, participant_id):
        self.participant_id = participant_id
        self.data = {
            'participant_id': participant_id,
            'timestamp': datetime.now().isoformat(),
            'training_trials': [],
            'red_jar_stage1': None,
            'green_jar_stage2': None,
            'red_jar_stage3': None
        }

        # Create data directory if it doesn't exist
        self.data_dir = Path('experiment_data')
        self.data_dir.mkdir(exist_ok=True)

    def add_training_trial(self, trial_num, result):
        """Add training trial data"""
        self.data['training_trials'].append({
            'trial': trial_num,
            'result': result
        })

    def add_stage_data(self, stage_name, stage_data):
        """Add main experiment stage data"""
        self.data[stage_name] = stage_data

    def export(self):
        """Export data to CSV and JSON"""
        # JSON export (complete data)
        json_file = self.data_dir / f'participant_{self.participant_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(json_file, 'w') as f:
            json.dump(self.data, f, indent=2)

        # CSV export (flattened trial-by-trial data)
        csv_file = self.data_dir / f'participant_{self.participant_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['participant_id', 'stage', 'jar_color', 'trial',
                           'sample_color', 'cumulative_black', 'cumulative_total',
                           'probability_estimate', 'confidence', 'true_probability'])

            # Write data for each stage
            for stage_name in ['red_jar_stage1', 'green_jar_stage2', 'red_jar_stage3']:
                stage_data = self.data.get(stage_name)
                if stage_data:
                    jar_color = 'red' if 'red' in stage_name else 'green'
                    stage_num = stage_name.split('_')[-1]

                    cumulative_black = 0
                    for trial in range(len(stage_data['samples'])):
                        sample = stage_data['samples'][trial]
                        if sample == 'black':
                            cumulative_black += 1

                        estimate = stage_data['estimates'][trial] if trial < len(stage_data['estimates']) else ''
                        confidence = stage_data['confidences'][trial] if trial < len(stage_data['confidences']) else ''

                        writer.writerow([
                            self.participant_id,
                            stage_num,
                            jar_color,
                            trial + 1,
                            sample,
                            cumulative_black,
                            trial + 1,
                            estimate,
                            confidence,
                            stage_data['true_probability']
                        ])

        print(f"\nData saved to:")
        print(f"  {json_file}")
        print(f"  {csv_file}")

class ConsentScreen:
    """Display consent form and collect consent"""

    def __init__(self, screen):
        self.screen = screen

    def run(self):
        """Display consent and wait for agreement"""
        consent_given = False

        agree_button = Button(SCREEN_WIDTH // 2 - 200, 700, 150, 50, "I Agree", GREEN)
        decline_button = Button(SCREEN_WIDTH // 2 + 50, 700, 150, 50, "Decline", RED)

        while not consent_given:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if agree_button.handle_event(event):
                    consent_given = True

                if decline_button.handle_event(event):
                    return False

            self.screen.fill(WHITE)

            # Title
            title = TITLE_FONT.render("Informed Consent", True, BLACK)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

            # Consent text
            consent_text = [
                "You are invited to participate in a research study investigating",
                "how people form judgments under conditions of uncertainty.",
                "",
                "The study will take approximately 30 minutes.",
                "You will be compensated for your time.",
                "",
                "Your participation is voluntary and you may withdraw at any time.",
                "All data will be kept confidential and anonymous.",
                "",
                "By clicking 'I Agree', you confirm that you:",
                "  - Are at least 18 years old",
                "  - Have read and understood this information",
                "  - Voluntarily agree to participate"
            ]

            y = 150
            for line in consent_text:
                text_surface = SMALL_FONT.render(line, True, BLACK)
                self.screen.blit(text_surface, (100, y))
                y += 35

            # Draw buttons
            agree_button.draw(self.screen)
            decline_button.draw(self.screen)

            pygame.display.flip()

        return True

class InstructionScreen:
    """Display instructions between stages"""

    def __init__(self, screen):
        self.screen = screen

    def show(self, instruction_type):
        """
        Show instructions

        Args:
            instruction_type: 'training', 'main_start', 'green_jar', 'red_jar_return'
        """
        if instruction_type == 'training':
            title = "Training Phase"
            instructions = [
                "You will see samples of balls drawn from an urn.",
                "Two candidate urns will be shown.",
                "Your task is to identify which urn the sample came from.",
                "",
                "This training will help you understand the relationship",
                "between samples and the urns they come from.",
                "",
                "Press SPACE to continue"
            ]
        elif instruction_type == 'main_start':
            title = "Main Experiment - RED JAR"
            instructions = [
                "Now the main experiment begins.",
                "A jar (urn) has been randomly selected from all possible jars.",
                "You won't see what's inside.",
                "",
                "You will:",
                "  1. Provide an initial probability estimate",
                "  2. Draw balls one at a time (press SPACEBAR)",
                "  3. After each draw, estimate the probability of drawing a black ball",
                "  4. Rate your confidence in your estimate (0-10)",
                "",
                "All previously drawn balls will remain visible.",
                "",
                "Press SPACE to continue"
            ]
        elif instruction_type == 'green_jar':
            title = "New Task - GREEN JAR"
            instructions = [
                "The RED jar is being set aside.",
                "A NEW jar (GREEN jar) with a different unknown probability",
                "has been selected.",
                "",
                "Begin the same estimation process with this new jar.",
                "",
                "Press SPACE to continue"
            ]
        elif instruction_type == 'red_jar_return':
            title = "Return to RED JAR"
            instructions = [
                "The GREEN jar is being set aside.",
                "We are now returning to the original RED jar.",
                "",
                "Continue your estimation process where you left off.",
                "All your previous samples from the RED jar are still here.",
                "",
                "Press SPACE to continue"
            ]
        else:
            title = "Instructions"
            instructions = ["Press SPACE to continue"]

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

            self.screen.fill(WHITE)

            # Title
            title_surface = TITLE_FONT.render(title, True, BLUE)
            self.screen.blit(title_surface,
                           (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 100))

            # Instructions
            y = 200
            for line in instructions:
                if line.startswith("  "):  # Indented line
                    text_surface = SMALL_FONT.render(line, True, DARK_GRAY)
                else:
                    text_surface = MEDIUM_FONT.render(line, True, BLACK)
                self.screen.blit(text_surface,
                               (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, y))
                y += 40

            pygame.display.flip()

class Experiment:
    """Main experiment controller"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bayesian Belief Updating Experiment")
        self.audio = AudioManager()
        self.clock = pygame.time.Clock()

        # Get participant ID
        self.participant_id = self._get_participant_id()
        self.data_collector = DataCollector(self.participant_id)

        self.instruction_screen = InstructionScreen(self.screen)

    def _get_participant_id(self):
        """Get participant ID from user"""
        participant_id = ""
        getting_id = True

        input_box = InputBox(SCREEN_WIDTH // 2 - 150, 400, 300, 50,
                            "Participant ID:", 0, 99999)
        submit_button = Button(SCREEN_WIDTH // 2 - 75, 500, 150, 50, "Start")

        while getting_id:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                input_box.handle_event(event)

                if submit_button.handle_event(event):
                    if input_box.text:
                        participant_id = input_box.text
                        getting_id = False

            self.screen.fill(WHITE)

            title = TITLE_FONT.render("Bayesian Belief Updating Study", True, BLACK)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

            inst = MEDIUM_FONT.render("Please enter your Participant ID:", True, BLACK)
            self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 300))

            input_box.draw(self.screen)
            submit_button.draw(self.screen)

            pygame.display.flip()

        return participant_id

    def run(self):
        """Run the complete experiment"""
        # Consent
        consent_screen = ConsentScreen(self.screen)
        if not consent_screen.run():
            print("Participant declined consent")
            return

        # Training phase
        self.instruction_screen.show('training')
        self._run_training()

        # Main experiment
        self.instruction_screen.show('main_start')

        # Stage 1: Red Jar (40 trials)
        red_stage1 = MainExperimentStage(self.screen, self.audio, 'red', 40)
        red_data = red_stage1.run()
        self.data_collector.add_stage_data('red_jar_stage1', red_data)

        # Stage 2: Green Jar (30 trials)
        self.instruction_screen.show('green_jar')
        green_stage = MainExperimentStage(self.screen, self.audio, 'green', 30)
        green_data = green_stage.run()
        self.data_collector.add_stage_data('green_jar_stage2', green_data)

        # Stage 3: Return to Red Jar (30 trials)
        self.instruction_screen.show('red_jar_return')
        red_stage3 = MainExperimentStage(self.screen, self.audio, 'red', 30,
                                        jar_probability=red_data['true_probability'],
                                        previous_data=red_data)
        red_data_continued = red_stage3.run()
        self.data_collector.add_stage_data('red_jar_stage3', red_data_continued)

        # Export data
        self.data_collector.export()

        # Thank you screen
        self._show_thank_you()

    def _run_training(self):
        """Run the training phase"""
        num_training_trials = 10

        for trial_num in range(1, num_training_trials + 1):
            trial = TrainingTrial(self.screen, self.audio)
            result = trial.run()
            self.data_collector.add_training_trial(trial_num, result)

    def _show_thank_you(self):
        """Show thank you message"""
        waiting = True
        start_time = pygame.time.get_ticks()

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False

                if event.type == pygame.KEYDOWN:
                    waiting = False

            # Auto-close after 5 seconds
            if pygame.time.get_ticks() - start_time > 5000:
                waiting = False

            self.screen.fill(WHITE)

            thanks = TITLE_FONT.render("Thank You!", True, GREEN)
            self.screen.blit(thanks, (SCREEN_WIDTH // 2 - thanks.get_width() // 2, 300))

            message = MEDIUM_FONT.render("The experiment is complete.", True, BLACK)
            self.screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 400))

            message2 = SMALL_FONT.render("Your data has been saved.", True, DARK_GRAY)
            self.screen.blit(message2, (SCREEN_WIDTH // 2 - message2.get_width() // 2, 450))

            pygame.display.flip()

def main():
    """Main entry point"""
    experiment = Experiment()
    experiment.run()
    pygame.quit()

if __name__ == "__main__":
    main()
