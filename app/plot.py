import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import matplotlib
matplotlib.use("Agg") # Uses a non interactive backend
import matplotlib.pyplot as plt
import os

def generate_decay_plot(n0, lam, t_max, max_points=1000):
    if t_max < 0.1:
        t_max = 0.1  # Minimum range for visibility
    # Determine the number of points to plot: at least 100, up to 1000, with 50 points per time unit
    num_points = min(max_points, max(100, int(t_max * 500)))

    # Generate evenly spaced time values from 0 to t_max
    t_values = np.linspace(0, t_max, num_points)

    # Apply the radioactive decay formula: N(t) = N₀ · e^(–λt)
    n_values = n0 * np.exp(-lam * t_values)

    # Create a new Plotly figure
    fig = go.Figure()

    # Add a line trace representing the decay curve
    fig.add_trace(go.Scatter(
        x=t_values,
        y=n_values,
        mode='lines',
        name='N(t)',
        hovertemplate='Time: %{x:.2f}<br>Remaining: %{y:.2f}<extra></extra>'  # Custom tooltip format
    ))

    # Customize layout: titles, axis labels, style, and margins
    fig.update_layout(
        title="Radioactive Decay",
        xaxis_title="Time (t)",
        xaxis=dict(range=[0, t_max]),
        yaxis_title="Quantity (N)",
        yaxis=dict(range=[0, min(n0, 1e6)]),  # Limit y-axis to avoid extreme values
        template="plotly_white",              # Use a clean white theme
        margin=dict(l=40, r=40, t=40, b=40)   # Set consistent margins
    )

    # Return the figure as an embeddable HTML snippet (without full HTML wrapper)
    return pio.to_html(fig, full_html=False)


def generate_decay_plot_image(n0, lam, t_max, filename="static/plots/decay_plot.png"):
    if t_max < 0.1:
        t_max = 0.1  # Minimum range for visibility
    # Determine number of points: at least 100, up to 1000, with 50 points per time unit
    num_points = min(1000, max(100, int(t_max * 500)))

    # Generate time values and compute decay values
    t_values = np.linspace(0, t_max, num_points)
    n_values = n0 * np.exp(-lam * t_values)

    # Create a new figure with specified size (in inches)
    plt.figure(figsize=(6, 4))

    # Plot the decay curve with label and color
    plt.plot(t_values, n_values, label="N(t) = N₀·e⁻ˡᵗ", color="green")

    # Add axis labels and title
    plt.xlabel("Time (t)")
    plt.ylabel("Quantity (N)")
    plt.title("Radioactive Decay")

    # Enable grid and legend
    plt.grid(True)
    plt.legend()

    # Force x axis limits for visualization
    plt.xlim(0, t_max)
    
    # Limit y-axis to avoid extreme values
    plt.ylim(0, min(n0, 1e6))

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save the figure to the specified path with tight bounding box
    plt.savefig(filename, bbox_inches="tight")

    # Close the figure to free memory
    plt.close()

    # Return the absolute path of the saved image
    return os.path.abspath(filename)