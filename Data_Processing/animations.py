import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import matplotlib.colors as mcolors


color_scale = ['#398278', '#97af87', '#d3c668', '#db9e63', '#bf5b32']

cmap = mcolors.LinearSegmentedColormap.from_list("mycmap", color_scale)



df = pd.read_csv('Data_Processing/total_5_df.csv')
df['total_resources'].fillna(0, inplace=True)  # replace NaNs with 0
df['total_resources'] = df['total_resources'].apply(lambda x: max(0, x))
df['total_resources'] = df['total_resources'] + 1
df['total_resources'] = df['total_resources'] / df['total_resources'].max()
size_factor = 100  # Adjust this value as needed
df['total_resources'] = df['total_resources'] * size_factor

df['location_y'] = df['location_y'] * -1
df['location_y'] = df['location_y'] + 50

graph_extent_x = 52
graph_extent_y = 52

# Create a figure and axis objects
fig, ax = plt.subplots(figsize=(10, 10))

# Get unique frames
frames = df['tick'].unique()

# Function to update the scatter plot for each frame
def update(frame):
    ax.clear()
    ax.set_xlim([-2, graph_extent_x])
    ax.set_ylim([-2, graph_extent_y])
    df_frame = df[df['tick'] == frame]
    scatter = ax.scatter(df_frame['location_x'], df_frame['location_y'], 
                         s=df_frame['total_resources'].round(2), 
                         c=df_frame['deprivation_quintile'],
                         cmap=cmap,
                         vmin=1, vmax=5,  # set color scale range
                         alpha=0.6)  # set transparency)
    # for i in range(len(df_frame)):
    #     ax.text(df_frame['location_x'].iloc[i], df_frame['location_y'].iloc[i], 
    #             str(df_frame['age'].iloc[i]), ha='center', va='center',
    #             fontsize=8)  # adjust fontsize as needed
    ax.set_title(f"Tick: {frame}")
    return scatter,



ani = animation.FuncAnimation(fig, update, frames=frames, interval=600, blit=True)
ani.save('animation.mp4', writer='ffmpeg', fps=len(frames) / 240, dpi=300)

plt.show()