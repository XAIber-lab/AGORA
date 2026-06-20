
# --- Restore original barplot layout ---
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------
# 1. ENTER YOUR DATA HERE
# -----------------------------------------
controls_uc1_temp10 = {
    "Control 1": [3, 4, 4, 3, 3, 3, 2, 2, 4, 2],
    "Control 2": [2, 2, 2, 4, 3, 2, 4, 3, 3, 2],
    "Control 3": [3, 4, 4, 2, 2, 4, 4, 4, 3, 5],
    "Control 4": [5, 3, 3, 5, 4, 4, 3, 5, 3, 4],
    "Control 5": [4, 4, 4, 4, 3, 4, 4, 4, 4, 4],
    "Control 6": [3, 3, 3, 4, 3, 4, 2, 3, 3, 2],
    "Control 7": [5, 3, 3, 3, 3, 3, 4, 3, 3, 4],
}

controls_uc2_temp10= {
    "Control 1": [4, 4, 5, 4, 3, 4, 4, 3, 4, 5],
    "Control 2": [3, 4, 3, 3, 3, 3, 3, 3, 5, 4],
    "Control 3": [4, 5, 4, 5, 4, 3, 5, 4, 4, 4],
    "Control 4": [3, 4, 3, 2, 3, 3, 5, 2, 4, 4],
    "Control 5": [3, 4, 3, 3, 4, 3, 3, 4, 4, 4],
    "Control 6": [3, 3, 4, 3, 4, 3, 4, 2, 4, 2],
    "Control 7": [5, 4, 3, 3, 3, 4, 3, 3, 4, 4],
}

controls_uc1_temp05 = {
    "Control 1": [3, 4, 3, 5, 4, 4, 4, 3, 3, 4],
    "Control 2": [3, 4, 3, 5, 4, 4, 5, 3, 3, 4],
    "Control 3": [3, 3, 5, 4, 4, 5, 4, 4, 4, 5],
    "Control 4": [5, 3, 4, 5, 4, 5, 4, 3, 4, 5],
    "Control 5": [4, 4, 4, 3, 3, 4, 4, 3, 4, 4],
    "Control 6": [4, 3, 4, 3, 4, 4, 4, 4, 3, 4],
    "Control 7": [3, 3, 4, 3, 4, 4, 4, 4, 3, 4],
}

controls_uc2_temp05= {
    "Control 1": [4, 5, 3, 4, 5, 4, 3, 4, 4, 3],
    "Control 2": [4, 4, 4, 3, 4, 4, 4, 3, 3, 4],
    "Control 3": [4, 5, 3, 4, 4, 4, 3, 3, 5, 3],
    "Control 4": [3, 4, 4, 3, 3, 4, 4, 4, 2, 4],
    "Control 5": [4, 4, 4, 5, 3, 3, 4, 4, 4, 4],
    "Control 6": [3, 3, 3, 4, 3, 5, 4, 4, 4, 3],
    "Control 7": [3, 4, 3, 4, 4, 4, 3, 4, 4, 3],
}


# -----------------------------------------
# 3. CALCULATE MEAN AND STANDARD DEVIATION
# -----------------------------------------

# Calculate means and stds for both sets
means_uc1_temp10 = {}
stds_uc1_temp10 = {}
means_uc1_temp05 = {}
stds_uc1_temp05 = {}

for control in controls_uc1_temp10:
    arr = np.array(controls_uc1_temp10[control])
    means_uc1_temp10[control] = arr.mean()
    stds_uc1_temp10[control] = arr.std(ddof=1)
    arr2 = np.array(controls_uc1_temp05[control])
    means_uc1_temp05[control] = arr2.mean()
    stds_uc1_temp05[control] = arr2.std(ddof=1)

print("\n=== RESULTS UC1 TEMP10 ===")
for control in controls_uc1_temp10:
    print(f"{control}: mean = {means_uc1_temp10[control]:.4f}, std = {stds_uc1_temp10[control]:.4f}")
print("\n=== RESULTS UC1 TEMP05 ===")
for control in controls_uc1_temp05:
    print(f"{control}: mean = {means_uc1_temp05[control]:.4f}, std = {stds_uc1_temp05[control]:.4f}")


means_uc2_temp10 = {}
stds_uc2_temp10 = {}
means_uc2_temp05 = {}
stds_uc2_temp05 = {}

for control in controls_uc2_temp10:
    arr = np.array(controls_uc2_temp10[control])
    means_uc2_temp10[control] = arr.mean()
    stds_uc2_temp10[control] = arr.std(ddof=1)
    arr2 = np.array(controls_uc2_temp05[control])
    means_uc2_temp05[control] = arr2.mean()
    stds_uc2_temp05[control] = arr2.std(ddof=1)

print("\n=== RESULTS UC2 TEMP10 ===")
for control in controls_uc2_temp10:
    print(f"{control}: mean = {means_uc2_temp10[control]:.4f}, std = {stds_uc2_temp10[control]:.4f}")
print("\n=== RESULTS UC2 TEMP05 ===")
for control in controls_uc2_temp05:
    print(f"{control}: mean = {means_uc2_temp05[control]:.4f}, std = {stds_uc2_temp05[control]:.4f}")


# -----------------------------------------
# 4. PLOTTING + SAVE AS PNG
# -----------------------------------------
import matplotlib as mpl
mpl.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 13,
    'figure.titlesize': 20,
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.dpi': 600
})


# --- Mean and standard deviation for both sets ---
fig, ax = plt.subplots(figsize=(12, 6))
control_names = list(controls_uc1_temp10.keys())
bar_positions = np.arange(len(control_names))
width = 0.35

for i, control in enumerate(control_names):
    # UC1 TEMP10: left position
    ax.hlines(means_uc1_temp10[control], i-width/2, i-width/2+width, colors='black', linewidth=3, label='Mean T1 Temp1' if i==0 else None)
    ax.errorbar(i-width/2+width/2, means_uc1_temp10[control], yerr=stds_uc1_temp10[control], fmt='none', ecolor='black', elinewidth=2, capsize=8, label='SD T1 Temp1' if i==0 else None)
    # UC1 TEMP05: right position
    ax.hlines(means_uc1_temp05[control], i+width/2, i+width/2+width, colors='gray', linewidth=3, label='Mean T1 Temp05' if i==0 else None)
    ax.errorbar(i+width/2+width/2, means_uc1_temp05[control], yerr=stds_uc1_temp05[control], fmt='none', ecolor='gray', elinewidth=2, capsize=8, label='SD T1 Temp05' if i==0 else None)

ax.set_xticks(bar_positions)
ax.set_xticklabels(control_names, fontsize=12)
ax.set_ylabel('Relevance', fontsize=16)
ax.set_ylim(0, 5)
ax.set_yticks(np.arange(0, 5.5, 0.5))
ax.set_yticklabels(np.arange(0, 5.5, 0.5), fontsize=12)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
ax.legend(loc="lower right", frameon=False)

plt.tight_layout(rect=[0, 0.05, 1, 1])

# Save the plot as high-res PNG and PDF
output_filename_png = "control_statistics_uc1.png"
output_filename_pdf = "control_statistics_uc1.pdf"
plt.savefig(output_filename_png, dpi=600, bbox_inches='tight')
plt.savefig(output_filename_pdf, dpi=600, bbox_inches='tight')

plt.show()

print(f"\nPlot saved as '{output_filename_png}' and '{output_filename_pdf}'")

fig, ax = plt.subplots(figsize=(12, 6))
control_names = list(controls_uc2_temp10.keys())
bar_positions = np.arange(len(control_names))
width = 0.35

for i, control in enumerate(control_names):
    # UC2 TEMP10: left position
    ax.hlines(means_uc2_temp10[control], i-width/2, i-width/2+width, colors='darkgreen', linewidth=3, label='Mean T2 Temp1' if i==0 else None)
    ax.errorbar(i-width/2+width/2, means_uc2_temp10[control], yerr=stds_uc2_temp10[control], fmt='none', ecolor='green', elinewidth=2, capsize=8, label='SD T2 Temp1' if i==0 else None)
    # UC2 TEMP05: right position
    ax.hlines(means_uc2_temp05[control], i+width/2, i+width/2+width, colors='darkorange', linewidth=3, label='Mean T2 Temp05' if i==0 else None)
    ax.errorbar(i+width/2+width/2, means_uc2_temp05[control], yerr=stds_uc2_temp05[control], fmt='none', ecolor='darkorange', elinewidth=2, capsize=8, label='SD T2 Temp05' if i==0 else None)

ax.set_xticks(bar_positions)
ax.set_xticklabels(control_names, fontsize=12)
ax.set_ylabel('Relevance', fontsize=16)
ax.set_ylim(0, 5)
ax.set_yticks(np.arange(0, 5.5, 0.5))
ax.set_yticklabels(np.arange(0, 5.5, 0.5), fontsize=12)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
ax.legend(loc="lower right", frameon=False)

plt.tight_layout(rect=[0, 0.05, 1, 1])

# Save the plot as high-res PNG and PDF
output_filename_png = "control_statistics_uc2.png"
output_filename_pdf = "control_statistics_uc2.pdf"

plt.savefig(output_filename_png, dpi=600, bbox_inches='tight')
plt.savefig(output_filename_pdf, dpi=600, bbox_inches='tight')

plt.show()

print(f"\nPlot saved as '{output_filename_png}' and '{output_filename_pdf}'")

# --- Combined chart: all 4 values per control ---
fig, ax = plt.subplots(figsize=(14, 6))
control_names = list(controls_uc1_temp10.keys())
bar_positions = np.arange(len(control_names))
width = 0.18

for i, control in enumerate(control_names):
    # UC1 TEMP10
    ax.hlines(means_uc1_temp10[control], i-1.5*width, i-0.5*width, colors='black', linewidth=3, label='Mean T1 Temp1' if i==0 else None)
    ax.errorbar(i-width, means_uc1_temp10[control], yerr=stds_uc1_temp10[control], fmt='none', ecolor='black', elinewidth=2, capsize=8, label='SD T1 Temp1' if i==0 else None)
    # UC1 TEMP05
    ax.hlines(means_uc1_temp05[control], i-0.5*width, i+0.5*width, colors='gray', linewidth=3, label='Mean T1 Temp05' if i==0 else None)
    ax.errorbar(i, means_uc1_temp05[control], yerr=stds_uc1_temp05[control], fmt='none', ecolor='gray', elinewidth=2, capsize=8, label='SD T1 Temp05' if i==0 else None)
    # UC2 TEMP10
    ax.hlines(means_uc2_temp10[control], i+0.5*width, i+1.5*width, colors='darkgreen', linewidth=3, label='Mean T2 Temp1' if i==0 else None)
    ax.errorbar(i+width, means_uc2_temp10[control], yerr=stds_uc2_temp10[control], fmt='none', ecolor='darkgreen', elinewidth=2, capsize=8, label='SD T2 Temp1' if i==0 else None)
    # UC2 TEMP05
    ax.hlines(means_uc2_temp05[control], i+1.5*width, i+2.5*width, colors='darkorange', linewidth=3, label='Mean T2 Temp05' if i==0 else None)
    ax.errorbar(i+2*width, means_uc2_temp05[control], yerr=stds_uc2_temp05[control], fmt='none', ecolor='darkorange', elinewidth=2, capsize=8, label='SD T2 Temp05' if i==0 else None)

ax.set_xticks(bar_positions)
ax.set_xticklabels(control_names, fontsize=12)
ax.set_ylabel('Relevance', fontsize=16)
ax.set_ylim(0, 5)
ax.set_yticks(np.arange(0, 5.5, 0.5))
ax.set_yticklabels(np.arange(0, 5.5, 0.5), fontsize=12)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
ax.legend(loc="lower right", frameon=False)

plt.tight_layout(rect=[0, 0.05, 1, 1])

# Save the plot as high-res PNG and PDF
output_filename_png = "control_statistics.png"
output_filename_pdf = "control_statistics.pdf"
plt.savefig(output_filename_png, dpi=600, bbox_inches='tight')
plt.savefig(output_filename_pdf, dpi=600, bbox_inches='tight')

plt.show()

print(f"\nPlot saved as '{output_filename_png}' and '{output_filename_pdf}'")

