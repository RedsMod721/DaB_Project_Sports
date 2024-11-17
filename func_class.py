import tempfile
import shutil
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

        # Check if the player exists in the dataset
        if player_name not in data['shooterName'].values:
            print(f"Error: Player '{player_name}' not found in the data.")
            # Allow user to retry by prompting them for a valid name
            raise ValueError(f"Player '{player_name}' not found in the dataset.")

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

    def shot_heatmap(self, output_dir="heatmaps"):
        """
        Creates a smoothed heatmap of shot probability (xGoal) for the player and returns the file path of the saved PNG.

        Args:
            output_dir (str): Directory to save the generated heatmap file.
        """
        [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
        xgoals_player = griddata(
            (self.data['xCordAdjusted'], self.data['yCordAdjusted']),
            self.data['xGoal'], (x, y), method='cubic', fill_value=0
        )
        xgoals_player = np.where(xgoals_player < 0, 0, xgoals_player)
        player_shots_smooth = gaussian_filter(xgoals_player, sigma=3)
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define the path for the output PNG file
        output_path = os.path.join(output_dir, f"{self.player_name}_xGoal_Smoothed_Heatmap.png")
        
        # Create the figure and plot the heatmap
        fig = plt.figure(figsize=(10, 12), facecolor='w', edgecolor='k')
        plt.imshow(player_shots_smooth, origin='lower')
        plt.colorbar(orientation='horizontal', pad=0.05)
        plt.title(f'{self.player_name} xGoal Smoothed Array', fontdict={'fontsize': 15})
        
        # Save the heatmap image to the specified output path
        plt.savefig(output_path)
        plt.close()  # Close the figure to free up memory
        
        # Return the file path of the saved heatmap image
        return output_path

    def compare_with_league(self, data=None, output_dir="heatmaps"):
        """
        Compares player's xGoal heatmap with league average and returns the file path of the saved PNG.

        Args:
            data (DataFrame, optional): League-wide shot data for comparison. Defaults to None.
            output_dir (str): Directory to save the generated heatmap file.

        Returns:
            str: File path of the saved comparison heatmap.
        """
        if data is None:
            data = self.data

        [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
        xgoals_player = griddata(
            (self.data['xCordAdjusted'], self.data['yCordAdjusted']),
            self.data['xGoal'],
            (x, y), method='cubic', fill_value=0
        )
        xgoals_player = np.where(xgoals_player < 0, 0, xgoals_player)
        
        # Smooth the player's xGoal data
        player_shots_smooth = gaussian_filter(xgoals_player, sigma=3)

        # Smooth the league's xGoals
        league_xgoals_smooth = generate_league_xgoals_smooth(data)

        # Calculate the difference heatmap
        difference = player_shots_smooth - league_xgoals_smooth

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define the path for the output PNG file
        output_path = os.path.join(output_dir, f"{self.player_name}_League_xGoal_Comparison.png")

        # Plot the difference heatmap with rink overlay
        fig, ax = plt.subplots(1, 1, figsize=(10, 12), facecolor='w', edgecolor='k')
        rink = HockeyRink.HockeyRink(board_radius=28, alpha=1)
        rink.draw(ax, plot_half=True)

        img = ax.imshow(difference, extent=(0, 89, -42.5, 42.5), cmap='bwr', origin='lower', alpha=0.4)
        fig.colorbar(img, orientation="horizontal", pad=0.05)
        plt.title(f'{self.player_name} vs League xGoal Difference', fontdict={'fontsize': 15})
        plt.axis('off')

        # Save the heatmap image to the specified output path
        plt.savefig(output_path)
        plt.close()

        # Return the file path of the saved heatmap image
        return output_path

    def high_danger_shots(self, distance_threshold=20):
        """Calculate high-danger shots based on a distance threshold."""
        high_danger_shots = self.data[self.data['shotDistance'] <= distance_threshold]
        return {
            "High Danger Shots": len(high_danger_shots),
            "High Danger Shot %": len(high_danger_shots) / self.total_shots * 100 if self.total_shots > 0 else 0
        }

class Team:
    def __init__(self, team_name, shot_data, skaters_data):
        """
        Initializes a Team object containing multiple players.

        Args:
            team_name (str): Name of the team.
            shot_data (DataFrame): DataFrame containing shot data for all players.
            skaters_data (DataFrame): DataFrame containing skaters' data.
        """
        self.team_name = team_name
        self.shot_data = shot_data
        self.skaters_data = skaters_data
        self.players = self.get_team_players()

    def get_team_players(self):
        """
        Retrieves players who belong to the specified team and initializes them as Player objects.

        Returns:
            list: A list of Player objects for the team.
        """
        team_players = self.skaters_data[self.skaters_data['team'] == self.team_name]
        player_objects = []

        for player_name in team_players['name'].unique():
            player_data = self.shot_data[self.shot_data['shooterName'] == player_name]
            if not player_data.empty:
                player_objects.append(Player(player_name, player_data))
        
        return player_objects
    
    def get_basic_stats(self):
        """
        Calculates and aggregates basic stats for all players in the team.

        Returns:
            dict: A dictionary containing total shots, total goals, and average shooting percentage for the team.
        """
        total_shots = 0
        total_goals = 0
        total_shooting_percentage = 0.0
        player_count = len(self.players)

        # Aggregate stats from each player
        for player in self.players:
            stats = player.get_basic_stats()
            total_shots += stats["Total Shots"]
            total_goals += stats["Goals"]
            total_shooting_percentage += stats["Shooting Percentage (%)"]

        # Calculate average shooting percentage across players
        avg_shooting_percentage = total_shooting_percentage / player_count if player_count > 0 else 0

        return {
            "Team": self.team_name,
            "Total Shots": total_shots,
            "Total Goals": total_goals,
            "Average Shooting Percentage (%)": avg_shooting_percentage
        }

    def shot_heatmap(self, output_dir="heatmaps"):
        """
        Creates a smoothed heatmap of shot probability (xGoal) for the entire team 
        and returns the file path of the saved PNG.
        
        Args:
            output_dir (str): Directory to save the heatmap image. Defaults to "heatmaps".
        
        Returns:
            str: Full path to the saved heatmap image.
        """
        # Combine shot data from all players on the team
        team_data = pd.concat([player.data for player in self.players], ignore_index=True)
        
        # Set up the mesh grid for heatmap
        [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
        
        # Interpolate shot probabilities (xGoal) over the grid
        xgoals_team = griddata(
            (team_data['xCordAdjusted'], team_data['yCordAdjusted']),
            team_data['xGoal'], (x, y), method='cubic', fill_value=0
        )
        
        # Ensure no negative values and smooth the heatmap
        xgoals_team = np.where(xgoals_team < 0, 0, xgoals_team)
        team_shots_smooth = gaussian_filter(xgoals_team, sigma=3)
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define the path for the team heatmap PNG file
        output_path = os.path.join(output_dir, f"{self.team_name}_xGoal_Smoothed_Heatmap.png")
        
        # Plot the heatmap
        fig = plt.figure(figsize=(10, 12), facecolor='w', edgecolor='k')
        plt.imshow(team_shots_smooth, origin='lower')
        plt.colorbar(orientation='horizontal', pad=0.05)
        plt.title(f'{self.team_name} xGoal Smoothed Array', fontdict={'fontsize': 15})
        
        # Save the heatmap image
        plt.savefig(output_path)
        plt.close()

        # Return the file path of the saved heatmap image
        return output_path

    def compare_with_league(self, league_data=None, output_dir="heatmaps"):
        """
        Compares the team's shot probability heatmap with the league's shot probability heatmap and returns
        the file path of the saved difference heatmap.

        Args:
            league_data (DataFrame): DataFrame containing league-wide shot data for comparison.
            output_dir (str): Directory to save the generated heatmap file.

        Returns:
            str: File path of the saved team vs. league difference heatmap.
        """
        # Use team's shot data if league_data is not provided
        if league_data is None:
            league_data = self.shot_data

        # Combine shot data for all players on the team
        team_data = pd.concat([player.data for player in self.players], ignore_index=True)

        # Generate team's xGoals on a grid
        [x, y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
        xgoals_team = griddata(
            (team_data['xCordAdjusted'], team_data['yCordAdjusted']),
            team_data['xGoal'], (x, y), method='cubic', fill_value=0
        )
        xgoals_team = np.where(xgoals_team < 0, 0, xgoals_team)
        team_shots_smooth = gaussian_filter(xgoals_team, sigma=3)

        # Generate league's xGoals smooth heatmap
        league_xgoals_smooth = generate_league_xgoals_smooth(league_data)

        # Calculate the difference between the team and league heatmaps
        difference = team_shots_smooth - league_xgoals_smooth

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define the path for the saved heatmap file
        output_path = os.path.join(output_dir, f"{self.team_name}_League_xGoal_Comparison.png")

        # Plot the difference heatmap with rink overlay
        fig, ax = plt.subplots(1, 1, figsize=(10, 12), facecolor='w', edgecolor='k')
        rink = HockeyRink.HockeyRink(board_radius=28, alpha=1)
        rink.draw(ax, plot_half=True)

        img = ax.imshow(difference, extent=(0, 89, -42.5, 42.5), cmap='bwr', origin='lower', alpha=0.4)
        fig.colorbar(img, orientation="horizontal", pad=0.05)
        plt.title(f'{self.team_name} vs League xGoal Difference', fontdict={'fontsize': 15})
        plt.axis('off')

        # Save the heatmap image
        plt.savefig(output_path)
        plt.close()

        # Return the file path of the saved heatmap image
        return output_path
   
    def high_danger_shots(self, distance_threshold=20):
        """
        Calculate high-danger shots for the entire team based on a specified distance threshold.

        Args:
            distance_threshold (int, optional): Distance threshold to define high-danger shots. Defaults to 20.

        Returns:
            dict: Dictionary with total high-danger shots and percentage of high-danger shots for the team.
        """
        # Filter shots within the high-danger threshold across all players
        high_danger_shots = self.shot_data[self.shot_data['shotDistance'] <= distance_threshold]
        
        # Calculate total shots for the team
        total_team_shots = len(self.shot_data)

        return {
            "High Danger Shots": len(high_danger_shots),
            "High Danger Shot %": (len(high_danger_shots) / total_team_shots * 100) if total_team_shots > 0 else 0
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

def generate_team_report(team_name, shot_data, team_data):
    """
    Generates a PDF report for the specified team, including a summary of team statistics,
    a team-level shot heatmap, individual reports for each player, and comparisons to the league average.

    Args:
        team_name (str): Name of the team.
        shot_data (DataFrame): DataFrame containing shot data for all players.
        team_data (DataFrame): DataFrame containing player information and performance data for the team.
    """
    # Initialize Team object
    team = Team(team_name, shot_data, team_data)
    
    # Define the heatmaps directory
    heatmaps_dir = "heatmaps"
    os.makedirs(heatmaps_dir, exist_ok=True)
    
    try:
        # Create a PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add Team Summary
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"{team_name} Team Report", ln=True, align="C")
        pdf.ln(10)
        
        # Calculate and add team basic stats
        team_stats = team.get_basic_stats()
        pdf.set_font("Arial", size=12)
        for stat, value in team_stats.items():
            pdf.cell(0, 10, f"{stat}: {value}", ln=True)
        pdf.ln(10)
        
        # Add team high danger shots
        high_danger_stats = team.high_danger_shots()
        for stat, value in high_danger_stats.items():
            pdf.cell(0, 10, f"{stat}: {value}", ln=True)
        pdf.ln(10)
        
        # Generate and add Team Heatmap
        team_heatmap_path = team.shot_heatmap(output_dir=heatmaps_dir)
        pdf.cell(0, 10, "Team Shot Heatmap:", ln=True)
        pdf.image(team_heatmap_path, x=10, y=pdf.get_y() + 5, w=180)
        pdf.add_page()
        
        # League comparison heatmap for the team
        team_vs_league_path = team.compare_with_league(league_data=shot_data, output_dir=heatmaps_dir)
        pdf.cell(0, 10, "Team vs. League Shot Heatmap:", ln=True)
        pdf.image(team_vs_league_path, x=10, y=pdf.get_y() + 5, w=180)
        
        # Individual Player Reports
        for player in team.players:
            pdf.add_page()
            
            # Get player stats
            player_stats = player.get_basic_stats()
            high_danger_stats = player.high_danger_shots()
            
            # Add player header
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"{player.player_name} - Individual Report", ln=True)
            
            # Add player basic stats
            pdf.set_font("Arial", size=12)
            for stat, value in player_stats.items():
                pdf.cell(0, 10, f"{stat}: {value}", ln=True)
            
            # Add player high danger stats
            for stat, value in high_danger_stats.items():
                pdf.cell(0, 10, f"{stat}: {value}", ln=True)
            
            # Player Shot Heatmap
            heatmap_path = player.shot_heatmap(output_dir=heatmaps_dir)
            pdf.ln(10)
            pdf.cell(0, 10, "Player Shot Heatmap:", ln=True)
            pdf.image(heatmap_path, x=10, y=pdf.get_y() + 5, w=180)
            
            # Player League Comparison Heatmap
            comparison_path = player.compare_with_league(data=shot_data, output_dir=heatmaps_dir)
            pdf.add_page()
            pdf.cell(0, 10, "Comparison with League Heatmap:", ln=True)
            pdf.image(comparison_path, x=10, y=pdf.get_y() + 5, w=180)
        
        # Save the PDF
        output_filename = f"{team_name}_Team_Report.pdf"
        pdf.output(output_filename)
        print(f"Team report generated and saved as {output_filename}.")
    
    finally:
        # Clean up the heatmaps folder
        if os.path.exists(heatmaps_dir):
            for file in os.listdir(heatmaps_dir):
                file_path = os.path.join(heatmaps_dir, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            os.rmdir(heatmaps_dir)  # Remove the directory itself

    return output_filename
