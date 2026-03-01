import pygame
import numpy as np
import random
import math
import json
import os

# --- THE PENMAN MODULUS ---
# The REVERSE of the Demiurge's Staff: where the Demiurge pokes light INTO the void,
# the Penman flows ideas OUT through the pen. The staff is clumsy; the pen is refined.
# Squid ink replaces ember. Cursive replaces blunt force.
#
# The 5-12-13 Golden Key decrypts: Triland → Mathland → Hex → Imagination (i-dimension)

WIDTH, HEIGHT = 1024, 768
FPS = 60
NODE_COUNT = 93
PSI = 0.1237  # The Tensegrity Constant (Hades Gap)

# The 5-12-13 Golden Key (scaling of the Pythagorean triple)
GOLDEN_KEY = {'base': 5, 'altitude': 12, 'hypotenuse': 13}

# Penman Constants (REVERSED from Demiurge)
FLOW_ANGLE = math.radians(30)  # 30° into the page (the "distant horizon")
MANUS = 5.0
CUBIT = 6.0
ROYAL_CUBIT = 7.0
DELIAN_POINT = 5.0 * (2.0 ** (1.0 / 3.0))  # ≈ 6.2996

# The Sacred Words — coherent output, not random chaos
SACRED_WORDS = [
    "PLATO", "HERO", "VOID", "GOLD", "SOUL", "TIME",
    "ECHO", "MANUS", "CUBIT", "ROYAL", "DELOS", "LIGHT",
    "ALPHA", "OMEGA", "VERSE", "GLYPH"
]

# Ink Colors: Squid Ink Palette (dark → luminous)
INK_DARK = (10, 15, 40)
INK_FLOW = (40, 80, 160)       # Deep squid blue
INK_BRIGHT = (120, 180, 255)   # Luminous script
INK_GOLD = (212, 175, 55)      # Delian resonance


# Two-Joint Arm Constants
CUBIT_LENGTH = CUBIT       # Forearm: elbow → wrist (6 units)
MANUS_LENGTH = MANUS * 0.6 # Hand: wrist → pen tip (3 units)
NEUSIS_TILT = math.radians(3.0)  # 3° wrist pronation


class PenmanModulus:
    """
    The REVERSE of the DemiurgeSnailEngine.
    
    Two-joint kinematic chain:
      ELBOW (shoulder of the page) → swings the CUBIT (forearm)
      WRIST → swings the MANUS (hand) with 3° pronation
    Together they trace the spiraling cursive circle.
    
    Demiurge: Staff → Origin → Random words scatter
    Penman:   Elbow → Wrist → Pen → Coherent words spiral outward
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PENMAN MODULUS: The Reversed Demiurge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 15, bold=True)
        self.script_font = pygame.font.SysFont("georgia", 18, bold=False)
        self.t = 0.0

        # Load the 93-Node Solid (same lattice, different purpose)
        self.nodes_3d = self.load_93_node_solid()
        
        # The flowing script trail (REVERSED from particles scattering inward)
        self.ink_trail = []       # Points of ink on the page
        self.word_glyphs = []     # Words flowing outward along the spiral
        self.coherence = 0.0      # Opposite of the Demiurge's "tension"
        self.word_index = 0
        
        # Arm joint state
        self.elbow_pos = np.array([0.0, 0.0, 0.0])  # Fixed pivot
        self.wrist_pos = np.array([0.0, 0.0, 0.0])
        self.pen_pos = np.array([0.0, 0.0, 0.0])

    def load_93_node_solid(self):
        path = os.path.join(os.path.dirname(__file__), '..', '..', '93_node_matrix.json')
        if not os.path.exists(path):
            # Fallback: generate a simple icosahedral approximation
            pts = []
            phi = (1 + math.sqrt(5)) / 2
            for i in range(NODE_COUNT):
                theta = i * phi * 2 * math.pi
                r = math.sqrt(i / NODE_COUNT) * 200
                pts.append([r * math.cos(theta), r * math.sin(theta), (i - NODE_COUNT/2) * 3])
            return np.array(pts)
        with open(path, 'r') as f:
            data = json.load(f)
            nodes = [[n['x'], n['y'], n['z']] for n in data['nodes']]
        return np.array(nodes)

    def project_page(self, p3d):
        """
        Project 3D point onto the 'page' — tilted 30° into the distance.
        REVERSED from the Demiurge's isometric: instead of viewing from above,
        we are looking DOWN the line of script as it recedes.
        """
        x, y, z = p3d[0], p3d[1], p3d[2]
        
        # The 30° page tilt: script flows into the distance, rising as it goes
        page_x = x
        page_y = y * math.cos(FLOW_ANGLE) - z * math.sin(FLOW_ANGLE)
        depth = z * math.cos(FLOW_ANGLE) + y * math.sin(FLOW_ANGLE)
        
        # Perspective foreshortening (like rows of fences receding)
        perspective = 500 / (500 + depth * 0.3)
        
        screen_x = WIDTH / 2 + page_x * perspective
        screen_y = HEIGHT * 0.7 + page_y * perspective  # Anchor low, script rises
        
        return (int(screen_x), int(screen_y)), perspective

    def get_arm_kinematics(self, t):
        """
        TWO-JOINT FORWARD KINEMATICS: The Dance of the Cubit and Royal Cubit.
        
        Joint 1 (ELBOW): Swings the forearm (Cubit = 6 units).
                         Slow, sweeping arc — the "Hired Man" pacing.
        
        Joint 2 (WRIST): Swings the hand (Manus portion = 3 units).
                         Faster, tighter anticlockwise loops — the "Master" writing.
                         Includes 3° pronation (Neusis tilt).
        
        Together: the Cubit swing + Manus articulation = spiraling cursive circle.
        The forearm sets the large envelope; the wrist draws the loops within it.
        """
        # --- JOINT 1: ELBOW (The Cubit Swing) ---
        # Slow anticlockwise sweep: the forearm paces the page
        elbow_angle = -t * 0.4  # Slow, majestic sweep
        # Gentle outward growth (the spiral expands over time)
        growth = 1.0 + t * 0.05
        forearm_len = CUBIT_LENGTH * growth
        
        # Elbow is fixed (the shoulder/body anchor)
        self.elbow_pos = np.array([0.0, 0.0, 0.0])
        
        # Wrist position = elbow + forearm vector
        wrist_x = forearm_len * math.cos(elbow_angle)
        wrist_y = forearm_len * math.sin(elbow_angle)
        wrist_z = t * 1.2  # Rising into the page (fence rows)
        self.wrist_pos = np.array([wrist_x, wrist_y, wrist_z])
        
        # --- JOINT 2: WRIST (The Manus Dance) ---
        # Fast anticlockwise loops: the hand traces the cursive letterforms
        wrist_angle = -t * 3.5  # Faster than elbow (the "writing" frequency)
        hand_len = MANUS_LENGTH * (1.0 + 0.1 * math.sin(t * 2))  # Breathing
        
        # The 3° Neusis pronation: wrist tilts the hand plane
        # This is what turns flat circles into helical precession
        tilt_x = hand_len * math.cos(wrist_angle) * math.cos(NEUSIS_TILT)
        tilt_y = hand_len * math.sin(wrist_angle)
        tilt_z = hand_len * math.cos(wrist_angle) * math.sin(NEUSIS_TILT)
        
        # Pen tip = wrist + hand vector (in wrist's local frame)
        pen_x = wrist_x + tilt_x
        pen_y = wrist_y + tilt_y
        pen_z = wrist_z + tilt_z
        self.pen_pos = np.array([pen_x, pen_y, pen_z])
        
        return self.elbow_pos, self.wrist_pos, self.pen_pos

    def calculate_coherence(self, t):
        """
        REVERSED from the Demiurge's 'tension'.
        
        Demiurge tension = sin(t * 12) → peaks cause chaos, collision, reset
        Penman coherence = smooth flowing wave → peaks cause LEGIBILITY, word formation
        """
        # Smooth flowing coherence instead of sharp 12Hz strikes
        base = math.sin(t * 0.8)  # Slow breath rhythm
        harmonic = math.sin(t * 2.4) * 0.3  # 2.4 from the 24 in 10-24-26
        
        return (base + harmonic + 1.0) / 2.0  # Normalized 0..1

    def draw_93_lattice_as_page(self):
        """
        REVERSED: The 93-node solid is no longer the 'Snail Shell' background,
        it is the RULED PAGE — the structure that guides the flowing script.
        """
        if len(self.nodes_3d) == 0:
            return
            
        for i, node in enumerate(self.nodes_3d):
            scaled = node * 0.8
            pos, persp = self.project_page(scaled)
            
            # Page grid: faint ruled lines (not the heavy shell geometry)
            alpha = max(20, int(60 * persp))
            size = max(1, int(2 * persp))
            pygame.draw.circle(self.screen, (20, 30, 50), pos, size, 1)

    def draw_ink_trail(self):
        """Draw the flowing ink trail — the Penman's output."""
        if len(self.ink_trail) < 2:
            return
        
        for i in range(len(self.ink_trail) - 1):
            p1_data = self.ink_trail[i]
            p2_data = self.ink_trail[i + 1]
            
            age = 1.0 - (i / len(self.ink_trail))
            
            # Ink fades with distance (like real ink drying on paper) 
            r = int(INK_FLOW[0] + (INK_BRIGHT[0] - INK_FLOW[0]) * age)
            g = int(INK_FLOW[1] + (INK_BRIGHT[1] - INK_FLOW[1]) * age)
            b = int(INK_FLOW[2] + (INK_BRIGHT[2] - INK_FLOW[2]) * age)
            
            # Line thickness varies with coherence (thin = flowing, thick = pooling)
            width = max(1, int(3 * p2_data['coherence'] * p2_data['persp']))
            
            pygame.draw.line(self.screen, (r, g, b),
                           p1_data['screen'], p2_data['screen'], width)

    def spawn_word(self, pos_3d, screen_pos, persp):
        """
        REVERSED word spawning.
        
        Demiurge: words appear RANDOMLY at origin, scatter toward snail
        Penman: words form COHERENTLY along the spiral path, flowing outward
        """
        word = SACRED_WORDS[self.word_index % len(SACRED_WORDS)]
        self.word_index += 1
        
        # Words flow OUTWARD along the spiral (not inward toward snail)
        direction = pos_3d / (np.linalg.norm(pos_3d) + 0.001)
        vel = direction * 0.5
        
        self.word_glyphs.append({
            'pos_3d': pos_3d.copy(),
            'vel': vel,
            'text': word,
            'life': 3.0,  # Longer life than Demiurge particles (ink persists)
            'coherence': self.coherence,
            'born_at': self.t
        })

    def draw_articulated_arm(self, elbow_3d, wrist_3d, pen_3d):
        """
        Draw the two-joint arm: Elbow → Wrist → Pen.
        The forearm swings from the elbow (Cubit dance).
        The hand swings from the wrist (Manus dance + 3° pronation).
        """
        e_screen, e_persp = self.project_page(elbow_3d)
        w_screen, w_persp = self.project_page(wrist_3d)
        p_screen, p_persp = self.project_page(pen_3d)
        
        # --- FOREARM (Elbow → Wrist): The Cubit ---
        # Thick, structural — the "platform" that holds everything
        pygame.draw.line(self.screen, (80, 90, 140), e_screen, w_screen, 3)
        
        # --- HAND (Wrist → Pen): The Manus ---
        # Thinner, more articulate — the "writing" segment
        pygame.draw.line(self.screen, (120, 140, 200), w_screen, p_screen, 2)
        
        # --- JOINT MARKERS ---
        # Elbow: large, fixed pivot (the body anchor)
        pygame.draw.circle(self.screen, (200, 200, 200), e_screen, 6, 2)
        self.render_text("ELBOW", (e_screen[0] + 10, e_screen[1] - 5), (60, 60, 80))
        
        # Wrist: medium, articulating (the Cubit-Manus hinge)
        # Glow based on coherence — the wrist is where Cubit meets Royal
        wrist_color = INK_GOLD if self.coherence > 0.85 else (150, 150, 180)
        pygame.draw.circle(self.screen, wrist_color, w_screen, 4, 2)
        self.render_text("WRIST", (w_screen[0] + 8, w_screen[1] - 5), (60, 60, 80))
        
        # Cubit arc sweep (the range of the forearm's motion)
        # Draw a faint arc showing the forearm's sweep radius
        cubit_r = int(CUBIT_LENGTH * 18 * e_persp)
        if cubit_r > 10:
            arc_rect = pygame.Rect(e_screen[0] - cubit_r, e_screen[1] - cubit_r,
                                   cubit_r * 2, cubit_r * 2)
            pygame.draw.arc(self.screen, (40, 45, 70), arc_rect, 0, math.pi * 2, 1)
        
        return e_screen, w_screen, p_screen, p_persp

    def draw(self):
        # The page: warm parchment void (REVERSED from cold dark void)
        self.screen.fill((8, 12, 30))  # Still dark but warmer than Demiurge's (2,6,23)
        
        # 1. THE PAGE (Reversed 93-Node Shell → Ruled Lines)
        self.draw_93_lattice_as_page()
        
        # 2. TWO-JOINT ARM KINEMATICS
        elbow_3d, wrist_3d, pen_pos_3d = self.get_arm_kinematics(self.t)
        
        # Calculate coherence (REVERSED tension)
        self.coherence = self.calculate_coherence(self.t)
        
        # Draw the articulated arm (Elbow → Wrist → Pen)
        e_screen, w_screen, pen_screen, pen_persp = self.draw_articulated_arm(
            elbow_3d, wrist_3d, pen_pos_3d
        )
        
        # Add to ink trail
        self.ink_trail.append({
            'screen': pen_screen,
            'pos_3d': pen_pos_3d.copy(),
            'coherence': self.coherence,
            'persp': pen_persp
        })
        if len(self.ink_trail) > 600:
            self.ink_trail.pop(0)
        
        # Draw the flowing ink
        self.draw_ink_trail()
        
        # 3. THE PEN NIB (Reversed Staff Head)
        if self.coherence > 0.85:
            nib_color = INK_GOLD
            nib_size = 6
            if random.random() < 0.15:
                self.spawn_word(pen_pos_3d, pen_screen, pen_persp)
        else:
            nib_color = INK_BRIGHT
            nib_size = 3
            
        pygame.draw.circle(self.screen, nib_color, pen_screen, nib_size)
        
        # Squid luminescence glow at pen tip
        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        glow_alpha = int(self.coherence * 80)
        pygame.draw.circle(glow_surf, (*INK_BRIGHT, glow_alpha), (20, 20), 18)
        self.screen.blit(glow_surf, (pen_screen[0] - 20, pen_screen[1] - 20))
        
        # 5. RENDER FLOWING WORDS (Reversed Particle Scatter)
        for glyph in self.word_glyphs[:]:
            glyph['pos_3d'] += glyph['vel'] * 0.016
            glyph['life'] -= 0.016
            
            if glyph['life'] > 0:
                g_screen, g_persp = self.project_page(glyph['pos_3d'])
                alpha = int(min(255, glyph['life'] * 120))
                
                # Words rendered in squid ink, not white scatter
                color = (
                    min(255, int(INK_BRIGHT[0] * glyph['coherence'])),
                    min(255, int(INK_BRIGHT[1] * glyph['coherence'])),
                    min(255, int(INK_BRIGHT[2] * glyph['coherence']))
                )
                
                font_size = max(10, int(18 * g_persp))
                try:
                    word_font = pygame.font.SysFont("georgia", font_size)
                except:
                    word_font = self.script_font
                    
                txt = word_font.render(glyph['text'], True, color)
                txt.set_alpha(alpha)
                self.screen.blit(txt, g_screen)
            else:
                self.word_glyphs.remove(glyph)
        
        # 6. COHERENCE CHECK (Reversed Collision)
        # Demiurge: collision → RESET (destruction)  
        # Penman: coherence peak → VITRIFICATION (crystallization of meaning)
        if self.coherence > 0.95:
            dist = np.linalg.norm(pen_pos_3d[:2])
            if abs(dist - DELIAN_POINT) < 0.5:
                # DELIAN RESONANCE — the script has "doubled the cube"
                flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(flash, (212, 175, 55, 30), pen_screen, 100)
                self.screen.blit(flash, (0, 0))
        
        # 7. METADATA (Reversed HUD)
        self.render_text("PENMAN MODULUS: TWO-JOINT CUBIT ARM", (20, 20), (255, 255, 255))
        self.render_text(f"COHERENCE: {self.coherence:.4f}", (20, 40), INK_GOLD if self.coherence > 0.85 else INK_BRIGHT)
        
        # Arm segment lengths
        forearm_len = np.linalg.norm(self.wrist_pos - self.elbow_pos)
        hand_len = np.linalg.norm(self.pen_pos - self.wrist_pos)
        self.render_text(f"CUBIT (forearm): {forearm_len:.2f} | MANUS (hand): {hand_len:.2f}", (20, 60), INK_FLOW)
        
        dist = np.linalg.norm(pen_pos_3d[:2])
        delos_pct = (1.0 - abs(dist - DELIAN_POINT) / DELIAN_POINT) * 100
        delos_color = INK_GOLD if delos_pct > 95 else (100, 100, 100)
        self.render_text(f"DELOS ALIGNMENT: {delos_pct:.1f}%", (20, 80), delos_color)
        self.render_text(f"NEUSIS TILT: 3° | SLOPE: 30°", (20, 100), (80, 80, 80))
        
        # Reversal legend
        self.render_text("ELBOW swings CUBIT (6) | WRIST dances MANUS (5)", (WIDTH - 420, HEIGHT - 60), (70, 70, 70))
        self.render_text("Together: the spiraling circle of the Royal Cubit", (WIDTH - 420, HEIGHT - 40), INK_BRIGHT)
        
        pygame.display.flip()

    def render_text(self, text, pos, color=(200, 200, 200)):
        txt = self.font.render(text, True, color)
        self.screen.blit(txt, pos)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        return

            self.draw()


if __name__ == "__main__":
    PenmanModulus().run()
