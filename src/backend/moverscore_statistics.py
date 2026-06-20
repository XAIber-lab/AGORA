import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generate_robustness_chart(uc1_csv, uc2_csv, output_prefix="MoverScore_Robustness_Analysis"):
    """
    Extracts MoverScore statistics from UC1 and UC2 evaluation results,
    generates a comparative bar plot, and saves the numerical summary to a text file.
    """
    
    # -----------------------------------------
    # 1. DATA EXTRACTION & STATISTICS
    # -----------------------------------------
    def get_stats(file_path):
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping.")
            return None
        
        df = pd.read_csv(file_path)
        # Calculate mean and sample standard deviation (ddof=1)
        stats = df.groupby('control_id')['mover_score'].agg(['mean', 'std']).to_dict('index')
        return stats

    stats_uc1 = get_stats(uc1_csv)
    stats_uc2 = get_stats(uc2_csv)

    if not stats_uc1 or not stats_uc2:
        print("Error: Could not load both datasets. Ensure filenames are correct.")
        return

    control_ids = sorted(list(set(stats_uc1.keys()) & set(stats_uc2.keys())))
    control_labels = [f"Control {cid}" for cid in control_ids]

    # -----------------------------------------
    # 2. GLOBAL PLOTTING CONFIGURATION
    # -----------------------------------------
    mpl.rcParams.update({
        'font.size': 14,
        'axes.labelsize': 16,
        'axes.titlesize': 18,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 20,
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white',
        'savefig.dpi': 600,
        'font.family': 'sans-serif'
    })

    fig, ax = plt.subplots(figsize=(14, 7))
    bar_positions = np.arange(len(control_ids))
    width = 0.35 

    # -----------------------------------------
    # 3. DRAWING THE COMPARISON
    # -----------------------------------------
    for i, cid in enumerate(control_ids):
        # UC1 Theme (Black)
        m1, s1 = stats_uc1[cid]['mean'], stats_uc1[cid]['std']
        ax.hlines(m1, i - width/2, i - width/2 + width, colors='black', linewidth=4, 
                  label='Mean T1' if i == 0 else None, zorder=3)
        ax.errorbar(i - width/2 + width/2, m1, yerr=s1, fmt='none', ecolor='black', 
                    elinewidth=2, capsize=8, label='SD T1' if i == 0 else None, zorder=2)

        # UC2 Theme (Dark Green)
        m2, s2 = stats_uc2[cid]['mean'], stats_uc2[cid]['std']
        ax.hlines(m2, i + width/2, i + width/2 + width, colors='darkgreen', linewidth=4, 
                  label='Mean T2' if i == 0 else None, zorder=3)
        ax.errorbar(i + width/2 + width/2, m2, yerr=s2, fmt='none', ecolor='darkgreen', 
                    elinewidth=2, capsize=8, label='SD T2' if i == 0 else None, zorder=2)

    # -----------------------------------------
    # 4. CHART FORMATTING & ANNOTATIONS
    # -----------------------------------------
    ax.set_xticks(bar_positions + width/4) 
    ax.set_xticklabels(control_labels)
    ax.set_ylabel('MoverScore', fontsize=16)
    ax.set_ylim(0, 1.1)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)

    # --- Updated Threshold Label Section ---
    # Shifted label_x_pos further to the left (e.g., 1.5 units from the right edge)
    label_x_pos = len(control_ids) - 0.75
    label_alpha = 0.6
    label_fontsize = 9

    # Perfect Similarity Threshold (0.90)
    ax.axhline(0.90, color='blue', linestyle=':', alpha=0.3, zorder=1)
    ax.text(label_x_pos, 0.91, 'Perfect', color='blue', alpha=label_alpha, 
            fontsize=label_fontsize, fontweight='bold', zorder=5)

    # Strong Similarity Threshold (0.70)
    ax.axhline(0.70, color='red', linestyle=':', alpha=0.3, zorder=1)
    ax.text(label_x_pos, 0.71, 'Strong', color='red', alpha=label_alpha, 
            fontsize=label_fontsize, fontweight='bold', zorder=5)

    # Moderate Similarity Threshold (0.55)
    ax.axhline(0.55, color='orange', linestyle=':', alpha=0.3, zorder=1)
    ax.text(label_x_pos, 0.56, 'Moderate', color='orange', alpha=label_alpha, 
            fontsize=label_fontsize, fontweight='bold', zorder=5)

    # Weak Similarity Label (< 0.55)
    ax.text(label_x_pos, 0.45, 'Weak', color='gray', alpha=label_alpha - 0.1, 
            fontsize=label_fontsize, fontweight='bold', zorder=5)

    ax.legend(loc="lower right", frameon=False, ncol=2)
    plt.tight_layout()

    # -----------------------------------------
    # 5. SAVE FILES (IMAGES & TEXT SUMMARY)
    # -----------------------------------------
    png_path = f"{output_prefix}.png"
    pdf_path = f"{output_prefix}.pdf"
    txt_path = f"{output_prefix}_summary.txt"
    
    plt.savefig(png_path, bbox_inches='tight', dpi=600)
    plt.savefig(pdf_path, bbox_inches='tight')
    
    # Generate the text summary content
    summary_lines = [
        "="*70,
        f"{'ROBUSTNESS ANALYSIS NUMERICAL SUMMARY':^70}",
        "="*70,
        f"{'Control ID':<12} | {'T1 Mean (±SD)':<22} | {'T2 Mean (±SD)':<22}",
        "-"*70
    ]
    
    for cid in control_ids:
        m1, s1 = stats_uc1[cid]['mean'], stats_uc1[cid]['std']
        m2, s2 = stats_uc2[cid]['mean'], stats_uc2[cid]['std']
        line = f"{cid:<12} | {m1:.4f} (±{s1:.4f})     | {m2:.4f} (±{s2:.4f})"
        summary_lines.append(line)
    
    summary_lines.append("="*70)
    summary_lines.append(f"Analysis generated using Temperature 1.0 datasets.")
    
    # Save text file
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    plt.show()

    # Output confirmation
    print("\n".join(summary_lines))
    print(f"\nSUCCESS: Results saved to {png_path}, {pdf_path}, and {txt_path}")


def main():
    # Update these filenames as needed
    UC1_RESULTS = "fact_check_stats_for_interpretation_UC1_temp1.csv"
    UC2_RESULTS = "fact_check_stats_for_interpretation_UC2_temp1.csv"
    
    generate_robustness_chart(
        uc1_csv=UC1_RESULTS,
        uc2_csv=UC2_RESULTS,
        output_prefix="MoverScore_Robustness_Comparison_Final"
    )

if __name__ == "__main__":
    main()