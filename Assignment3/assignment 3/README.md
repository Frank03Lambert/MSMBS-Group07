# Boolean Networks – Cancer-Causing Mutations

## Objective

The objective of this assignment is to study how mutations can affect the behavior of a simplified cell regulatory network using Boolean networks.

The model represents biological components as binary variables, where each node is either ON (1) or OFF (0). The network includes the following nodes:

- DNA_damage
- p53
- MYC
- CDK2
- MDM2
- p21
- Growth
- Death

Starting from the normal regulatory network developed during the practical, four mutations were introduced and compared with the normal network.

The mutations studied were:

- **Mutation A – p53 Knockout:** p53 is permanently OFF.
- **Mutation B – MYC Amplification:** MYC is permanently ON.
- **Mutation C – MDM2 Overexpression:** MDM2 is permanently ON.
- **Mutation D – p21 Knockout:** p21 is permanently OFF.

For each mutation, the three scenarios from the practical were tested:

1. Healthy Cell
2. Stressed Cell
3. Oncogene Hijacked Cell

Attractor analysis was also performed to study the long-term behavior of the network from all possible initial states.


## How to Run the Code

The analysis is contained in the Jupyter notebook included in this assignment folder.

### Requirements

The notebook uses Python and the following libraries:

- NumPy
- Matplotlib
- Seaborn
- itertools
- collections

A Jupyter environment such as JupyterLab can be used to run the notebook.

### Running the notebook

1. Open the notebook in JupyterLab.
2. Run the cells from top to bottom.
3. First run the cells defining the `BooleanNetwork` class and the normal regulatory network.
4. Run the practical sections to create and test the normal network.
5. Run each mutation section in order.
6. Run the scenario analysis and attractor analysis for each mutation.
7. Finally, restore the normal network and run the final verification.

The order of execution is important because the Boolean rules are modified when mutations are introduced.


## Boolean Network

The model uses Boolean rules to represent interactions between the different regulatory components.

Some important interactions are:

- DNA damage can activate p53.
- p53 activates p21.
- p21 inhibits cell-cycle progression.
- MYC promotes cell growth and activates MDM2.
- MDM2 inhibits p53.
- CDK2 and MYC contribute to cell growth.
- p53 and DNA damage can activate the cell-death response.

The model therefore contains several regulatory and feedback interactions that determine whether the final cell behavior is growth or death.


## Scenario Analysis

Three predefined initial conditions were tested for the normal network and each mutation.

### Healthy Cell

The healthy-cell scenario represents a cell without DNA damage.

### Stressed Cell

The stressed-cell scenario introduces DNA damage and tests whether the protective p53 pathway responds correctly.

### Oncogene Hijacked Cell

The oncogene-hijacked scenario begins with MYC active and represents abnormal activation of a growth-promoting pathway.

The final values of **Growth**, **Death**, and **p53** were recorded for each scenario.


## Attractor Analysis

An attractor represents a long-term behavior reached by the Boolean network.

Two types of attractors were considered:

- **Fixed point:** the network reaches a state that no longer changes.
- **Limit cycle:** the network repeatedly moves through the same sequence of states.

Because the network contains 8 Boolean nodes, there are:

`2^8 = 256`

possible initial states.

All 256 initial states were tested during the attractor analysis.

The **basin size** of an attractor represents the number of initial states that eventually lead to that attractor.

A state was considered cancer-like when the network showed continued growth despite the presence of DNA damage:

- Growth = 1
- Death = 0
- DNA_damage = 1


## Normal Network

The final verification of the normal network produced three fixed-point attractors.

- Normal growth without DNA damage: **128 states (50.0%)**
- Cell death following DNA damage: **120 states (46.9%)**
- Growth despite DNA damage: **8 states (3.1%)**

All **256/256 initial states** were accounted for.

The normal network therefore mainly leads either to normal growth or to a protective death response when DNA damage is present. A small cancer-like basin is also present in this simplified model.


## Mutation A – p53 Knockout

For Mutation A, p53 was permanently switched OFF:

`p53 = False`

This represents loss of the p53 tumor-suppressor function.

Without p53, the network loses an important mechanism responsible for responding to DNA damage. The scenario and attractor analyses were used to examine how this changes the balance between cell growth and cell death.


## Mutation B – MYC Amplification

For Mutation B, MYC was permanently switched ON:

`MYC = True`

This represents oncogene amplification.

Continuous MYC activity promotes the growth pathway and also affects MDM2, which interacts with the p53 pathway. The mutation therefore changes both growth signaling and the regulatory feedback of the network.


## Mutation C – MDM2 Overexpression

For Mutation C, MDM2 was permanently switched ON:

`MDM2 = True`

This represents MDM2 overexpression.

In the model, p53 follows the rule:

`p53 = DNA_damage AND (NOT MDM2)`

Therefore, permanent MDM2 activation prevents p53 from activating even when DNA damage is present.

In the scenario analysis, the stressed cell continued to grow instead of activating the normal protective response.


## Mutation D – p21 Knockout

For Mutation D, p21 was permanently switched OFF:

`p21 = False`

This represents loss of the cell-cycle inhibitor p21.

The complete attractor analysis identified **five attractors**:

- Attractor 1: fixed point – **50.0%**
- Attractor 2: 3-state limit cycle – **21.9%**
- Attractor 3: fixed point – **9.4%**
- Attractor 4: 3-state limit cycle – **15.6%**
- Attractor 5: fixed point – **3.1%**

The two 3-state limit cycles together account for **37.5%** of the initial states.

The cancer-like fixed point, where growth continues despite DNA damage, accounts for **3.1%** of the initial states.


## Which Mutation Is Most Dangerous?

The mutations can be compared quantitatively using the percentage of initial states that lead to cancer-like behavior.

The final conclusion should be based on the complete attractor analysis of Mutations A, B, C, and D, using the same definition of a cancer-like state:

`Growth = 1, Death = 0, DNA_damage = 1`

This ensures that the mutations are compared using the same criterion and all 256 possible initial states.

> **Note:** The final ranking should only be made after the complete fixed-point and limit-cycle analyses for Mutations A, B, and C have been verified.


## Role of Feedback Loops

Feedback loops are important because the state of one component can indirectly influence itself through other components.

One important pathway in this model is:

`MYC → MDM2 ┤ p53`

MYC activates MDM2, while MDM2 inhibits p53. Therefore, increased MYC activity can indirectly reduce the activity of the p53 tumor-suppressor pathway.

p53 also activates p21:

`p53 → p21`

p21 acts as a cell-cycle inhibitor and suppresses growth-related activity.

These interactions allow the network to switch between different long-term behaviors depending on DNA damage and oncogenic signals. Mutations that interrupt these regulatory relationships can change which attractors are reachable and the sizes of their basins.


## Limitations of the Boolean Network Model

### 1. Binary representation

Every biological component can only be ON or OFF. Real biological systems have continuous expression levels and different degrees of activation. The Boolean representation therefore simplifies the actual behavior of genes and proteins.

### 2. Simplified biological network

The model contains only eight nodes and a limited number of interactions. Real cell-cycle and cancer regulatory networks contain many more genes, proteins, signaling pathways, and environmental influences.

### 3. Simplified timing

The model assumes synchronous Boolean updates, meaning that all nodes are updated together at each time step. In real cells, biological processes occur at different speeds and are not perfectly synchronized.

Because of these limitations, the model should be interpreted as a simplified representation of regulatory behavior rather than a complete biological model of cancer.


## Notes

The attractor analysis initially identified only fixed points by checking whether two consecutive states were identical. A more complete analysis was later used to detect repeated states, allowing both fixed points and limit cycles to be identified.

This was particularly important for the p21 knockout, where two 3-state limit cycles were found.


## Files

- `BooleanModeling.ipynb` – Jupyter notebook containing the Boolean network implementation, simulations, mutation analysis, and attractor analysis.
- `README.md` – Documentation and interpretation of the assignment.