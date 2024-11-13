from fpdf import FPDF
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import HockeyRink  # Make sure your HockeyRink module is correctly set up

# Step 1: Data Cleansing Function
def import_clean_data(data_file):
    """
    Import and clean data based on project-specific rules:
    - Only 5 v 5 plays
    - No shots taking place across the ice
    - No empty-net shots
    - No shots from behind the net

    Args:
        data_file (str): Path to the CSV file containing shot data.

    Returns:
        DataFrame: Cleaned DataFrame with shot data.
    """
    data = pd.read_csv(data_file)
    data = data[(data['awaySkatersOnIce'] == 5) & (data['homeSkatersOnIce'] == 5)]
    data = data[data['shotDistance'] <= 89]
    data = data[data['shotOnEmptyNet'] == 0]
    data = data[data['xCordAdjusted'] <= 89]
    return data

def generate_league_xgoals_smooth(data):
    """
    Generates a league-wide smoothed xGoal heatmap by averaging shot data across all players.

    Args:
        data (DataFrame): DataFrame containing shot data for all players, with 'xCordAdjusted',
                          'yCordAdjusted', and 'xGoal' columns.

    Returns:
        league_xgoals_smooth (np.array): Smoothed xGoals array for the league.
    """
    # Define a grid for interpolation
    [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
    
    # Interpolate league-wide xGoal values on the grid
    league_xgoals = griddata(
        (data['xCordAdjusted'], data['yCordAdjusted']),
        data['xGoal'],
        (x, y), method='cubic', fill_value=0
    )
    
    # Replace any negative values with zero (if needed)
    league_xgoals = np.where(league_xgoals < 0, 0, league_xgoals)
    
    # Smooth the league-wide xGoal data
    league_xgoals_smooth = gaussian_filter(league_xgoals, sigma=3)
    
    return league_xgoals_smooth

# Step 2: Define Player Class
class Player:
    def __init__(self, player_name, data):
        """
        Initializes a Player object with player-specific shot data.

        Args:
            player_name (str): Name of the player.
            data (DataFrame): DataFrame containing shot data for all players.
        """
        self.player_name = player_name
        self.data = data[data['shooterName'] == player_name]
        self.total_shots = len(self.data)
        
    def get_basic_stats(self):
        """Calculate basic statistics such as total shots, goals, and shooting percentage."""
        goals = self.data[self.data['event'] == 'GOAL']
        shooting_percentage = len(goals) / self.total_shots * 100 if self.total_shots > 0 else 0
        return {
            "Total Shots": self.total_shots,
            "Goals": len(goals),
            "Shooting Percentage (%)": shooting_percentage
        }

    def shot_heatmap(self):
        """Creates a smoothed heatmap of shot probability (xGoal) for the player and returns the file path of the saved PNG."""
        [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
        xgoals_player = griddata(
            (self.data['xCordAdjusted'], self.data['yCordAdjusted']),
            self.data['xGoal'], (x, y), method='cubic', fill_value=0
        )
        xgoals_player = np.where(xgoals_player < 0, 0, xgoals_player)
        player_shots_smooth = gaussian_filter(xgoals_player, sigma=3)
        
        # Create the directory to store the heatmap image (optional)
        output_dir = "heatmaps"
        os.makedirs(output_dir, exist_ok=True)
        
        # Define the path for the output PNG file
        output_path = os.path.join(output_dir, f"{self.player_name}_xGoal_Smoothed_Heatmap.png")
        
        # Create the figure and plot the heatmap
        fig = plt.figure(figsize=(10, 12), facecolor='w', edgecolor='k')
        plt.imshow(player_shots_smooth, origin='lower')
        plt.colorbar(orientation='horizontal', pad=0.05)
        plt.title(f'{self.player_name} xGoal Smoothed Array', fontdict={'fontsize': 15})
        
        # Save the heatmap image to the defined file path
        plt.savefig(output_path)
        plt.close()  # Close the figure to free up memory
        
        # Return the file path of the saved heatmap image
        return output_path
    
    def compare_with_league(self, data):
        [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
        xgoals_player = griddata(
            (self.data['xCordAdjusted'], self.data['yCordAdjusted']),
            self.data['xGoal'], 
            (x, y), method='cubic', fill_value=0
        )
        xgoals_player = np.where(xgoals_player < 0, 0, xgoals_player)
        
        # Smooth the player's xGoal data
        player_shots_smooth = gaussian_filter(xgoals_player, sigma=3)

        # Smooth the leagu's xGoals
        league_xgoals_smooth = generate_league_xgoals_smooth(data)

        # Calculate the difference heatmap
        difference = player_shots_smooth - league_xgoals_smooth

        # Plot the difference heatmap with rink overlay
        fig, ax = plt.subplots(1, 1, figsize=(10, 12), facecolor='w', edgecolor='k')
        rink = HockeyRink.HockeyRink(board_radius=28, alpha=1)
        rink.draw(ax, plot_half=True)
        
        img = ax.imshow(difference, extent=(0, 89, -42.5, 42.5), cmap='bwr', origin='lower', alpha=0.4)
        fig.colorbar(img, orientation="horizontal", pad=0.05)
        plt.title(f'{self.player_name} vs League xGoal Difference', fontdict={'fontsize': 15})
        plt.axis('off')

        # Save the heatmap image
        filename = f"{self.player_name}_League_xGoal_Comparison.png"
        plt.savefig(filename)
        plt.close()
        
        return filename


    def high_danger_shots(self, distance_threshold=20):
        """Calculate high-danger shots based on a distance threshold."""
        high_danger_shots = self.data[self.data['shotDistance'] <= distance_threshold]
        return {
            "High Danger Shots": len(high_danger_shots),
            "High Danger Shot %": len(high_danger_shots) / self.total_shots * 100 if self.total_shots > 0 else 0
        }

def generate_player_report(player_name, data):
    # Step 1: Create a Player object
    player = Player(player_name, data)
    
    # Step 2: Generate basic stats
    basic_stats = player.get_basic_stats()

    # Step 3: Generate shot heatmap and save the path
    heatmap_image_path = player.shot_heatmap()

    # Step 4: Generate league comparison image and save the path
    league_comparison_image_path = player.compare_with_league(data)

    # Step 5: Generate high danger shots stats
    high_danger_stats = player.high_danger_shots()

    # Step 6: Create a PDF report
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add title
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, f"{player_name} - Personalized Shooting Report", ln=True, align="C")
    pdf.ln(10)

    # Add basic stats section
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Basic Stats:", ln=True)
    for stat, value in basic_stats.items():
        pdf.cell(200, 10, f"{stat}: {value}", ln=True)
    pdf.ln(10)

    # Add high danger shots section
    pdf.cell(200, 10, "High Danger Shots:", ln=True)
    for stat, value in high_danger_stats.items():
        pdf.cell(200, 10, f"{stat}: {value}", ln=True)
    pdf.ln(10)

    # Add Heatmap Image (first page)
    pdf.cell(200, 10, "Shot Heatmap:", ln=True)
    pdf.image(heatmap_image_path, x=10, y=pdf.get_y(), w=180)
    pdf.ln(90)  # Keep some space after the image for the next content

    # Add a new page before the league comparison heatmap
    pdf.add_page()
    
    # Add League Comparison Image
    pdf.cell(200, 10, "Comparison with League:", ln=True)
    pdf.image(league_comparison_image_path, x=10, y=pdf.get_y(), w=180)
    pdf.ln(10)

    # Step 7: Save the PDF to a file
    report_filename = f"{player_name}_Shooting_Report.pdf"
    pdf.output(report_filename)

    print(f"Report generated successfully: {report_filename}")
    return report_filename
