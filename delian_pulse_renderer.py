import pygame
import numpy as np
import math
import struct
import array

# --- DELIAN PULSE RENDERER ---
# The visual/audio feedback engine for the Penman Modulus.
# Implements: Golden Spiral, Cube Doubling, Cubit Arc Glow, Manus Halo, 432Hz Chime.
#
# This module completes the mytho-technical loop:
# Divine Geometry → Human Gesture → Biological Embodiment → Real-Time Rendering

WIDTH, HEIGHT = 1024, 768
FPS = 60

# Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden Ratio ≈ 1.618
DELOS_CONSTANT = 5.0 * (2.0 ** (1.0 / 3.0))  # ≈ 6.2996
MANUS = 5.0
CUBIT = 6.0
ROYAL = 7.0

# Audio
SAMPLE_RATE = 44100
CHIME_FREQ = 432       # Hz — The "Mastered 6" resonance
CHIME_DURATION = 0.8   # seconds
CHIME_AMPLITUDE = 0.4


def generate_432hz_chime():
    """
    Generates a 432Hz chime with exponential fade.
    Returns a pygame.mixer.Sound object.
    """
    n_samples = int(SAMPLE_RATE * CHIME_DURATION)
    samples = array.array('h')  # signed short integers
    
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # Exponential fade: loud start, smooth decay
        envelope = math.exp(-t * 4.0)
        # Base tone + harmonic (octave shimmer)
        wave = (math.sin(2 * math.pi * CHIME_FREQ * t) * 0.7 +
                math.sin(2 * math.pi * CHIME_FREQ * 2 * t) * 0.2 +
                math.sin(2 * math.pi * CHIME_FREQ * 3 * t) * 0.1)
        sample = int(wave * envelope * CHIME_AMPLITUDE * 32767)
        sample = max(-32767, min(32767, sample))
        samples.append(sample)
    
    # Convert to bytes for pygame
    buf = struct.pack(f'{len(samples)}h', *samples)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


# Nautilus 93 layout: 60 edges + 20 faces + 10 vertices = 90 peripheral
NAUTILUS_TENTACLE_GROUPS = {
    'edges': 60,     # Short rays
    'faces': 20,     # Medium rays
    'vertices': 10,  # Long rays
}
NAUTILUS_HEARTS = 3  # Central pulses
RADULA_GATE = 13     # Modulo for grinding rhythm


class DelianPulseRenderer:
    """
    The visual/audio feedback engine.
    
    When the Penman's anticlockwise loop hits the Delos Resonance Cylinder
    (R ≈ 6.299), this renderer triggers:
    
    1. Golden Spiral Overlay (φ-spiral from elbow pivot)
    2. Cube Doubling Animation (125 → 250, counter-rotating)
    3. Cubit Arc Glow (sin(loop_count × π/13) modulation)
    4. Manus Illumination (hexagonal "Mastered 6" halo)
    5. Audio Cue (432Hz chime, 800ms, exponential fade)
    6. 93-Node Nautilus Halo (90 tentacle rays + 3 heart pulses)
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 14, bold=True)
        
        # Pulse state
        self.pulse_active = False
        self.pulse_timer = 0.0
        self.pulse_intensity = 0.0
        self.loop_count = 0
        self.total_pulses = 0
        
        # Audio
        try:
            pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
            self.chime = generate_432hz_chime()
            self.audio_available = True
        except Exception:
            self.audio_available = False
            self.chime = None
        
        # Cube rotation state
        self.cube_angle = 0.0
    
    def check_resonance(self, pen_pos_3d, slope_deg=30.0, neusis_deg=3.0):
        """
        Checks if the Penman has hit the Delos Resonance Cylinder.
        Returns True if vitrification condition is met.
        """
        radial_dist = math.sqrt(pen_pos_3d[0]**2 + pen_pos_3d[1]**2)
        radial_tolerance = 0.5
        
        is_aligned = abs(radial_dist - DELOS_CONSTANT) < radial_tolerance
        
        if is_aligned and not self.pulse_active:
            self.trigger_pulse()
        
        return is_aligned, radial_dist
    
    def trigger_pulse(self):
        """Fires the Delian Pulse — all visual and audio layers."""
        self.pulse_active = True
        self.pulse_timer = 1.5  # seconds of visual effect
        self.pulse_intensity = 1.0
        self.loop_count += 1
        self.total_pulses += 1
        
        if self.audio_available and self.chime:
            self.chime.play()
    
    def update(self, dt):
        """Advance pulse state."""
        if self.pulse_active:
            self.pulse_timer -= dt
            self.pulse_intensity = max(0, self.pulse_timer / 1.5)
            self.cube_angle += dt * 90  # degrees per second
            
            if self.pulse_timer <= 0:
                self.pulse_active = False
                self.pulse_intensity = 0.0
    
    # --- VISUAL LAYERS ---
    
    def draw_golden_spiral(self, center, t):
        """
        Layer 1: Golden Spiral Overlay (φ-spiral from elbow pivot).
        The Nautilus shell geometry rendered in golden light.
        """
        if self.pulse_intensity <= 0:
            return
        
        pts = []
        for i in range(200):
            angle = i * 0.15
            r = 3.0 * (PHI ** (angle / (2 * math.pi)))
            
            # Rotate slowly
            rot = angle + t * 0.5
            x = center[0] + r * math.cos(rot)
            y = center[1] + r * math.sin(rot)
            
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                pts.append((int(x), int(y)))
        
        if len(pts) > 2:
            alpha = int(self.pulse_intensity * 180)
            color = (212, 175, 55)  # Gold
            
            for i in range(len(pts) - 1):
                # Fade alpha along the spiral
                seg_alpha = max(30, int(alpha * (1 - i / len(pts))))
                r = min(255, color[0])
                g = min(255, color[1])
                b = min(255, color[2])
                pygame.draw.line(self.screen, (r, g, b), pts[i], pts[i + 1], 2)
    
    def draw_cube_doubling(self, center, t):
        """
        Layer 2: Cube Doubling Animation.
        Original cube (side=5, vol=125) + Doubled cube (side≈6.3, vol=250).
        Counter-rotating in 3D.
        """
        if self.pulse_intensity <= 0:
            return
        
        angle1 = math.radians(self.cube_angle)
        angle2 = -angle1  # Counter-rotation
        
        # Original cube (Manus = 5)
        self._draw_wireframe_cube(center, MANUS * 8, angle1,
                                   (78, 205, 196), self.pulse_intensity)
        
        # Doubled cube (Delian ≈ 6.3)
        self._draw_wireframe_cube(center, DELOS_CONSTANT * 8, angle2,
                                   (212, 175, 55), self.pulse_intensity * 0.7)
    
    def _draw_wireframe_cube(self, center, size, angle, color, intensity):
        """Draws a rotating wireframe cube."""
        half = size / 2
        # 8 vertices of a cube
        verts_3d = [
            [-half, -half, -half], [half, -half, -half],
            [half, half, -half], [-half, half, -half],
            [-half, -half, half], [half, -half, half],
            [half, half, half], [-half, half, half]
        ]
        
        # Rotate around Y axis
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        rotated = []
        for v in verts_3d:
            rx = v[0] * cos_a - v[2] * sin_a
            rz = v[0] * sin_a + v[2] * cos_a
            ry = v[1]
            # Simple perspective
            persp = 300 / (300 + rz * 0.3)
            sx = center[0] + rx * persp
            sy = center[1] + ry * persp
            rotated.append((int(sx), int(sy)))
        
        # 12 edges of a cube
        edges = [
            (0,1),(1,2),(2,3),(3,0),  # front
            (4,5),(5,6),(6,7),(7,4),  # back
            (0,4),(1,5),(2,6),(3,7)   # connects
        ]
        
        alpha_color = (
            min(255, int(color[0] * intensity)),
            min(255, int(color[1] * intensity)),
            min(255, int(color[2] * intensity))
        )
        
        for e in edges:
            pygame.draw.line(self.screen, alpha_color,
                           rotated[e[0]], rotated[e[1]], 1)
    
    def draw_cubit_arc_glow(self, center, t):
        """
        Layer 3: Cubit Arc Glow modulated by sin(loop_count × π/13).
        The 13-tooth radula rhythm.
        """
        # Modulation: the 13-node compass grinding
        mod = abs(math.sin(self.loop_count * math.pi / 13))
        
        for radius, label, base_color in [
            (MANUS * 20, "5", (50, 70, 90)),
            (CUBIT * 20, "6", (70, 90, 110)),
            (DELOS_CONSTANT * 20, "∛2", (212, 175, 55)),
            (ROYAL * 20, "7", (90, 110, 130)),
        ]:
            # Glow intensity
            glow = 0.3 + 0.7 * mod * self.pulse_intensity
            color = (
                min(255, int(base_color[0] + 100 * glow)),
                min(255, int(base_color[1] + 100 * glow)),
                min(255, int(base_color[2] + 100 * glow)),
            )
            
            # Draw arc ring
            pts = []
            for a in np.linspace(0, 2 * math.pi, 64):
                x = center[0] + radius * math.cos(a + t * 0.1)
                y = center[1] + radius * math.sin(a + t * 0.1) * 0.6  # Perspective squash
                pts.append((int(x), int(y)))
            
            if len(pts) > 2:
                pygame.draw.aalines(self.screen, color, True, pts)
    
    def draw_manus_halo(self, pen_pos, t):
        """
        Layer 4: Manus Illumination — hexagonal "Mastered 6" halo.
        The six-sided glow of the achieved Cubit state.
        """
        if self.pulse_intensity <= 0.1:
            return
        
        # Hexagonal halo (6 sides = the Mastered 6)
        hex_radius = 25 + 10 * math.sin(t * 3)
        pts = []
        for i in range(7):  # 7 points to close the hexagon
            angle = i * (2 * math.pi / 6) + t * 0.5
            x = pen_pos[0] + hex_radius * math.cos(angle)
            y = pen_pos[1] + hex_radius * math.sin(angle)
            pts.append((int(x), int(y)))
        
        alpha = int(self.pulse_intensity * 200)
        # Inner glow
        glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (212, 175, 55, int(alpha * 0.3)), (40, 40), 35)
        self.screen.blit(glow_surf, (pen_pos[0] - 40, pen_pos[1] - 40))
        
        # Hexagon outline
        color = (
            min(255, int(212 * self.pulse_intensity)),
            min(255, int(175 * self.pulse_intensity)),
            min(255, int(55 * self.pulse_intensity))
        )
        pygame.draw.lines(self.screen, color, True, pts, 2)
    
    def draw_93_halo(self, pen_pos, t):
        """
        Layer 6: The 93-Node Nautilus Halo.
        
        90 peripheral 'tentacle' rays radiating from the pen tip:
          - 60 short (Edge nodes) — closest sensing
          - 20 medium (Face nodes) — mid-range
          - 10 long (Vertex nodes) — far reach
        
        3 central 'heart' pulses throbbing at the pen tip.
        
        The radula gate (mod 13) controls tentacle undulation speed.
        """
        if self.pulse_intensity <= 0.05:
            return
        
        # Radula grinding rhythm — mod 13
        grind = math.sin(t * RADULA_GATE) * 0.5 + 0.5
        
        # --- 90 TENTACLE RAYS ---
        total_tentacles = 90
        ray_index = 0
        
        for group_name, count in NAUTILUS_TENTACLE_GROUPS.items():
            # Ray length by group
            if group_name == 'edges':
                base_len = 15  # Short
                color = (30, 60, 90)
            elif group_name == 'faces':
                base_len = 30  # Medium
                color = (50, 100, 140)
            else:  # vertices
                base_len = 50  # Long reach
                color = (80, 150, 200)
            
            for i in range(count):
                # Distribute evenly around the circle
                angle = (ray_index / total_tentacles) * 2 * math.pi
                # Undulation: each tentacle waves independently
                wave = math.sin(t * 2.5 + ray_index * 0.7) * 0.3
                ray_len = base_len * (1.0 + wave) * self.pulse_intensity * grind
                
                # Slight rotation over time (the sensing sweep)
                rot_angle = angle + t * 0.3
                
                tip_x = pen_pos[0] + ray_len * math.cos(rot_angle)
                tip_y = pen_pos[1] + ray_len * math.sin(rot_angle)
                
                # Color intensity by pulse
                c = (
                    min(255, int(color[0] + 80 * self.pulse_intensity)),
                    min(255, int(color[1] + 80 * self.pulse_intensity)),
                    min(255, int(color[2] + 80 * self.pulse_intensity)),
                )
                
                pygame.draw.line(self.screen, c, pen_pos,
                               (int(tip_x), int(tip_y)), 1)
                ray_index += 1
        
        # --- 3 HEART PULSES ---
        # Three concentric throbs at the pen tip (Systemic + 2 Branchial)
        heart_colors = [
            (220, 50, 50),    # Systemic (Apollo) — red
            (50, 50, 220),    # Branchial L (Hades) — blue
            (50, 220, 50),    # Branchial R (Hero) — green
        ]
        
        for h in range(NAUTILUS_HEARTS):
            # Each heart beats at a slightly different phase
            beat = abs(math.sin(t * 3.0 + h * (2 * math.pi / 3)))
            radius = int(4 + 8 * beat * self.pulse_intensity)
            
            # Offset slightly from center (triangular arrangement)
            offset_angle = h * (2 * math.pi / 3) + t * 0.5
            ox = int(pen_pos[0] + 6 * math.cos(offset_angle))
            oy = int(pen_pos[1] + 6 * math.sin(offset_angle))
            
            c = (
                min(255, int(heart_colors[h][0] * self.pulse_intensity)),
                min(255, int(heart_colors[h][1] * self.pulse_intensity)),
                min(255, int(heart_colors[h][2] * self.pulse_intensity)),
            )
            
            pygame.draw.circle(self.screen, c, (ox, oy), radius, 1)
    
    def draw_all(self, center, pen_pos, t):
        """Render all 6 pulse layers."""
        # Always draw the arcs (dim when no pulse)
        self.draw_cubit_arc_glow(center, t)
        
        if self.pulse_active or self.pulse_intensity > 0:
            self.draw_golden_spiral(center, t)
            self.draw_cube_doubling(center, t)
            self.draw_manus_halo(pen_pos, t)
            self.draw_93_halo(pen_pos, t)
    
    def draw_status(self, y_offset=100):
        """Render pulse status text."""
        status = "VITRIFIED" if self.pulse_active else "SCANNING"
        color = (212, 175, 55) if self.pulse_active else (80, 80, 80)
        
        self.screen.blit(
            self.font.render(f"DELIAN PULSE: {status}", True, color),
            (20, y_offset)
        )
        self.screen.blit(
            self.font.render(f"RESONANCE COUNT: {self.total_pulses} | RADULA MOD: sin({self.loop_count}π/13)", True, (100, 100, 100)),
            (20, y_offset + 20)
        )


# --- STANDALONE DEMO ---

class DelianPulseDemo:
    """
    Standalone demonstration of the Delian Pulse Renderer.
    A pen traces an expanding anticlockwise spiral. When it crosses
    the Delos Resonance Cylinder (R≈6.299), the pulse fires.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DELIAN PULSE RENDERER: 93-Node Vitrification")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 15, bold=True)
        
        self.renderer = DelianPulseRenderer(self.screen)
        self.t = 0.0
        self.trail = []
    
    def get_pen_pos(self, t):
        """Anticlockwise spiral that crosses the Delos boundary."""
        growth = 1.0 + t * 0.08
        theta = -t * 1.5  # Anticlockwise
        r = MANUS * growth
        
        x = r * math.cos(theta) + 1.5 * math.cos(theta * 3)
        y = r * math.sin(theta) + 1.5 * math.sin(theta * 3)
        z = t * 3.0  # Rising into the page at 30°
        
        return np.array([x, y, z])
    
    def project(self, p3d):
        """30° page-tilt projection."""
        flow = math.radians(30)
        px = p3d[0]
        py = p3d[1] * math.cos(flow) - p3d[2] * math.sin(flow)
        depth = p3d[2] * math.cos(flow) + p3d[1] * math.sin(flow)
        persp = 400 / (400 + depth * 0.2)
        return (int(WIDTH/2 + px * persp * 18), int(HEIGHT * 0.6 + py * persp * 18))
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    running = False
            
            self.screen.fill((2, 6, 20))
            
            # Get pen position
            pen_3d = self.get_pen_pos(self.t)
            pen_screen = self.project(pen_3d)
            center = (WIDTH // 2, int(HEIGHT * 0.6))
            
            # Check resonance
            is_aligned, radial = self.renderer.check_resonance(pen_3d)
            self.renderer.update(dt)
            
            # Trail
            self.trail.append(pen_screen)
            if len(self.trail) > 500:
                self.trail.pop(0)
            
            # Draw trail (squid ink)
            for i in range(len(self.trail) - 1):
                age = i / len(self.trail)
                c = int(40 + 180 * age)
                pygame.draw.line(self.screen, (int(c*0.3), int(c*0.7), c),
                               self.trail[i], self.trail[i+1], 2)
            
            # Draw all pulse layers
            self.renderer.draw_all(center, pen_screen, self.t)
            
            # Pen nib
            nib_color = (212, 175, 55) if is_aligned else (200, 200, 200)
            pygame.draw.circle(self.screen, nib_color, pen_screen, 4)
            
            # HUD
            self.screen.blit(self.font.render("DELIAN PULSE RENDERER: 93-NODE VITRIFICATION", True, (255, 255, 255)), (20, 20))
            self.screen.blit(self.font.render(f"RADIAL: {radial:.3f} | TARGET: {DELOS_CONSTANT:.3f}", True, 
                           (212, 175, 55) if is_aligned else (100, 100, 100)), (20, 40))
            self.screen.blit(self.font.render(f"PHI: {PHI:.6f} | CHIME: {CHIME_FREQ}Hz | RADULA: mod {RADULA_GATE}", True, (80, 80, 80)), (20, 60))
            self.renderer.draw_status(80)
            
            # 93-node legend
            self.screen.blit(self.font.render("90 TENTACLES (60E+20F+10V) + 3 HEARTS = 93 NODES", True, (50, 70, 90)), (20, HEIGHT - 50))
            self.screen.blit(self.font.render("[Q] QUIT", True, (60, 60, 60)), (WIDTH - 100, HEIGHT - 30))
            
            pygame.display.flip()
        
        pygame.quit()


if __name__ == "__main__":
    DelianPulseDemo().run()
