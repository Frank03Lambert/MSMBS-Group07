# Multiscale Modeling of Biological Systems: Assignment 4- Computational Neuroscience

**Authors:** Irina Kalmykova (I6365269), Kimi Knaider (I6367547), Frank Lambert (I6354310), Elias Loisel (I6359467), Noortje van Maldegem (I6374487)

**Course:** Multiscale Modeling of Biological Systems, Maastricht University

---

## Table of contents

1. [Objective](#1-objective)
2. [Repository contents](#2-repository-contents)
3. [Dependencies](#3-dependencies)
4. [Setup](#4-setup)
5. [Data and model checkpoints](#5-data-and-model-checkpoints)
6. [How to run the code](#6-how-to-run-the-code)
7. [The analysis pipeline](#7-the-analysis-pipeline)
8. [The biological model (Part II)](#8-the-biological-model-part-ii)
9. [Outputs](#9-outputs)
10. [Summary of main findings](#10-summary-of-main-findings)
11. [Notes, caveats and reproducibility](#11-notes-caveats-and-reproducibility)
12. [Use of AI / LLM tools](#12-use-of-ai--llm-tools)
13. [References and acknowledgements](#13-references-and-acknowledgements)

---

## 1. Objective

The assignment uses RSA to compare the representations of artificial neural networks with real brain data. The brain data are fMRI response estimates (betas) from **5521 STG voxels of a single participant**, recorded for **288 natural sounds** from the Santoro dataset. The sounds fall into six categories of 48 sounds each: speech, voice, animal, music, nature and tools. The STG is believed to represent intermediate acoustic-to-semantic sound representations.

The assignment answers questions about the effect of training models on both model performance and brain alignment, as well as whether a biologically more plausible model aligns also better with the brain and whether this model has a better performance on the task or not. We have written a very extensive and complete report in which we describe all our findings and results. So for further information about the goal of this assignment, what we actually did, and what our results are, we refer to the report.

The assignment was divided into two parts:

**Part I (core analysis)**

1. Build RDMs for the STG data, for every trainable layer of the **untrained** and **trained** versions of the three provided models (`WaveformModel`, `UninspiredModel`, `InspiredModel`), and for the 15 layers of the pretrained **YAMNet**.
2. Quantify model-to-brain alignment and analyse:
   - the effect of **training** (trained vs. untrained),
   - the effect of **architectural choices** (input representation, convolution, recurrence, activation function),
   - the effect of **layer depth** on alignment with the STG.
3. Visualize how layers separate the sound categories and compare this to the brain (we use non-metric MDS and cross-validated LDA instead of t-SNE, see [section 7](#7-the-analysis-pipeline)).

**Part II (bonus)**

4. Design, train and analyse our own biologically inspired auditory-cortex model (`BiologicalModel`). It is a CRNN that follows the human auditory pathway A1 → lateral/medial belt → parabelt → A4 → A5/STS. The same analysis as in Part I is run on it.

You can find the full report in the file:[`Multi-Scale_Modeling_of_Biological_Systems_Assignment4_report.pdf`](Multi-Scale_Modeling_of_Biological_Systems_Assignment4_report.pdf). The original task description is in [`Assignment_description.md`](Assignment_description.md).

---

## 2. Repository contents

### 2.1 Files in the repository root

| Path | Type | Description |
| --- | --- | --- |
| `Assignment4.ipynb` | Notebook | **Main deliverable.** The complete analysis: activation extraction, RDM construction, metric experiment, alignment plots, statistics (permutation tests, Holm correction, Welch CIs), loudness control, architecture and depth analyses, MDS/LDA visualizations. Writes CSVs to `results/` and figures to the working directory. |
| `Multi-Scale_Modeling_of_Biological_Systems_Assignment4_report.pdf` | Report | The final written report (introduction, methods, results, discussion, future work, conclusion). |
| `Assignment_description.md` | Doc | The provided description of the assignment. |
| `README.md` | Doc | This file. |
| `models.py` | Code | The model classes: `WaveformModel`, `UninspiredModel`, `InspiredModel` (provided) and `BiologicalModel` (our Part II model). |
| `core.py` | Code | Core helpers: `SantoroDataset` (288 sounds + STG betas), `ESC50Dataset` (training data), `extract_activations` (per-layer activations via forward hooks), `load_yamnet_activations` (YAMNet layers in Santoro order), and the `MODEL_CLASSES` registry (`waveform`, `uninspired`, `inspired`, `biological`). |
| `train.py` | Code | CLI training script for the models on ESC-50. Saves `*_best.pt` checkpoints and `*_history.json` logs into `models/`. |
| `util.py` | Code | Supporting functions: waveform loading and resampling, YAMNet filename mapping, device selection, the train/eval loop, checkpoint and history bookkeeping, `mean_and_ci`, and `plot_accuracy_history`. |
| `config.py` | Code | Central configuration: data paths, sample rate (8 kHz), 64 mel bins, 1 s snippets, 50 classes, and default training hyperparameters. |
| `pyproject.toml` | Config | Project metadata and dependency list (project name `ken3170`, Python >= 3.11). |
| `uv.lock` | Config | Fully pinned dependency lock file for [`uv`](https://docs.astral.sh/uv/). |

### 2.2 Folders in the repository

| Folder | Description |
| --- | --- |
| `data/` | All input data. Contents listed below. |
| `models/` | Trained model checkpoints and training histories. Contains five trained runs for each of the four model types (`waveform`, `uninspired`, `inspired`, `biological`), named `<model>_run<N>_best.pt` (best-validation-accuracy weights) and `<model>_run<N>_history.json` (per-epoch train/validation loss and accuracy). |
| `img/` | The image used by the assignment description. |
| `practical/` | The RSA code we wrote during the practical session, which served as the starting point for this assignment. |
| `results/` | Result files produced by the experiments (see [section 9](#9-outputs)). |
| `Use_of_LLM_disclosures/` | Disclosures describing how Irina Kalmykova and Noortje van Maldegem used AI / LLM tools for this assignmment (see [section 12](#12-use-of-ai--llm-tools)). |
| `__pycache__/` | Auto-generated Python bytecode cache. Safe to ignore or delete. |

### 2.3 Contents of `data/`

| Path | Description |
| --- | --- |
| `data/ESC50/audio/` | ESC-50 `.wav` clips (2000 clips, 5 s each, 50 classes). Used **only for training** the models. |
| `data/ESC50/meta/esc50.csv` | ESC-50 metadata (filename, fold, target). Fold 5 is held out for validation. |
| `data/santoro_sounds/` | The 288 Santoro et al. natural-sound stimuli, plus `Labels_288Sounds_ObjectSoundDescription.csv` (category labels and filenames, `;`-separated). |
| `data/yamnet_embeddings/` | Pre-extracted YAMNet activations as `.hdf5` files (one per sound, layers `layer01relu` … `layer14relu` and `embedding`). |
| `data/stg_betas_train.mat`, `data/stg_betas_test.mat` | STG fMRI betas (5521 voxels) for the two sound subsets (216 and 72 sounds). |
| `data/train_sound_keys.mat`, `data/test_sound_keys.mat` | Indices that map the two beta subsets back to the 288 sounds. `SantoroDataset` merges both and sorts them into ascending sound order. |

---

## 3. Dependencies

**Python:** >= 3.11

**Declared in `pyproject.toml`:**

| Package | Used for |
| --- | --- |
| `torch`, `torchaudio` | Models, training, mel-spectrograms, resampling |
| `numpy`, `scipy` | Numerics, RDMs (`pdist`/`squareform`), Spearman correlation, Procrustes |
| `h5py` | Reading `.mat` (HDF5-based) brain data and YAMNet `.hdf5` activations |
| `soundfile` | Reading `.wav` files |
| `matplotlib` | All plots |
| `rsatoolbox` | RSA toolbox (declared dependency; the notebook's RDM and statistics code is implemented by hand) |

**Also imported by `Assignment4.ipynb`:**

| Package | Used for |
| --- | --- |
| `pandas` | Result tables and CSV export |
| `scikit-learn` | Non-metric MDS, PCA, shrinkage LDA, stratified cross-validation |
| `jupyter` / `notebook` / `ipykernel` | Running the notebook |

`pandas` and `scikit-learn` are not listed in `pyproject.toml` but are pinned in `uv.lock` (they come in transitively through `rsatoolbox`). **Jupyter is not in the lock file** and must be installed separately (see below).

**Hardware:** a GPU is optional. `train.py` auto-detects CUDA or Apple MPS and otherwise falls back to the CPU. Extracting activations for the 288 sounds runs fast enough on a CPU.

---

## 4. Setup

### Option A: `uv` (recommended, reproduces the pinned environment)

```bash
# 1. install uv if needed: https://docs.astral.sh/uv/getting-started/installation/
# 2. from the repository root:
uv sync --no-install-project     # installs the pinned dependencies from uv.lock
uv pip install jupyter           # only needed to run the notebook
```

> `--no-install-project` is used because the `[tool.hatch.build.targets.wheel]` section in `pyproject.toml` still refers to an `assignment/` sub-folder layout. The code is meant to be run directly from the repository root and does not need to be installed as a package.

### Option B: plain `pip`

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install torch torchaudio numpy scipy h5py soundfile matplotlib rsatoolbox \
            pandas scikit-learn jupyter
```

---

## 5. Data and model checkpoints

Before running anything, make sure the folders from [section 2](#2-repository-contents) are in place:

- `data/` with all sub-folders and `.mat` files listed in [section 2.3](#23-contents-of-data),
- `models/` with the checkpoints (`<model>_run<N>_best.pt`).

The ESC-50 dataset can be re-downloaded from <https://github.com/karolpiczak/esc-50> if needed. It is only required if you want to (re)train models.

> **Run everything from the folder called Assignment4 in our repository.** The ESC-50 paths in `config.py` (`data/ESC50/...`) and the `models/` and `results/` paths used by the notebook are relative to the current working directory.

---

## 6. How to run the code

### 6.1 Reproduce the analysis (Part I + Part II evaluation)

```bash
jupyter notebook Assignment4.ipynb       # or: jupyter lab / open in VS Code
```

Then run **Kernel → Restart & Run All**. The notebook does the following in order:

1. Loads `SantoroDataset` and the YAMNet activations.
2. For each of the four model types, loads every `models/<model>_run*_best.pt` checkpoint and, for each one, builds a freshly initialized **untrained** twin. It then extracts activations for all trainable layers.
3. Computes 1 − correlation RDMs (and Euclidean RDMs for the metric experiment).
4. Runs the analyses listed in [section 7](#7-the-analysis-pipeline).
5. Writes the CSV tables to `results/` and the figures `mds_by_category.png`, `mds_by_sound_level.png` and `lda_by_category.png` to the working directory.

The notebook is self-contained once the data and checkpoints are in place. No command-line arguments are needed. The permutation tests use 1000 permutations and the MDS/LDA steps run several fits, so expect the full run to take several minutes on a laptop CPU.

### 6.2 Train the models (optional)

Checkpoints are already provided in `models/`. To retrain, for example, five runs of the biological model:

```bash
python train.py --models biological --n-models 5
```

Common variants:

```bash
# train all four model types, 5 independent runs each (what the report uses)
python train.py --n-models 5

# train only the provided baselines
python train.py --models waveform uninspired inspired --n-models 5

# choose the device explicitly
python train.py --models biological --n-models 5 --device cuda     # or mps / cpu

# also keep untrained (epoch 0) and intermediate checkpoints
python train.py --models biological --checkpoint-epochs 5 10
```

| Argument | Default | Meaning |
| --- | --- | --- |
| `--models` | all four | Which model types to train (`waveform`, `uninspired`, `inspired`, `biological`) |
| `--n-models` | `1` | Independently initialized runs per model type |
| `--epochs` | `10` | Training epochs |
| `--batch-size` | `16` | Batch size |
| `--lr` | `1e-3` | Adam learning rate |
| `--val-fold` | `5` | ESC-50 fold held out for validation (folds 1 to 4 are used for training) |
| `--checkpoint-epochs` | none | Epochs at which to additionally save checkpoints, which also saves the untrained epoch-0 weights |
| `--checkpoint-dir` | `models` | Where checkpoints and histories are written |
| `--audio-dir`, `--meta-csv` | `data/ESC50/...` | ESC-50 locations |
| `--num-workers` | `0` | DataLoader workers |
| `--device` | auto | `cuda`, `mps` or `cpu` |

Each run writes `<model>_run<N>_best.pt` (weights with the highest validation accuracy) and `<model>_run<N>_history.json`. Run ids count up automatically, so repeated calls never overwrite earlier runs. **If you retrain into a folder that already contains checkpoints, the new runs are added next to the old ones and the notebook will pick up all of them.** Use a fresh `--checkpoint-dir` (and point `models_dir` in the notebook at it) for a clean re-run.

---

## 7. The analysis pipeline

| Step | What is done | Where |
| --- | --- | --- |
| **Models** | 4 architectures × 5 trained runs, each paired with an independently initialized untrained model | `models.py`, `train.py` |
| **Activations** | Forward hooks return the output (after the non-linearity) of every trainable layer | `core.extract_activations` |
| **RDMs** | 1 − Pearson correlation between all sound pairs (spatial and feature dimensions flattened) | notebook |
| **Metric experiment** | Euclidean vs. 1 − correlation RDMs and Pearson vs. Spearman RDM comparison, evaluated on YAMNet as a sensitivity analysis. **Final choice: 1 − correlation RDMs compared with Spearman.** | notebook |
| **Alignment** | Spearman correlation of the upper triangles of model and brain RDMs, reported as mean with 95% CI (t-distribution over runs) | notebook |
| **Training effect** | Trained − untrained difference with Welch CIs. Two-sided label-permutation test with Holm correction across layers. | notebook |
| **Above-chance test** | Brain RDM rows and columns permuted 1000 times, one-sided, max-statistic correction across layers of each model and condition | notebook |
| **Waveform follow-up** | Two-sided brain-permutation test for anti-alignment | notebook |
| **Loudness control** | RDM of \|Δ log RMS\| between sounds, correlated with the brain and with every model layer | notebook |
| **Architecture comparison** | Per-run peak-layer and mean-over-layers alignment. Pairwise architecture-label permutation tests with Holm correction. | notebook |
| **Depth analysis** | Least-squares slope of alignment over relative depth, tested against the brain permutation null (Holm-corrected), plus peak-depth estimates | notebook |
| **Seed consistency** | Mean Spearman correlation between RDMs of different runs of the same layer | notebook |
| **Category visualization** | Non-metric MDS of the 1 − correlation RDMs, Procrustes-aligned to the STG map, coloured by category and by sound level. Cross-validated shrinkage LDA (PCA to 30 components, 5-fold balanced accuracy) for linear category read-out. | notebook |

The assignment allows "t-SNE or something similar". We used non-metric MDS on the very RDMs that are compared in the RSA. The maps therefore show exactly the geometry entering the Spearman comparison, and non-metric MDS preserves only rank order, matching the Spearman assumption. LDA complements it by testing whether category information is linearly readable even when it does not dominate the geometry.

---

## 8. The biological model (Part II)

`BiologicalModel` in `models.py` is a convolutional-recurrent network whose stages are mapped to regions of the human auditory pathway. The regions were chosen from the HCP-MMP1.0 atlas and human effective-connectivity literature (see the report).

```
mel-spectrogram (1 x 64 x T)
   └─ A1      Conv(1→32)  + LRN + ReLU6 + MaxPool(2,2)
        ├─ LBelt  Conv(32→32) + LRN + ReLU6 + MaxPool(2,1)
        └─ MBelt  Conv(32→32) + LRN + ReLU6 + MaxPool(2,1)      (parallel branches)
             └─ concat (64 ch) → PBelt  Conv(64→64) + LRN + ReLU6 + MaxPool(2,1)
                  └─ A4     Conv(64→128) + LRN + ReLU6 + MaxPool(2,1)
                       └─ mean over frequency → A5/STS  2-layer bidirectional GRU (128 hidden)
                            └─ Linear(256 → 50 classes)
```

Biologically motivated design choices:

- **ReLU6** everywhere: a lower bound of zero (no negative firing) and an upper bound (a maximum firing rate).
- **Local Response Normalization** instead of batch norm, as a model of lateral inhibition (AlexNet hyperparameters; window 3 in narrow layers, 5 in wide layers).
- **Asymmetric pooling**: after A1, pooling only over frequency, which broadens spectral tuning while preserving the temporal resolution needed by the GRU.
- **Capacity scaling**: 32 → 64 → 128 channels with depth.
- **Parallel L/M-belt streams** merged in the parabelt.
- **Bidirectional recurrence** for temporal integration in A5/STS.

The model is registered as `"biological"` in `core.MODEL_CLASSES`, so `train.py` and the notebook handle it like the other three. In depth plots, the two parallel belt branches share one relative-depth position.

---

## 9. Outputs

**CSV tables written to `results/` by the notebook**

| File | Content |
| --- | --- |
| `training_effect_per_layer.csv` | Per model and layer: trained/untrained alignment with 95% CIs, Δ (trained − untrained) with Welch CI, seed consistency, and (after the permutation cell) p-values |
| `peak_alignment.csv` | Best layer and peak alignment per model and condition, plus YAMNet |
| `architecture_scores.csv` | Peak and mean-over-layers alignment per architecture and condition, with CIs |
| `architecture_comparisons.csv` | Pairwise architecture differences, CIs, raw and Holm-corrected p-values |
| `depth_trend.csv` | Depth slopes, peak depths and their CIs and p-values per model and condition |

**Figures**

| File | Content |
| --- | --- |
| `mds_by_category.png` | Non-metric MDS maps (first / peak / last layer per trained model, STG, YAMNet), coloured by sound category |
| `mds_by_sound_level.png` | The same maps coloured by sound level (log RMS) |
| `lda_by_category.png` | Cross-validated LDA projections with held-out balanced accuracy |
| `img/training_history.png` | Train/validation accuracy per model type (`util.plot_accuracy_history`) |

The alignment-by-layer plots (report Figures 1 and 2) are drawn inline in the notebook.

---

## 10. Main findings

See our report for all our findings.

---

## 11. Notes, caveats and reproducibility

- **Run from the repository root.** Several paths in `config.py` and the notebook are relative.
- **Do not shuffle the Santoro dataloader.** `SantoroDataset` returns sounds in the same order as the brain responses and the YAMNet activations, and all RDM comparisons rely on that alignment.
- **Untrained models are not seeded.** The notebook builds one freshly initialized untrained twin per trained run and sets no global random seed. Numbers for the untrained condition, and hence Δ and related p-values, can therefore differ slightly between executions. The brain permutation tests use a fixed seed (`seed=0`), and the MDS/LDA seeds are fixed in their helper functions.
- **Trained weights** are the best-validation-accuracy checkpoint (`*_best.pt`), not necessarily the final epoch.
- **Test resolution.** With 5 runs per condition, the smallest attainable corrected p-value for label-permutation tests is about 0.04 to 0.056, depending on the number of layers. Significant results therefore sit at the floor of the test.
- **Sample rate.** Waveforms are resampled to 8 kHz. Mel-spectrograms use 64 mel bins on 1 s snippets. ESC-50 training uses a random 1 s crop per access (data augmentation), while the Santoro sounds are cropped or zero-padded to 1 s.
- **Model-specific input.** `extract_activations` automatically feeds raw waveforms to `WaveformModel` and spectrograms to all other models.
- **Hemisphere.** The dataset does not specify the hemisphere of the STG voxels.

---

## 12. Use of AI / LLM tools

Disclosures about how AI / LLM tools were used in this project are in [`Use_of_LLM_disclosures/`](Use_of_LLM_disclosures/).

---

## 13. References and acknowledgements

You can find the complete reference list is in the report. The assignment framework (`core.py`, `models.py`, `train.py`, `util.py`, `config.py` and the data and pretrained checkpoints) was provided by the course instructor (Tonio Weidler, Maastricht University). `BiologicalModel` in models.py and the analysis in `Assignment4.ipynb` are our own work.
