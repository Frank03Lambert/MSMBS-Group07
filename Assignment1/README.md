# SIRD epidemic model – analysis toolkit

This notebook builds on a basic SIR model by adding a **death (D)** compartment,
then uses it to explore how the recovery rate shapes an epidemic, to compare
scenarios, and to reason about interventions.

Everything is driven by three reusable functions:

| Function | What it does |
|----------|--------------|
| `sird_model` | The differential equations of the SIRD model (fed to the solver). |
| `run_sird_simulation` | Runs one simulation for a single set of parameters. |
| `analyze_recovery_rates` | Runs several simulations across recovery rates and returns a summary table. |

## Requirements

```
numpy
scipy
pandas
matplotlib
```

The analysis cells also use `display()`, which is provided automatically inside
Jupyter. If you run the exported `.py` outside a notebook, either add
`from IPython.display import display` or replace those calls with `print()`.

## The model

The state vector is `y = [S, I, R, D]`:

- **S** – susceptible
- **I** – infectious
- **R** – recovered
- **D** – deceased

The parameters are:

- **beta (β)** – transmission rate
- **gamma (γ)** – recovery rate (mean infectious period is `1 / (γ + μ)`)
- **mu (μ)** – mortality rate

The basic reproduction number is `R0 = β / (γ + μ)`.

## Functions

### `sird_model(y, t, beta, gamma, mu)`

The right-hand side of the SIRD system. You normally don't call this directly —
it's passed to `scipy.integrate.odeint`.

**Arguments**

- `y` – current state `[S, I, R, D]`
- `t` – time (required by the solver; not used in the equations)
- `beta`, `gamma`, `mu` – model parameters described above

**Returns** the four derivatives `(dS/dt, dI/dt, dR/dt, dD/dt)`.

### `run_sird_simulation(beta, gamma, mu, N=1000, I0=10, days=150, plot=True)`

Runs a single simulation and, optionally, plots the four curves.

**Arguments**

- `beta`, `gamma`, `mu` – model parameters
- `N` – total population (default 1000)
- `I0` – initial number of infected (default 10)
- `days` – number of days to simulate (default 150)
- `plot` – if `True`, draw the S/I/R/D curves; set `False` when you only need
  the returned arrays

**Returns** the tuple `(t, S, I, R, D)`, where each element is a NumPy array of
length `days`. Because time is built as `np.linspace(0, days - 1, days)`,
`t[i] == i`, so you can index the arrays by day directly.

**Example**

```python
t, S, I, R, D = run_sird_simulation(beta=0.4, gamma=0.1, mu=0.02,
                                    N=1000, I0=5, days=200)

peak_day = t[I.argmax()]
peak_infected = I.max()
total_deaths = D[-1]
```

Passing `plot=False` is the usual choice when the result feeds another
calculation or a combined figure.

### `analyze_recovery_rates(beta, mu, N, I0, simulation_days, gamma_values=(0.05, 0.1, 0.15, 0.2, 0.25))`

Runs one simulation per recovery rate, draws all the infectious curves on a
single figure, and returns a summary table.

**Arguments**

- `beta`, `mu` – transmission and mortality rates (held fixed across the sweep)
- `N` – total population
- `I0` – initial number of infected
- `simulation_days` – number of days to simulate
- `gamma_values` – iterable of recovery rates to test

**Returns** a `pandas.DataFrame` with one row per recovery rate and the columns:

| Column | Meaning |
|--------|---------|
| `gamma` | The recovery rate tested |
| `R0` | Basic reproduction number, `β / γ` |
| `peak_infected` | Highest number infected at once (`None` if the curve never rises) |
| `peak_day` | Day the peak occurred (`None` if there is no peak) |
| `total_deaths` | Deaths at the end of the simulation |

When a run never peaks (infections only decline from the start), the
`peak_infected` and `peak_day` cells are left empty rather than reporting a
false day-0 peak.

**Example**

```python
results = analyze_recovery_rates(beta=0.4, mu=0.02, N=1000, I0=5,
                                 simulation_days=200)
results          # summary table, one row per gamma
```

## Typical workflow

1. Use `run_sird_simulation` to look at one parameter set in detail.
2. Use `analyze_recovery_rates` to sweep several recovery rates and compare the
   resulting peaks and death tolls in one table and one figure.
3. Compare two parameter regimes (high vs. low transmission) by calling
   `analyze_recovery_rates` twice, as in Part 2 of the notebook.
4. For intervention analysis, call `run_sird_simulation` with a baseline gamma
   and an increased gamma and compare the resulting attack rate and deaths, as
   in Part 3.