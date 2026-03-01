import pygame
import numpy as np
import math
import sys

# --- GEOFONT 13: THE PENMAN MODULUS (CUBIT PLATFORM EDITION) ---
# Bounded by the 10-24-26 Pythagorean Manifold
# Inspired by Barbara Nichol's "Art of Penmanship" and the "Cubit Arc" Sketch
WIDTH, HEIGHT = 1024, 768
FPS = 60

# Constants
MANUS = 5.0
CUBIT = 6.0
ROYAL_CUBIT = 7.0
DELIAN_POINT = 5.0 * (2.0 ** (1.0/3.0)) # ~6.2996

# Historical Slope Angles (Master Penmanship)
SLOPES = {
    "COPPERPLATE": math.radians(10.0),
    "ITALIC": math.radians(15.0),
    "WRITING": math.radians(30.0)
}

# The 3-Degree Master Key (Subtle Torsional Offset)
MATH_TILT = math.radians(3.0)

class PenmanGeoglyph:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PENMAN: The Cubit Platform & Delian Hand")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16, bold=True)
        self.t = 0.0
        self.points = []
        self.running = True
        self.current_slope_name = "COPPERPLATE"
        self.show_cubit_arcs = True
        self.show_forearm = True

    def get_trajectory(self, t):
        """
        Parametric 3D trajectory with Penman Slope and Torsional Tilt.
        Enforces "anticlockwise moving shape" mechanics.
        """
        # Outer radius R=10, Inner radius r varies for loop
        R = 10.0
        r = 3.33 
        
        # Primary rotation (The Hired Man)
        theta = t * 1.5 
        
        # Anticlockwise loop (The "Mechanics of Cursive")
        kx = R * math.cos(theta) + r * math.cos(-2 * theta)
        ky = R * math.sin(theta) + r * math.sin(-2 * theta)
        kz = t * 2.4 
        
        # 1. Apply Slope
        slope_angle = SLOPES[self.current_slope_name]
        y_sloped = ky * math.cos(slope_angle) - kz * math.sin(slope_angle)
        z_sloped = kz * math.cos(slope_angle) + ky * math.sin(slope_angle)
        x_sloped = kx
        
        # 2. Apply 3-Degree Master Key
        x_tilted = x_sloped * math.cos(MATH_TILT) - z_sloped * math.sin(MATH_TILT)
        z_header = z_sloped * math.cos(MATH_TILT) + x_sloped * math.sin(MATH_TILT)
        
        return np.array([x_tilted, y_sloped, z_header])

    def project(self, p):
        """Isometric Projection with depth scaling."""
        scale = 22.0
        iso_x = p[0] - p[2]
        iso_y = p[1] + (p[0] + p[2]) * 0.5
        return (WIDTH//2 + iso_x * scale, HEIGHT//2 + iso_y * scale)

    def draw_cubit_platform(self, current_p):
        """Draws the Forearm 'holding up' the Hand/Pen."""
        # The 'Base' of the forearm (The Elbow)
        elbow = np.array([0, 0, 0])
        p_elbow = self.project(elbow)
        p_hand = self.project(current_p)
        
        # Draw the Forearm Bone (The Cubit)
        pygame.draw.line(self.screen, (100, 100, 150), p_elbow, p_hand, 4)
        
        # Radial 'Support' arcs along the forearm
        for dist in np.linspace(0.2, 0.8, 4):
            mid_p = current_p * dist
            mid_pos = self.project(mid_p)
            pygame.draw.circle(self.screen, (50, 50, 100), (int(mid_pos[0]), int(mid_pos[1])), 5, 1)

    def draw_cubit_arc(self, radius, label, color):
        """Draws the rings from the 'Cubit Arc' sketch."""
        pts = []
        for angle in np.linspace(0, 2 * math.pi, 64):
            pts.append(self.project(np.array([radius * math.cos(angle), 0, radius * math.sin(angle)])))
        pygame.draw.aalines(self.screen, color, True, pts)
        
        label_pos = pts[int(64 * 30 / 360)]
        txt = self.font.render(label, True, color)
        self.screen.blit(txt, label_pos)

    def draw(self):
        self.screen.fill((2, 6, 20)) 
        
        # current head
        current_p = self.get_trajectory(self.t)

        if self.show_cubit_arcs:
            self.draw_cubit_arc(MANUS, "MANUS (5)", (50, 70, 90))
            self.draw_cubit_arc(CUBIT, "CUBIT (6)", (70, 90, 110))
            self.draw_cubit_arc(DELIAN_POINT, "DELOS (6.299)", (212, 175, 55))
            self.draw_cubit_arc(ROYAL_CUBIT, "ROYAL (7)", (90, 110, 130))

        if self.show_forearm:
            self.draw_cubit_platform(current_p)

        # Dynamic Trace
        self.points.append(current_p)
        if len(self.points) > 800: self.points.pop(0)
        
        if len(self.points) > 2:
            for i in range(len(self.points) - 1):
                p1 = self.project(self.points[i])
                p2 = self.project(self.points[i+1])
                pygame.draw.line(self.screen, (78, 205, 196), p1, p2, 2)

        # Head Marker (The Pen)
        head_pos = self.project(current_p)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(head_pos[0]), int(head_pos[1])), 4)
        # Pen Tip / Nib
        nib_pos = (int(head_pos[0] + 5), int(head_pos[1] - 5))
        pygame.draw.line(self.screen, (255, 255, 255), head_pos, nib_pos, 2)

        # Legend / Metadata
        self.render_text(f"HAND: {self.current_slope_name}", (20, 20), (212, 175, 55))
        self.render_text(f"PLATFORM: CUBIT FOREARM ACTIVE", (20, 40), (100, 100, 150))
        self.render_text(f"DELOS ALIGNMENT: {(1.0 - abs(np.linalg.norm(current_p[:2]) - DELIAN_POINT) / DELIAN_POINT)*100:.2f}%", (20, 90))

        # Keyboard Guide
        self.render_text("[1-3] SLOPES | [Space] ARCS | [F] FOREARM | [Q] QUIT", (WIDTH - 450, HEIGHT - 30), (100, 100, 100))

        pygame.display.flip()

    def render_text(self, text, pos, color=(200, 200, 200)):
        txt = self.font.render(text, True, color)
        self.screen.blit(txt, pos)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: self.current_slope_name = "COPPERPLATE"
                if event.key == pygame.K_2: self.current_slope_name = "ITALIC"
                if event.key == pygame.K_3: self.current_slope_name = "WRITING"
                if event.key == pygame.K_SPACE: self.show_cubit_arcs = not self.show_cubit_arcs
                if event.key == pygame.K_f: self.show_forearm = not self.show_forearm
                if event.key == pygame.K_q: self.running = False

    def run(self):
        while self.running:
            self.handle_input()
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    PenmanGeoglyph().run()
