from func_class import import_clean_data, Player, generate_player_report

data = import_clean_data("shots_2023.csv")

# Call the method to get the basic stats
generate_player_report('Connor McDavid', data)
