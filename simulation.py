"""
simulation.py – محرك محاكاة الاستاد
Stadium Simulation Core – NumPy-based crowd agents
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import random


# ──────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────
CELL_SIZE   = 16        # pixels per grid cell
FIELD_COLOR = (0, 60, 20)      # green field
BG_COLOR    = (5, 13, 10)      # dark background
GATE_COLOR  = (220, 220, 220)  # white gates

# Crowd density → color gradient
DENSITY_COLORS = [
    (0,   0,   0,   0),    # 0  – empty
    (0,   108, 53,  200),  # 1  – Saudi green (sparse)
    (0,   165, 80,  220),  # 2-3 – light green
    (0,   200, 100, 230),  # 4-6
    (255, 149, 0,   240),  # 7-9 – warning orange
    (255, 59,  48,  255),  # 10+ – critical red
]


def _density_to_color(count: int) -> tuple:
    """Map agent count in a cell → RGBA color."""
    if count == 0:
        return (0, 0, 0, 0)
    elif count <= 1:
        return DENSITY_COLORS[1]
    elif count <= 3:
        return DENSITY_COLORS[2]
    elif count <= 6:
        return DENSITY_COLORS[3]
    elif count <= 9:
        return DENSITY_COLORS[4]
    else:
        return DENSITY_COLORS[5]


# ──────────────────────────────────────────────────────────────────
# Agent Class – represents a fan/spectator
# ──────────────────────────────────────────────────────────────────
class Agent:
    __slots__ = ("row", "col", "target_row", "target_col",
                 "speed", "state", "evacuation_path")

    def __init__(self, row: int, col: int, rows: int, cols: int):
        self.row = row
        self.col = col
        self.speed = random.uniform(0.5, 1.5)  # individual speed variance
        self.state = "moving"          # moving | seated | evacuating
        # Random target within stadium
        self.target_row = random.randint(2, rows - 3)
        self.target_col = random.randint(2, cols - 3)
        self.evacuation_path = None


# ──────────────────────────────────────────────────────────────────
# StadiumSimulation
# ──────────────────────────────────────────────────────────────────
class StadiumSimulation:
    """
    NumPy-based grid simulation of a stadium.
    Grid cells store the count of agents present.
    """

    def __init__(self, rows: int = 30, cols: int = 40):
        self.rows = rows
        self.cols = cols
        self.grid: np.ndarray = np.zeros((rows, cols), dtype=np.int16)

        # Configuration
        self.flow_speed  = 5        # gate flow speed (1-10)
        self.routing     = "normal"
        self.emergency   = False
        self.gates_open  = True

        # Gate locations (row, col) pairs for each side
        self.gates = self._init_gates()

        # Field zone (center rectangle) – no agents allowed here
        self.field_rows = slice(rows // 4, 3 * rows // 4)
        self.field_cols = slice(cols // 5, 4 * cols // 5)

        # Agents list
        self.agents: list[Agent] = []

        # Pre-populate with initial crowd
        self.add_agents(600, "random")

    # ── Gate Initialization ──────────────────────────────────────
    def _init_gates(self) -> dict:
        """Define gate positions around the stadium perimeter."""
        return {
            "north": [(0, self.cols // 4), (0, self.cols // 2), (0, 3 * self.cols // 4)],
            "south": [(self.rows - 1, self.cols // 4), (self.rows - 1, self.cols // 2),
                      (self.rows - 1, 3 * self.cols // 4)],
            "east":  [(self.rows // 4, self.cols - 1), (self.rows // 2, self.cols - 1),
                      (3 * self.rows // 4, self.cols - 1)],
            "west":  [(self.rows // 4, 0), (self.rows // 2, 0), (3 * self.rows // 4, 0)],
        }

    # ── Add Agents ───────────────────────────────────────────────
    def add_agents(self, count: int, zone: str = "random"):
        """Spawn agents at a given zone entrance."""
        zone_spawns = {
            "north":  lambda: (random.randint(0, 3),              random.randint(0, self.cols - 1)),
            "south":  lambda: (random.randint(self.rows - 4, self.rows - 1), random.randint(0, self.cols - 1)),
            "east":   lambda: (random.randint(0, self.rows - 1),  random.randint(self.cols - 4, self.cols - 1)),
            "west":   lambda: (random.randint(0, self.rows - 1),  random.randint(0, 3)),
            "random": lambda: (random.randint(0, self.rows - 1),  random.randint(0, self.cols - 1)),
        }
        spawn_fn = zone_spawns.get(zone, zone_spawns["random"])

        for _ in range(count):
            r, c = spawn_fn()
            r = np.clip(r, 0, self.rows - 1)
            c = np.clip(c, 0, self.cols - 1)
            # Skip field area
            if self.field_rows.start <= r < self.field_rows.stop and \
               self.field_cols.start <= c < self.field_cols.stop:
                continue
            agent = Agent(r, c, self.rows, self.cols)
            self.agents.append(agent)
            self.grid[r, c] += 1

    # ── Configuration Setters ────────────────────────────────────
    def set_flow_speed(self, speed: int):
        self.flow_speed = speed

    def set_gates(self, open_all: bool):
        self.gates_open = open_all

    def set_routing(self, mode: str):
        self.routing = mode
        if mode == "north":
            for a in self.agents:
                a.target_row = random.randint(0, 3)
        elif mode == "south":
            for a in self.agents:
                a.target_row = random.randint(self.rows - 4, self.rows - 1)
        elif mode == "balanced":
            for i, a in enumerate(self.agents):
                # Alternate agents between exits
                if i % 4 == 0:   a.target_row = 0
                elif i % 4 == 1: a.target_row = self.rows - 1
                elif i % 4 == 2: a.target_col = 0
                else:             a.target_col = self.cols - 1

    def set_emergency(self, active: bool):
        self.emergency = active
        if active:
            # All agents rush to nearest exit
            for a in self.agents:
                exits = [0, self.rows - 1]
                a.target_row = min(exits, key=lambda e: abs(e - a.row))
                a.target_col = (0 if a.col < self.cols // 2 else self.cols - 1)
                a.state = "evacuating"
                a.speed = random.uniform(1.5, 3.0)  # faster in emergency

    def reroute_agents(self, mode: str):
        self.set_routing(mode)

    # ── Simulation Step ──────────────────────────────────────────
    def step(self):
        """Advance simulation by one tick using vectorized movement."""
        # Speed multiplier from gate setting
        base_prob = self.flow_speed / 10.0

        new_grid = np.zeros_like(self.grid)
        departed = []

        for agent in self.agents:
            # Skip if already exited
            move_prob = base_prob * agent.speed
            if self.emergency:
                move_prob = min(1.0, move_prob * 2.0)

            if random.random() > move_prob:
                # Agent stays this tick
                new_grid[agent.row, agent.col] += 1
                continue

            # Compute desired direction toward target
            dr = np.sign(agent.target_row - agent.row)
            dc = np.sign(agent.target_col - agent.col)

            # Candidate moves: preferred + small randomness
            candidates = [(dr, dc), (dr, 0), (0, dc), (0, 0),
                          (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))]

            moved = False
            for drow, dcol in candidates:
                nr = agent.row + int(drow)
                nc = agent.col + int(dcol)

                # Boundary check
                if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    # Reached boundary – agent exits if gates open
                    if self.gates_open or self.emergency:
                        departed.append(agent)
                        moved = True
                        break
                    continue

                # Avoid field
                if (self.field_rows.start <= nr < self.field_rows.stop and
                        self.field_cols.start <= nc < self.field_cols.stop):
                    continue

                # Move agent
                agent.row, agent.col = nr, nc
                new_grid[nr, nc] += 1
                moved = True
                break

            if not moved:
                new_grid[agent.row, agent.col] += 1

        # Remove departed agents
        for a in departed:
            self.agents.remove(a)

        self.grid = new_grid

    # ── Metrics ──────────────────────────────────────────────────
    def get_metrics(self) -> dict:
        crowd_count = len(self.agents)
        # Average density (% of max safe occupancy per cell, max ~15)
        non_zero = self.grid[self.grid > 0]
        avg_density = float(np.mean(non_zero) / 15 * 100) if len(non_zero) > 0 else 0
        avg_density = min(avg_density, 100)

        # Hotspots: cells with >10 agents
        hotspots = int(np.sum(self.grid > 10))

        # Evac efficiency – percentage of perimeter cells free (proxy)
        perimeter_cells = (
            self.grid[0, :].sum() + self.grid[-1, :].sum() +
            self.grid[:, 0].sum() + self.grid[:, -1].sum()
        )
        max_perimeter = 2 * (self.rows + self.cols) * 8
        evac_eff = max(0, 100 - float(perimeter_cells) / max_perimeter * 100)

        return {
            "crowd_count": crowd_count,
            "avg_density": avg_density,
            "evac_efficiency": evac_eff,
            "hotspots": hotspots,
        }

    def get_zone_densities(self) -> dict:
        """Return average density % for 5 zones of the stadium."""
        r, c = self.rows, self.cols
        zones = {
            "north":  self.grid[:r // 4, :],
            "south":  self.grid[3 * r // 4:, :],
            "east":   self.grid[:, 3 * c // 4:],
            "west":   self.grid[:, :c // 4],
            "center": self.grid[r // 4:3 * r // 4, c // 4:3 * c // 4],
        }
        result = {}
        for name, zone in zones.items():
            nz = zone[zone > 0]
            result[name] = float(np.mean(nz) / 15 * 100) if len(nz) > 0 else 0
        return result

    # ── Grid Rendering ───────────────────────────────────────────
    def render_grid_image(self) -> Image.Image:
        """Render the grid as a PIL Image with colored density cells."""
        img_w = self.cols * CELL_SIZE
        img_h = self.rows * CELL_SIZE
        img = Image.new("RGBA", (img_w, img_h), (5, 13, 10, 255))
        draw = ImageDraw.Draw(img)

        # Draw field background
        fx1 = self.field_cols.start * CELL_SIZE
        fx2 = self.field_cols.stop  * CELL_SIZE
        fy1 = self.field_rows.start * CELL_SIZE
        fy2 = self.field_rows.stop  * CELL_SIZE
        draw.rectangle([fx1, fy1, fx2, fy2], fill=(0, 80, 30, 255))
        # Field center circle
        cx, cy = (fx1 + fx2) // 2, (fy1 + fy2) // 2
        r_circle = min(fx2 - fx1, fy2 - fy1) // 5
        draw.ellipse([cx - r_circle, cy - r_circle, cx + r_circle, cy + r_circle],
                     outline=(0, 130, 50, 200), width=2)
        # Field lines
        draw.line([(cx, fy1), (cx, fy2)], fill=(0, 130, 50, 180), width=1)

        # Draw grid cells
        for row in range(self.rows):
            for col in range(self.cols):
                count = int(self.grid[row, col])
                if count == 0:
                    continue
                # Skip field interior
                if (self.field_rows.start <= row < self.field_rows.stop and
                        self.field_cols.start <= col < self.field_cols.stop):
                    continue
                x0 = col * CELL_SIZE
                y0 = row * CELL_SIZE
                color = _density_to_color(count)
                draw.rectangle(
                    [x0 + 1, y0 + 1, x0 + CELL_SIZE - 2, y0 + CELL_SIZE - 2],
                    fill=color[:3]
                )

        # Draw gates
        for side, gate_list in self.gates.items():
            for (gr, gc) in gate_list:
                x0 = gc * CELL_SIZE
                y0 = gr * CELL_SIZE
                gate_fill = (0, 165, 80) if self.gates_open else (180, 60, 60)
                draw.rectangle(
                    [x0 + 2, y0 + 2, x0 + CELL_SIZE - 3, y0 + CELL_SIZE - 3],
                    fill=gate_fill, outline=(255, 255, 255, 150), width=1
                )

        # Grid lines (subtle)
        for col in range(0, img_w, CELL_SIZE):
            draw.line([(col, 0), (col, img_h)], fill=(0, 40, 20, 80), width=1)
        for row in range(0, img_h, CELL_SIZE):
            draw.line([(0, row), (img_w, row)], fill=(0, 40, 20, 80), width=1)

        # Emergency overlay – red tint on hotspot cells
        if self.emergency:
            overlay = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            ov_draw = ImageDraw.Draw(overlay)
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.grid[row, col] > 10:
                        x0, y0 = col * CELL_SIZE, row * CELL_SIZE
                        ov_draw.rectangle(
                            [x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE],
                            fill=(255, 0, 0, 60)
                        )
            img = Image.alpha_composite(img, overlay)

        return img.convert("RGB")
