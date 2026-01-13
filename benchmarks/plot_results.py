import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
RESULTS_FILE = "benchmarks/movingai_results.csv"
OUTPUT_DIR = "benchmarks/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_results():
    if not os.path.exists(RESULTS_FILE):
        print(f"Results file {RESULTS_FILE} not found.")
        return

    # Load Data
    df = pd.read_csv(RESULTS_FILE)
    
    # 1. Pivot to get Algorithms as columns
    # We keep full names like "Batch A* (k=20)"
    pivot = df.pivot(index='Map', columns='Algorithm', values='AvgTime(ms)')
    
    std_col = "Standard A* (k=1)"
    batch_best = "Batch A* (k=20)"
    
    # 1. Comparison Scatter Plot: Standard vs Best Batch
    if std_col in pivot.columns and batch_best in pivot.columns:
        plt.figure(figsize=(10, 8))
        plt.loglog(pivot[std_col], pivot[batch_best], 'o', alpha=0.6)
        
        # Diagonal line
        min_val = min(pivot[std_col].min(), pivot[batch_best].min())
        max_val = max(pivot[std_col].max(), pivot[batch_best].max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Equal Performance')
        
        plt.xlabel(f'{std_col} Time (ms)')
        plt.ylabel(f'{batch_best} Time (ms)')
        plt.title('Performance Comparison: Standard vs Best Batch (8-Way)')
        plt.legend()
        plt.grid(True, which="both", ls="-", alpha=0.2)
        
        plt.savefig(os.path.join(OUTPUT_DIR, "scatter_comparison.png"))
        plt.close()

    # 2. Box Plot of Speedups for all variants
    if std_col in pivot.columns:
        speedups = pd.DataFrame(index=pivot.index)
        for col in pivot.columns:
            if col != std_col:
                speedups[col] = pivot[std_col] / pivot[col]
        
        if not speedups.empty:
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=speedups)
            plt.axhline(y=1.0, color='r', linestyle='--')
            plt.ylabel('Speedup Factor (vs Standard A*)')
            plt.title('Speedup Distribution across all DAO Maps')
            plt.yscale('log')
            plt.xticks(rotation=15)
            plt.savefig(os.path.join(OUTPUT_DIR, "speedup_boxplot.png"))
            plt.close()

    # 3. Bar Chart for Top 10 Slowest Maps
    if std_col in pivot.columns:
        top_slowest = pivot.sort_values(std_col, ascending=False).head(10)
        # Select representative columns
        cols_to_plot = [std_col, "Batch A* (k=5)", "Batch A* (k=10)", "Batch A* (k=20)", "Adaptive A* (k=10)"]
        cols_to_plot = [c for c in cols_to_plot if c in top_slowest.columns]
        
        top_slowest[cols_to_plot].plot(kind='bar', figsize=(14, 7))
        plt.ylabel('Time (ms)')
        plt.title('Performance on 10 Hardest DAO Maps')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "slowest_maps_bar.png"))
        plt.close()

    # 4. Optimality Analysis
    pivot_opt = df.pivot(index='Map', columns='Algorithm', values='Optimality(%)')
    if std_col in pivot_opt.columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(pivot_opt[std_col], bins=20, kde=True)
        plt.xlabel('Optimality (%)')
        plt.title('Distribution of Path Optimality vs MovingAI Ground Truth')
        plt.axvline(x=100, color='g', linestyle='--', label='Perfect Match')
        plt.savefig(os.path.join(OUTPUT_DIR, "optimality_hist.png"))
        plt.close()

    # 5. K-Factor Median Speedup
    if std_col in pivot.columns:
        k_variants = ["Batch A* (k=5)", "Batch A* (k=10)", "Batch A* (k=20)"]
        k_variants = [v for v in k_variants if v in pivot.columns]
        
        median_speedups = {v: (pivot[std_col] / pivot[v]).median() for v in k_variants}
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(median_speedups.keys(), median_speedups.values(), color='skyblue')
        plt.axhline(y=1.0, color='r', linestyle='--', label='Standard A*')
        plt.ylabel('Median Speedup Factor')
        plt.title('Impact of Batch Size (K) on Performance (All Maps)')
        
        # Add labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f'{yval:.2f}x', ha='center', va='bottom')
            
        plt.savefig(os.path.join(OUTPUT_DIR, "k_factor_analysis.png"))
        plt.close()

if __name__ == "__main__":
    plot_results()