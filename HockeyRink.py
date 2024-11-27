import matplotlib as mpl
import matplotlib.pyplot as plt

class HockeyRink:
    def __init__(self, board_radius=28, alpha=1):
        """
        Initialize a HockeyRink object.
        
        Args:
            board_radius (float): Radius of the corner boards
            alpha (float): Transparency level of the rink elements
        """
        self.board_radius = board_radius
        self.alpha = alpha
        
    def draw_corner_boards(self, ax):
        """Draw the corner boards of the rink."""
        # Top Right
        ax.add_artist(mpl.patches.Arc(
            (100-self.board_radius, (85/2)-self.board_radius),
            self.board_radius * 2, self.board_radius * 2,
            theta1=0, theta2=89, edgecolor='Black', lw=4.5,
            zorder=1, alpha=self.alpha
        ))
        # Top Left
        ax.add_artist(mpl.patches.Arc(
            (-100+self.board_radius+.1, (85/2)-self.board_radius),
            self.board_radius * 2, self.board_radius * 2,
            theta1=90, theta2=180, edgecolor='Black', lw=4.5,
            zorder=1, alpha=self.alpha
        ))
        # Bottom Left
        ax.add_artist(mpl.patches.Arc(
            (-100+self.board_radius+.1, -(85/2)+self.board_radius-.1),
            self.board_radius * 2, self.board_radius * 2,
            theta1=180, theta2=270, edgecolor='Black', lw=4.5,
            zorder=1, alpha=self.alpha
        ))
        # Bottom Right
        ax.add_artist(mpl.patches.Arc(
            (100-self.board_radius, -(85/2)+self.board_radius-.1),
            self.board_radius * 2, self.board_radius * 2,
            theta1=270, theta2=360, edgecolor='Black', lw=4.5,
            zorder=1, alpha=self.alpha
        ))

    def draw_boards(self, ax):
        """Draw the straight boards of the rink."""
        # Bottom
        ax.plot([-100+self.board_radius,100-self.board_radius], 
                [-42.75, -42.75], linewidth=6, color="Black", 
                zorder=1, alpha=self.alpha)
        # Top
        ax.plot([-100+self.board_radius-1,100-self.board_radius+1], 
                [42.5, 42.5], linewidth=4.5, color="Black", 
                zorder=1, alpha=self.alpha)
        # Left
        ax.plot([-100,-100], [-42.5+self.board_radius, 42.5-self.board_radius], 
                linewidth=4.5, color="Black", zorder=1, alpha=self.alpha)
        # Right
        ax.plot([100,100], [-42.5+self.board_radius, 42.5-self.board_radius], 
                linewidth=4.5, color="Black", zorder=1, alpha=self.alpha)

    def draw_lines(self, ax):
        """Draw goal lines, center line, and blue lines."""
        # Goal Lines
        adj_top, adj_bottom = 4.6, 4.5
        ax.plot([89,89], [-41+adj_bottom, 41-adj_top], 
                linewidth=3, color="Red", zorder=0, alpha=self.alpha)
        ax.plot([-89,-89], [-42.5+adj_bottom, 42.5-adj_top], 
                linewidth=3, color="Red", zorder=0, alpha=self.alpha)
        
        # Center Line
        ax.plot([0,0], [-42.5, 42.5], 
                linewidth=3, color="Red", zorder=0, alpha=self.alpha)
        
        # Blue Lines
        ax.plot([25,25], [-42.5, 42.5], 
                linewidth=2, color="Blue", zorder=0, alpha=self.alpha)
        ax.plot([-25,-25], [-42.5, 42.5], 
                linewidth=2, color="Blue", zorder=0, alpha=self.alpha)

    def draw_center_ice(self, ax):
        """Draw center ice dot and circle."""
        ax.plot(0, 0, markersize=6, color="Blue", 
                marker="o", zorder=0, alpha=self.alpha)
        ax.add_artist(mpl.patches.Circle(
            (0, 0), radius=33/2, facecolor='none',
            edgecolor="Blue", linewidth=3, zorder=0, alpha=self.alpha
        ))

    def draw_faceoff_spots(self, ax):
        """Draw all faceoff spots and circles."""
        # Zone Faceoff Dots
        faceoff_coords = [(69, 22), (69, -22), (-69, 22), (-69, -22)]
        for x, y in faceoff_coords:
            ax.plot(x, y, markersize=6, color="Red", 
                    marker="o", zorder=0, alpha=self.alpha)
            ax.add_artist(mpl.patches.Circle(
                (x, y), radius=15, facecolor='none',
                edgecolor="Red", linewidth=3, zorder=0, alpha=self.alpha
            ))
        
        # Neutral Zone Faceoff Dots
        neutral_coords = [(22, 22), (22, -22), (-22, 22), (-22, -22)]
        for x, y in neutral_coords:
            ax.plot(x, y, markersize=6, color="Red", 
                    marker="o", zorder=0, alpha=self.alpha)

    def draw_goals_and_creases(self, ax):
        """Draw goals and goalie creases."""
        # Goalie Creases
        ax.add_artist(mpl.patches.Arc(
            (89, 0), 6, 6, theta1=90, theta2=270,
            facecolor="Blue", edgecolor='Red', lw=2,
            zorder=0, alpha=self.alpha
        ))
        ax.add_artist(mpl.patches.Arc(
            (-89, 0), 6, 6, theta1=270, theta2=90,
            facecolor="Blue", edgecolor='Red', lw=2,
            zorder=0, alpha=self.alpha
        ))
        
        # Goals
        ax.add_artist(mpl.patches.Rectangle(
            (89, -2), 2, 4, lw=2, color='Red',
            fill=False, zorder=0, alpha=self.alpha
        ))
        ax.add_artist(mpl.patches.Rectangle(
            (-91, -2), 2, 4, lw=2, color='Red',
            fill=False, zorder=0, alpha=self.alpha
        ))

    def set_display_settings(self, ax, plot_half=False):
        """Configure display settings for the rink."""
        if plot_half:
            ax.set_xlim(-0.5, 100.5)
        else:
            ax.set_xlim(-101, 101)
        ax.set_ylim(-43, 43)
        
        # Hide spines
        for spine in ax.spines.values():
            spine.set_visible(False)

    def draw(self, ax, plot_half=False):
        """
        Draw the complete hockey rink.
        
        Args:
            ax: Matplotlib axis object
            plot_half (bool): If True, only draw half the rink
        """
        self.draw_corner_boards(ax)
        self.draw_boards(ax)
        self.draw_lines(ax)
        self.draw_center_ice(ax)
        self.draw_faceoff_spots(ax)
        self.draw_goals_and_creases(ax)
        self.set_display_settings(ax, plot_half)
