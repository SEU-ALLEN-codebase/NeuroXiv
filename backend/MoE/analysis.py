import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def analyze_by_model():
    # Load the CSV file
    file_path = './log_0726_batch/test1/MoE_scores_20240726_222715.csv'
    df = pd.read_csv(file_path)

    # Filter and group the data
    filtered_df = df[(df[['Accuracy', 'Consistency', 'Readability', 'Conciseness']] != 0).all(axis=1)]
    grouped_df = filtered_df.groupby('Model').mean()

    # Select the relevant columns
    score_means = grouped_df[['Accuracy', 'Consistency', 'Readability', 'Conciseness']]

    # Plotting the data
    fig, ax = plt.subplots(figsize=(10, 6))
    score_means.plot(kind='bar', ax=ax)
    ax.set_title('Average Scores by Model')
    ax.set_xlabel('Model')
    ax.set_ylabel('Average Score')
    ax.legend(loc='best')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the plot
    plt.show()

def generate_distinct_colors(n):
    colors = cm.get_cmap('tab20', n)
    return colors(np.linspace(0, 1, n))

def analyze_by_model_type():
    import pandas as pd
    import matplotlib.pyplot as plt

    # Load the CSV file
    file_path = './log_0726_batch/test2/MoE_scores_20240726_230930.csv'
    df = pd.read_csv(file_path)

    # Filter and group the data
    filtered_df = df[(df[['Accuracy', 'Consistency', 'Readability', 'Conciseness']] != 0).all(axis=1)]
    grouped_df = filtered_df.groupby(['Model', 'Type']).mean()

    # Select the relevant columns
    score_means_by_type = grouped_df[['Accuracy', 'Consistency', 'Readability', 'Conciseness']]

    # Define a list of colors for each bar
    distinct_colors = generate_distinct_colors(len(score_means_by_type.unstack().columns))

    # Create subplots
    fig, axs = plt.subplots(2, 2, figsize=(20, 12), dpi=300)

    metrics = ['Accuracy', 'Consistency', 'Readability', 'Conciseness']
    ax_index = 0

    for metric in metrics:
        ax = axs[ax_index // 2, ax_index % 2]
        score_means_by_metric = score_means_by_type.unstack()[metric]
        bar_plot = score_means_by_metric.plot(kind='bar', ax=ax, color=distinct_colors, edgecolor='black', width=0.8)

        # Add data labels to bars
        for p in bar_plot.patches:
            ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=10)

        # Add average line
        for type in score_means_by_type.index.levels[1]:
            avg_value = score_means_by_type.loc[(slice(None), type), metric].mean()
            ax.axhline(y=avg_value, linestyle='--', linewidth=2, color='black', label=f'{metric} {type} Avg')

        ax.set_title(f'Average {metric} by Model and Type', fontsize=16)
        ax.set_xlabel('Model and Type', fontsize=14)
        ax.set_ylabel('Average Score', fontsize=14)
        ax.tick_params(axis='x', labelrotation=45, labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        ax.legend(loc='upper left', fontsize='small')

        ax_index += 1

    plt.tight_layout()
    plt.show()


def redar():
    # Load the CSV file
    file_path = './log_0726_batch/test2/MoE_scores_20240726_230930.csv'
    df = pd.read_csv(file_path)

    # Filter and group the data
    filtered_df = df[(df[['Accuracy', 'Consistency', 'Readability', 'Conciseness']] != 0).all(axis=1)]
    grouped_df = filtered_df.groupby(['Model', 'Type']).mean().reset_index()

    # Select the relevant columns
    score_means = grouped_df[['Model', 'Type', 'Accuracy', 'Consistency', 'Readability', 'Conciseness']]

    # Plotting the scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define colors for each type
    colors = {'basic info': 'red', 'morpho info': 'green', 'proj info': 'blue'}
    for type in score_means['Type'].unique():
        subset = score_means[score_means['Type'] == type]
        ax.scatter(subset['Accuracy'], subset['Consistency'], label=f'{type} (Acc vs Cons)', color=colors[type],
                   alpha=0.6)
        ax.scatter(subset['Accuracy'], subset['Readability'], label=f'{type} (Acc vs Read)', color=colors[type],
                   marker='x', alpha=0.6)
        ax.scatter(subset['Accuracy'], subset['Conciseness'], label=f'{type} (Acc vs Conc)', color=colors[type],
                   marker='*', alpha=0.6)

    ax.set_title('Scatter Plot of Scores by Model and Type')
    ax.set_xlabel('Accuracy')
    ax.set_ylabel('Scores')
    ax.legend(loc='best', fontsize='small')
    plt.tight_layout()

    # Show the plot
    plt.show()

def analyze_by_model_type_2():
    file_path = './log_0726_batch/test2/MoE_scores_20240726_230930.csv'
    df = pd.read_csv(file_path)

    # Filter and group the data
    filtered_df = df[(df[['Accuracy', 'Consistency', 'Readability', 'Conciseness']] != 0).all(axis=1)]
    grouped_df = filtered_df.groupby(['Model', 'Type']).mean().reset_index()

    # Pivot the data for better grouping in the plot
    pivot_df = grouped_df.pivot(index='Type', columns='Model',
                                values=['Accuracy', 'Consistency', 'Readability', 'Conciseness'])

    # Plotting the data with grouped bars for each metric
    fig, ax = plt.subplots(figsize=(20, 12))

    # Define colors for each model
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

    # Plot each metric in a single subplot
    pivot_df.plot(kind='bar', ax=ax, color=colors, width=0.8)

    # Customize the plot for better clarity
    ax.set_title('Scores by Type and Model', fontsize=20)
    ax.set_xlabel('Type', fontsize=16)
    ax.set_ylabel('Average Score', fontsize=16)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.legend(title='Model', fontsize=14, title_fontsize=16)
    ax.grid(True)

    # Save the figure at the highest resolution
    plt.tight_layout()
    # plt.savefig('./MoE/pic/', dpi=1200)
    plt.show()
if __name__ == '__main__':
    analyze_by_model_type()