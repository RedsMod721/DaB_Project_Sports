from func_class import import_clean_data, Player, Team, generate_player_report, generate_team_report 

data = import_clean_data("shots_2023.csv")
shoot_data = import_clean_data("shots_2023.csv")
team_data = pd.read_csv("skaters.csv")

generate_player_report('Connor McDavid', data)

generate_team_report('OTT', shoot_data, team_data)
