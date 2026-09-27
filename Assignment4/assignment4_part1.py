import torch
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader
from core import *
from util import mean_and_ci
from config import NUM_CLASSES
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr


# Load the data
dataset = SantoroDataset()
dataloader = DataLoader(dataset, batch_size=16, shuffle=False) # Keep shuffle=False to align with brain data
print(f"Loaded {len(dataset)} Santoro sounds.")

# Fix 1: Remove parentheses from brain_responses
brain_data = dataset.brain_responses
print(f"Brain data shape: {brain_data.shape}")

# Load YAMNet activations
yamnet_activations = load_yamnet_activations()
print(f"Loaded YAMNet activations for layers: {list(yamnet_activations.keys())}")

# Dictionaries to store lists of extracted activations for all runs
all_trained_activations = {"waveform": [], "uninspired": [], "inspired": []}
all_untrained_activations = {"waveform": [], "uninspired": [], "inspired": []}

# Path to the directory containing the model files
models_dir = Path("models") 

# Iterate through each model type independently and extract untrained weights
for model_name in ["waveform", "uninspired", "inspired"]:
    
    # Get all "best" trained runs for this specific model
    trained_files = list(models_dir.glob(f"{model_name}_run*_best.pt"))
    print(f"\nProcessing {model_name}: Found {len(trained_files)} trained runs.")
    
    # Process Trained Runs
    for pt_file in trained_files:
        trained_model = MODEL_CLASSES[model_name](num_classes=NUM_CLASSES)
        trained_model.load_state_dict(torch.load(pt_file, map_location=torch.device('cpu'), weights_only=True))

        trained_activations = extract_activations(dataloader, trained_model)
        all_trained_activations[model_name].append(trained_activations)

        # Process Untrained Model
        untrained_model = MODEL_CLASSES[model_name](num_classes=NUM_CLASSES)
        untrained_activations = extract_activations(dataloader, untrained_model)
        all_untrained_activations[model_name].append(untrained_activations)

print("\nFinished extracting all activations. Ready to compute RDMs!")

# ----- Calculate the RDMs for each model type and each run -----

# -- Functions to compute RDMs --
# Function to compute RDM using Euclidean distance
def compute_rdm_euclidean(patterns: np.ndarray) -> np.ndarray:
    """Computes the Euclidean-distance RDM for a set of representational patterns using a fast, vectorized approach."""
    # Convert to numpy if it's a PyTorch tensor
    if isinstance(patterns, torch.Tensor):
        patterns = patterns.numpy()
        
    # Flatten spatial/feature dimensions so the shape becomes (n_samples, n_features)
    n_samples = patterns.shape[0]
    patterns_flattened = patterns.reshape(n_samples, -1)
    
    # Vectorized Euclidean distance calculation using scipy. 
    # In the practical we used for-loops to calculate the RDM, but using scipy's pdist and squareform is much faster and more efficient.
    # Since we have to compute the RDM for many layers and runs, this is a very significant speedup for this assignment.
    distances = pdist(patterns_flattened, metric='euclidean')
    rdm = squareform(distances)
    
    return rdm

# Function to compute RDM using 1-Pearson correlation
def compute_rdm_1correlation(patterns: np.ndarray) -> np.ndarray:
    """Computes the 1-correlation RDM using a fast, vectorized approach."""
    # Convert to numpy if it's a PyTorch tensor
    if isinstance(patterns, torch.Tensor):
        patterns = patterns.numpy()
        
    # Flatten spatial/feature dimensions so the shape becomes (n_samples, n_features)
    n_samples = patterns.shape[0]
    patterns_flattened = patterns.reshape(n_samples, -1)
    
    # Vectorized 1-Pearson correlation across all 288 sounds simultaneously
    rdm = 1 - np.corrcoef(patterns_flattened)
    np.fill_diagonal(rdm, 0) # Ensure the diagonal is exactly 0
    
    return rdm

# Compute RDM for brain_data
print("\nComputing Brain RDM...")
brain_rdm_euclidean = compute_rdm_euclidean(brain_data) # Required for metric experiment baseline
brain_rdm_1correlation = compute_rdm_1correlation(brain_data)

# Compute RDMs for untrained models
print("Computing Untrained Models RDMs...")
untrained_rdms_1correlation = {"waveform": [], "uninspired": [], "inspired": []}

for model_name in ["waveform", "uninspired", "inspired"]:
    for run_acts in all_untrained_activations[model_name]:
        run_rdms = {}
        for layer_name, acts in run_acts.items():
            run_rdms[layer_name] = compute_rdm_1correlation(acts)
        untrained_rdms_1correlation[model_name].append(run_rdms)

# Compute RDMs for trained models
print("Computing Trained Models RDMs...")
trained_rdms_1correlation = {"waveform": [], "uninspired": [], "inspired": []}

for model_name in ["waveform", "uninspired", "inspired"]:
    for run_acts in all_trained_activations[model_name]:
        run_rdms = {}
        for layer_name, acts in run_acts.items():
            run_rdms[layer_name] = compute_rdm_1correlation(acts)
        trained_rdms_1correlation[model_name].append(run_rdms)

# Compute RDMs for YAMNet activations
print("Computing YAMNet RDMs...")
yamnet_rdms_euclidean = {} # Required for metric experiment baseline
yamnet_rdms_1correlation = {}

for layer_name, acts in yamnet_activations.items():
    yamnet_rdms_euclidean[layer_name] = compute_rdm_euclidean(acts) # ADDED: Required for metric experiment baseline
    yamnet_rdms_1correlation[layer_name] = compute_rdm_1correlation(acts)

print("All RDMs computed successfully!")


# ---------------------------------------------------------
# METRIC EXPERIMENTATION: YAMNET BASELINE
# ---------------------------------------------------------
print("\nRunning Metric Selection Experiment on YAMNet...")

def upper_triangle(rdm: np.ndarray) -> np.ndarray:
    """Extract the off-diagonal upper-triangular entries of an RDM as a 1D vector."""
    return rdm[np.triu_indices(rdm.shape[0], k=1)]

def compare_rdms_pcc(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    """Compare two RDMs via Pearson correlation of their upper-triangular entries."""
    rdm_a = upper_triangle(rdm_a)
    rdm_b = upper_triangle(rdm_b)
    return np.corrcoef(rdm_a, rdm_b)[0, 1]

def compare_rdms_spearman(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    """Compare two RDMs via Spearman correlation of their upper-triangular entries."""
    rdm_a = upper_triangle(rdm_a)
    rdm_b = upper_triangle(rdm_b)
    return spearmanr(rdm_a, rdm_b).correlation

# Matrix to store the peak alignment score for each combination
results_matrix = np.zeros((2, 2))
scoring_functions = [compare_rdms_pcc, compare_rdms_spearman]

# Euclidean RDM combinations
for j, score_func in enumerate(scoring_functions):
    layer_scores = []
    for layer_name, y_rdm in yamnet_rdms_euclidean.items():
        alignment = score_func(y_rdm, brain_rdm_euclidean) # CHANGED: Uses score_func directly
        layer_scores.append(alignment)
    # Store the peak score achieved by YAMNet for this combination
    results_matrix[0, j] = max(layer_scores)

# 2. 1-Correlation RDM combinations
for j, score_func in enumerate(scoring_functions):
    layer_scores = []
    for layer_name, y_rdm in yamnet_rdms_1correlation.items():
        alignment = score_func(y_rdm, brain_rdm_1correlation) # CHANGED: Uses score_func directly
        layer_scores.append(alignment)
    # Store the peak score achieved by YAMNet for this combination
    results_matrix[1, j] = max(layer_scores)

# Format and print the results as a clean table for the report
results_df = pd.DataFrame(
    results_matrix, 
    index=['Euclidean RDM', '1-Correlation RDM'], 
    columns=['Pearson Scoring', 'Spearman Scoring']
)

print("\n--- Peak YAMNet Alignment Across Metric Combinations ---")
print(results_df.round(4))
print("--------------------------------------------------------\n")


# ---------------------------------------------------------
# FINAL ANALYSIS: SCORES & PLOTS
# ---------------------------------------------------------
print("Scoring Custom Models & Generating Analysis Plots...")

models = ["waveform", "uninspired", "inspired"]
trained_layer_scores = {m: {} for m in models}
untrained_layer_scores = {m: {} for m in models}

# Score layers across all runs using Spearman
for model_name in models:
    layer_names = list(trained_rdms_1correlation[model_name][0].keys())
    
    for layer in layer_names:
        # Trained scores
        t_scores = [compare_rdms_spearman(run[layer], brain_rdm_1correlation) for run in trained_rdms_1correlation[model_name]]
        trained_layer_scores[model_name][layer] = np.array(t_scores)
        
        # Untrained scores
        u_scores = [compare_rdms_spearman(run[layer], brain_rdm_1correlation) for run in untrained_rdms_1correlation[model_name]]
        untrained_layer_scores[model_name][layer] = np.array(u_scores)

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
colors = {"waveform": "tab:blue", "uninspired": "tab:orange", "inspired": "tab:green"}

for ax, model_name in zip(axes, models):
    layer_names = list(trained_layer_scores[model_name].keys())
    x_positions = np.arange(len(layer_names))
    
    # Calculate Mean and CI
    t_means, t_cis = zip(*[mean_and_ci(trained_layer_scores[model_name][layer]) for layer in layer_names])
    u_means, u_cis = zip(*[mean_and_ci(untrained_layer_scores[model_name][layer]) for layer in layer_names])
    
    t_means, t_cis = np.array(t_means), np.array(t_cis)
    u_means, u_cis = np.array(u_means), np.array(u_cis)
    
    # Plot Untrained
    ax.plot(x_positions, u_means, color=colors[model_name], linestyle='--', label=f'{model_name} (Untrained)')
    ax.fill_between(x_positions, u_means - u_cis, u_means + u_cis, color=colors[model_name], alpha=0.1)

    # Plot Trained
    ax.plot(x_positions, t_means, color=colors[model_name], linestyle='-', label=f'{model_name} (Trained)')
    ax.fill_between(x_positions, t_means - t_cis, t_means + t_cis, color=colors[model_name], alpha=0.3)
    
    # Formatting
    ax.set_xticks(x_positions)
    ax.set_xticklabels(layer_names, rotation=45, ha="right")
    ax.set_title(f"{model_name.capitalize()} Model Alignment")
    ax.set_xlabel("Network Depth (Layers)")
    ax.grid(True, alpha=0.3)
    ax.legend()

axes[0].set_ylabel("Spearman Correlation (Alignment to STG)")
plt.tight_layout()
plt.show()