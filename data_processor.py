import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(file_path):
    try:
        data = pd.read_csv(file_path)
        plt.figure(figsize=(10, 6))
        sns.histplot(data['player_actions'], bins=30)
        plt.title('Player Actions Frequency')
        plt.xlabel('Actions')
        plt.ylabel('Frequency')
        plt.show()
    except Exception as e:
        raise Exception(f"Plotting data failed: {e}")
