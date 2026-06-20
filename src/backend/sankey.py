import plotly.graph_objects as go
import pandas as pd
import sankey_input
import math

# =========================
# 0. CONFIGURATION
# =========================
CHOSEN_TIERS = ["FR", "SR"] 

TIER_MAP = {
    "REF": sankey_input.REF_CLASSES,
    "FR": sankey_input.FR_CLASSES,
    "SR": sankey_input.SR_CLASSES
}

# 1. Load Data
df_raw = pd.DataFrame(
    sankey_input.REQUIREMENTS_DATA,
    columns=['source', 'target', 'value', 's_class', 't_class']
)

# 2. Filter Data
allowed_classes = []
for tier in CHOSEN_TIERS:
    allowed_classes.extend(list(TIER_MAP[tier].keys()))

df = df_raw[
    df_raw['s_class'].isin(allowed_classes) & 
    df_raw['t_class'].isin(allowed_classes)
].copy()
df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(1)

# 3. Metadata & Groups
node_metadata = {}
for _, row in df.iterrows():
    node_metadata[row['source']] = row['s_class']
    node_metadata[row['target']] = row['t_class']

tier_groups = []
for tier in CHOSEN_TIERS:
    classes = TIER_MAP[tier]
    nodes = sorted([n for n in node_metadata if node_metadata[n] in classes], key=lambda x: (node_metadata[x], x))
    if nodes: tier_groups.append(nodes)

sorted_nodes = [node for group in tier_groups for node in group]
node_dict = {name: i for i, name in enumerate(sorted_nodes)}

# 4. Sizes & Layout Calc
in_vals = df.groupby('target')['value'].sum().to_dict()
out_vals = df.groupby('source')['value'].sum().to_dict()
node_sizes = {n: max(max(in_vals.get(n, 0), out_vals.get(n, 0)), 1e-6) for n in sorted_nodes}

NODE_THICKNESS = 12   
NODE_PAD = 6          
max_nodes = max([len(g) for g in tier_groups]) if tier_groups else 0
FIG_HEIGHT = max(800, max_nodes * (NODE_THICKNESS + NODE_PAD) * 1.5)

# 5. Position Generator
def get_positions(node_list, x_pos):
    if not node_list: return [], []
    count = len(node_list)
    total_pixel = count * NODE_THICKNESS + (count - 1) * NODE_PAD
    node_total = (count * NODE_THICKNESS) / total_pixel
    pad_total = ((count - 1) * NODE_PAD) / total_pixel
    total_val = sum(node_sizes[n] for n in node_list)
    x_coords, y_coords, current_y = [x_pos] * count, [], 0.0
    for i, n in enumerate(node_list):
        frac = max((node_sizes[n] / total_val) * node_total, 0.0005)
        y_coords.append(min(current_y + frac / 2, 0.999))
        current_y += frac
        if i < count - 1: current_y += pad_total / (count - 1)
    return x_coords, y_coords

all_x, all_y = [], []
num_cols = len(tier_groups)
for i, group in enumerate(tier_groups):
    x_val = 0.01 + (i * (0.98 / (num_cols - 1))) if num_cols > 1 else 0.5
    gx, gy = get_positions(group, x_val)
    all_x.extend(gx); all_y.extend(gy)

# 6. Colors
node_colors = []
for n in sorted_nodes:
    cls = node_metadata.get(n)
    color = next((t[cls] for t in TIER_MAP.values() if cls in t), "rgba(180,180,180,0.8)")
    node_colors.append(color)

link_colors = []
for _, row in df.iterrows():
    s_cls = row['s_class']
    base = next((t[s_cls] for t in TIER_MAP.values() if s_cls in t), "rgba(200,200,200,0.8)")
    link_colors.append(base.replace("0.8", "0.25"))

# =========================
# 7. BUILD FIGURE
# =========================
fig = go.Figure()

fig.add_trace(go.Sankey(
    arrangement="fixed",
    node=dict(
        pad=NODE_PAD, thickness=NODE_THICKNESS, label=sorted_nodes,
        color=node_colors, x=all_x, y=all_y,
        line=dict(color="rgba(0,0,0,0.5)", width=0.5),
        hovertemplate='Node: %{label}<extra></extra>'
    ),
    link=dict(
        source=df['source'].map(node_dict), target=df['target'].map(node_dict),
        value=df['value'], color=link_colors,
        hovertemplate='From: %{source.label}<br>To: %{target.label}<extra></extra>'
    )
))

# 8. LEGEND (Horizontal)
for tier in CHOSEN_TIERS:
    # Adding a simple dash to separate tier groups in the horizontal legend
    for cls_name, color in TIER_MAP[tier].items():
        if cls_name in [node_metadata[n] for n in node_metadata]:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(size=10, color=color, symbol='square'),
                name=f"{tier}: {cls_name}",
                showlegend=True
            ))

# 9. CLEAN LAYOUT (No grid, no axes)
fig.update_layout(
    title_text=f"Requirements Traceability: {' → '.join(CHOSEN_TIERS)}",
    font=dict(size=10, color="black"),
    height=FIG_HEIGHT + 100, # Extra space for bottom legend
    margin=dict(l=50, r=50, t=80, b=150), 
    paper_bgcolor="white",
    plot_bgcolor="white",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.02, # Positioned below the diagram
        xanchor="center",
        x=0.5,
        title=None,
        bordercolor="rgba(0,0,0,0.2)",
        borderwidth=1
    )
)

# Explicitly hide axes and grid
fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)

fig.show()