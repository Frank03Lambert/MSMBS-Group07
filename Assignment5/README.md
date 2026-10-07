# Assignment 5: Plant Tissue Simulations

**Authors:** Irina Kalmykova (I6365269), Kimi Knaider (I6367547), Frank Lambert (I6354310), Elias Loisel (I6359467), Noortje van Maldegem (I6374487)

**AI disclosures:** In this folder you can also find some files in which we explain how we used AI for this assignment.

## Objective

The objective of this assignment is to study how a pathogen spreads through plant tissue, using the Infection model in VirtualLeaf, a cell-based simulation framework for plant tissue. We simulated the infection, analysed how the chemical of the pathogen weakens the cell walls and diffuses between cells, varied the division threshold of the pathogen, and proposed a plant defense. The answers to the six questions are below.

## How to run

1. Download VirtualLeaf v2.2.1 from https://github.com/rmerks/VirtualLeaf2021/releases/tag/v2.2.1 (precompiled for Linux, macOS and Windows), or compile it from source with Qt as described in the VirtualLeaf README.
2. Start VirtualLeaf and choose **Infection** in the **Models** menu. This loads `pathogen_infection.xml`.
3. Start and stop the simulation with the spacebar. The simulated time is shown while it runs; we ran for 2 hours of simulated time.
4. Parameters such as `rel_cell_div_threshold` can be changed with **Options → Edit parameters**.
5. VirtualLeaf saves snapshots (`leaf.NNNNNN.xml` and `.pdf`, where NNNNNN is the simulated time in seconds) in a folder called `infection_growth`. This folder is created in the folder from which the program was started, which is often the home folder.

## Dependencies and notes

- VirtualLeaf v2.2.1. Qt 6 is only needed to compile it yourself. The precompiled macOS build contains an Intel binary, so on a Mac with Apple Silicon it needs Rosetta 2.
- The answers below are written results of the simulations. There is no code in this folder that has to be run. The short Python script that we used to read the XML snapshots is in `irina_kalmykova_ai_use_disclosure.md`.

## Question 1

We opened the Infection model, which loads pathogen_infection.xml, and ran it for 2 hours of simulated time. We took a screenshot at the start and then every 30 minutes.



<img width="221" height="214" alt="image" src="https://github.com/user-attachments/assets/1d131e12-afb5-4bf6-bdab-abcac59d7465" />
<img width="283" height="220" alt="image" src="https://github.com/user-attachments/assets/56b9a75f-32a7-4550-a0ca-c472a3242172" />
<img width="241" height="203" alt="image" src="https://github.com/user-attachments/assets/a95f9081-8b69-42d9-82eb-57116fcaa9a9" />
<img width="229" height="204" alt="image" src="https://github.com/user-attachments/assets/e10953df-fd7f-4cbc-a7c5-734ba856eaab" />
<img width="252" height="223" alt="image" src="https://github.com/user-attachments/assets/38cce174-1c26-4885-a510-7d0063c12109" />

At the start, the pathogen (the red cell) sits just outside the left edge of the tissue and none of the plant cells are infected yet. The healthy cells are light blue, and the cell files on the right side are green. As the simulation runs, the cells closest to the pathogen turn purple because the chemical produced by the pathogen diffuses into them. The infection first spreads along the outermost cell file on the left, the one in contact with the pathogen, from top to bottom, and then moves inward more slowly, one cell file at a time. After 2 hours, most of the first two cell files (roughly a quarter of the tissue) are purple and some cells in the third file are starting to change colour. The green cell files on the right are not affected at all.
The tissue also deforms. The pathogen keeps growing, so it takes up more space and pushes against the plant cells around it. Because the infected cells have weaker walls, they are deformed more easily and get squeezed, while cells further away mostly keep their shape. The cells also get rounder and the walls look thicker between 0 and 30 minutes, but this happens in the whole tissue, also far away from the pathogen, so it is only the tissue mechanics settling at the start. The deformation caused by the infection is local, around the pathogen.


## Question 2

In CellHouseKeeping, each plant cell first looks at its chemical concentration. This value is divided by 0.5 and capped at 1.2, which gives a sort of infection level. If this infection level is above 0.1 and the cell is not the pathogen, the stiffness of all its wall elements is set to 3 minus the infection level. If the level is 0.1 or lower, the cell just keeps the normal stiffness of 3. So the more chemical a cell has, the softer its walls get, and this relation is linear. Because of the cap at 1.2, the stiffness can never go lower than 1.8. Infected cells also lose their veto, which is relevant for question 5.
This matches what was explained in the lecture, where fungi and bacteria produce chemicals that weaken the plant cell wall to make it easier to infect the tissue.
The pathogen behaves differently in a few ways. Its own walls are never weakened, because the weakening rule skips cell type 2, so it always keeps a stiffness of 3. It is also the only cell that grows: every step its target area increases by 2, and when its area becomes larger than rel_cell_div_threshold times the base area, it divides. The base area is a reference value that is the same for all cells (1000 in pathogen_infection.xml), not the pathogen's own starting size, which is about 559. Finally, in CellDynamics the pathogen produces the chemical at a constant rate, while the plant cells only slowly degrade it. So the pathogen is the source of the chemical and the plant cells are the ones affected by it.


## Question 3

In CelltoCellTransport the chemical moves between neighbouring cells through passive diffusion, in a similar way to auxin in the exercise during the computer practical. The flux depends on the length of the wall, the diffusion coefficient and the difference in concentration between the two cells, with a small correction for the cell areas.
The difference with the auxin model is that the diffusion coefficient is not a fixed parameter. First, the function getLengthAndStiffness calculates the average stiffness of the wall between the two cells, weighted by the length of the wall elements and taking both sides of the wall into account. The diffusion coefficient is then 0.00001 divided by this average stiffness. This means that a softer wall lets the chemical pass through faster. If the stiffness is almost zero, the code just uses 0.00001 so it does not divide by a number close to zero.
This creates a feedback loop. When a cell receives the chemical, its walls become softer (as was also discussed in question 2). Softer walls give a higher diffusion coefficient, so the chemical moves faster through those walls into the next cells. These cells then also get softer walls and pass the chemical on even faster. Each step strengthens the next one, so this is a positive feedback loop, and the infection basically speeds up its own spread. It does not grow without limit, because the stiffness cannot go below 3 − 1.2 = 1.8. The diffusion coefficient therefore ranges from 0.00001/3 ≈ 3.3·10⁻⁶ (healthy wall) to 0.00001/1.8 ≈ 5.6·10⁻⁶ (fully weakened wall), so it can increase by at most a factor 3/1.8 ≈ 1.67. On top of that, plant cells degrade the chemical at a rate of 0.001 × their chemical level (which can be seen in the method called CellDynamics).
We can also check the sign of the loop with what we saw about feedback loops in the network biology lecture, where a loop is positive if it contains an even number of negative interactions. Here, more chemical lowers the stiffness (a negative interaction), and since the diffusion coefficient is 0.00001 divided by the stiffness, stiffness also has a negative effect on diffusion (a second negative interaction). Higher diffusion then increases the amount of chemical in the neighbouring cells (a positive interaction). Two negative interactions give a positive loop, which confirms what we described above. 

<img width="487" height="392" alt="image" src="https://github.com/user-attachments/assets/995d8200-7b89-4210-9ba1-03fc500ff686" />




Figure 1 : Sketch of the feedback loop between the chemical, the wall stiffness and the diffusion coefficient. 

Figure 1 was generated using Claude but we thought it is nice to have a sketch of the feedback loop to support our answer to question 3. See the AI disclosure for information about how we used AI for this assignment.



## Question 4

The pathogen divides when its area becomes larger than rel_cell_div_threshold times the base area, which is a fixed reference value of 1000 for all cells. The pathogen starts with a target area of about 559, and in each simulation step a pathogen cell's target area increases by 2. Since every step corresponds to 10 seconds (rd_dt = 10), a run of 2 hours is 720 steps, so the target area of a single undivided pathogen cell can only increase by about 1440, to a maximum of about 2000. We expected that a lower threshold would make the pathogen divide earlier and more often—causing the pathogen population to expand faster—and that having more pathogen cells would also make the infection spread faster through the plant tissue.

Run 1: rel_cell_div_threshold = 1. 

<img height="150" alt="Schermafbeelding 2026-10-07 om 20 43 56" src="https://github.com/user-attachments/assets/ad2075a6-36ea-4f1f-85c1-0a48833ee476" />
<img height="150" alt="3E4D0842-2E79-4059-B23F-A5F39EE031B0" src="https://github.com/user-attachments/assets/7ba7dfee-b217-4b31-9c82-765607121c44" />
<img height="150" alt="921FBDB6-F251-45AC-91E8-2F3606854D19" src="https://github.com/user-attachments/assets/dbc9746e-3256-4d48-b4c8-c8f2760063bd" />
<img height="150" alt="5ED89737-E415-4F1D-A7DD-6679014AC96D" src="https://github.com/user-attachments/assets/7cc5f6d2-0d06-4389-b1dd-f05bf613df38" />
<img height="150" alt="99787888-4D29-483A-909E-DA1D0268347F" src="https://github.com/user-attachments/assets/741f04ce-c5b6-4eb1-a735-f8de38f6b0c1" />






Run 2: rel_cell_div_threshold = 3.

<img height="150" alt="D1E8FEEC-FACB-4251-9DD4-88EF194A0BB1" src="https://github.com/user-attachments/assets/f827b98b-8e07-463a-a18e-d92ba4a6b152" />
<img height="150" alt="6B2B1F5E-9E91-47BD-B76F-E0622611F77D" src="https://github.com/user-attachments/assets/c7071e2f-ca5d-4196-a49f-fe6189cef194" />
<img height="150" alt="415906F7-79D0-48AB-B1F5-6DB5FA93ABFA" src="https://github.com/user-attachments/assets/9df97c3a-55f6-4007-b9e4-065de9923fc8" />
<img height="150" alt="A0409D31-8586-4F77-8B02-3750A93E956C" src="https://github.com/user-attachments/assets/902cdd88-f00e-4f62-bba3-d9705201fe2d" />
<img height="150" alt="B688D2F1-2245-4367-A698-8B988E5B6F2C" src="https://github.com/user-attachments/assets/d0d693e9-fd92-4c48-a827-8ba37ec3dd87" />


We also experimented with 2 other runs for which we will give the end result below (we did not put the entire runs in this document because otherwise we will have a bit too much screenshots in this section):


Run 3: rel_cell_div_threshold = 0.5.

<img height="150" alt="Scherm­afbeelding 2026-10-07 om 22 45 38" src="https://github.com/user-attachments/assets/f8d8de93-095c-4bd8-bb0b-eaa2fc34ed02" />

Run 4: rel_cell_div_threshold = 15.

<img height="150" alt="Scherm­afbeelding 2026-10-07 om 22 48 20" src="https://github.com/user-attachments/assets/4d121cbc-cb95-4081-a4d9-8aacc438102e" />






In our runs, the infected plant region looked almost the same after 2 hours for all thresholds we tried (0.5, 1, 3, and 15), covering the first three cell files and one cell in the fourth file, even though the pathogen population itself expanded at very different rates. This can be explained by the numbers above: with a threshold of 3 or higher the pathogen would need an area of at least 3000 to divide, which it cannot reach within 2 hours, so it never divides and raising the threshold has no effect at all. Even with the default value of 2, the pathogen barely reaches a target area of 2000 by the end of the run. Only with a threshold of 1 or lower (such as 1 and 0.5) can the pathogen divide within 2 hours, expanding the pathogen population from 1 cell to 2 and 7 cells, respectively.

**Effect on pathogen population vs. infection spread.** The threshold only decides at which area a pathogen cell divides. Before division, it does not change how fast an individual pathogen cell grows, because each cell's target area increases by a fixed 2 per step, whatever the threshold is (once a cell divides, however, each new daughter cell also increases its target area by 2 per step, accelerating total population area growth). The first division therefore comes after about (threshold × 1000 − 559) / 2 steps of 10 seconds: about 221 steps (37 minutes) for threshold 1, 721 steps (just after 2 hours) for threshold 2 and 1221 steps (about 3 hours 24 minutes) for threshold 3. These are the earliest possible moments, because the division check uses the actual area, which follows the target area with a delay. In the run with threshold 1 the pathogen indeed divided only after about 68 minutes, not after 37, because its actual area crossed 1000 only then. So in a 2-hour run thresholds 2, 3 and 15 all mean "no division", which is why these runs looked the same, and only thresholds of 1 or lower can lead to a division at all. In the output of the default run (threshold 2) the pathogen stays a single cell during the whole 2 hours (47 cells in every snapshot): its target area grows from 559 to 1999 as expected, but its actual area only reaches about 1600, so the division condition is never met. In the run with threshold 1 the pathogen population expanded to 2 cells at the end (48 cells in total), but the number of infected plant cells was 11, the same as in the default run at 2 hours. It reached 11 after 63 minutes, before the division, and did not increase after it. We also ran threshold 0.5. The pathogen starts with an actual area of about 552, which is already above 0.5 × 1000, so it divides right at the start and ends with 7 cells after 2 hours (53 cells in total). Even then the number of infected plant cells at 2 hours was again 11, and the spread was even slower in the first hour (6 infected cells after 60 minutes, against 10 or 11 in the other runs), likely because early divisions split the shared boundary with the host and cause the daughter cells to push against each other rather than wedging deeply into the epidermis. So while lowering the threshold below 2 strongly accelerates how fast the pathogen population expands (from 1 to 2 to 7 cells), having more pathogen cells did not make the infection spread faster through the host tissue. This suggests that the infection spread is mainly set by how fast the chemical diffuses through the cell walls (question 3), and not by the number of pathogen cells. To see an effect of raising the threshold above 2, we would need a much longer run, and to speed up tissue infection we would need a change to something that acts directly on the chemical or the walls, which is fixed in the model code.

Table 1: Summary of the five runs, based on the snapshots saved every 3 minutes. A plant cell is counted as infected when its chemical level is above 0.05, the level at which CellHouseKeeping starts to weaken its walls.


| Run | Threshold | First division | Pathogen cells at 2 h | Cells in total | Infected plant cells at 30 / 60 / 90 / 120 min |
|---|---|---|---|---|---|
| Default | 2 | none | 1 | 47 | 6 / 10 / 10 / 11 |
| Run 1 | 1 | about 68 min | 2 | 48 | 6 / 10 / 11 / 11 |
| Run 2 | 3 | none | 1 | 47 | 6 / 10 / 11 / 11 |
| Run 3 | 0.5 | within the first 3 min | 7 | 53 | 5 / 6 / 9 / 11 |
| Run 4 | 15 | none | 1 | 47 | 6 / 11 / 11 / 11 |


## Question 5

In the auxin model, which is the other model we worked with, all cells are treated the same way: no cell is ever prevented from rearranging its walls with its neighbours. The infection model is different, because it is the only model that uses the cell veto (SetCellVeto in CellHouseKeeping). With wall reconfiguration switched on (compatibility_level = 65535), wall elements can be moved from one cell to a neighbouring cell, so cells can gain or lose neighbours. Healthy cells set their veto to true, so their walls cannot be moved and they keep their neighbours. Cells that have been weakened by the pathogen's chemical set their veto to false, so only in the infected part of the tissue can walls shift and cells change neighbours. Whether a cell can change neighbours therefore depends on its state, which fits a pathogen pushing its way between weakened cells. In addition, the exchange of chemical between two neighbours depends on the wall they share: the diffusion coefficient is calculated from the stiffness of both cells' sides of that wall, while in the auxin model passive diffusion uses the same D for every pair of neighbours.


## Question 6

The idea of the defense is that a plant cell that detects a lot of the chemical makes its walls stiffer instead of letting them be weakened. This would go in CellHouseKeeping, in the part that handles the plant cells, right after the infection level is calculated. The defense check needs to happen before the existing weakening rule, otherwise the weakening would overwrite it. We would also need two new parameters, a defense threshold and a defense stiffness that is higher than the normal value of 3. The defense threshold has to lie between 0.1 and 1.2 on the scale of the infection level: the infection level is capped at 1.2, so a threshold of 1.2 or higher can never be exceeded and the defense would never switch on, and with a threshold of 0.1 or lower the defense would take over from the weakening rule completely, so the cells would never be weakened first.

Pseudocode for CellHouseKeeping:

```text
for each cell c:
    if c is the pathogen:
        grow and divide as before, keep stiffness 3
    else:
        level = chemical of c / 0.5, capped at 1.2
        
        if level > defense_threshold:
            set stiffness of all walls of c to defense_stiffness
            keep veto on
        else if level > 0.1:
            set stiffness of all walls of c to 3 - level
            turn veto off
        else:
            set stiffness of all walls of c to 3
            keep veto on
```

Optionally, in SetCellColor we could give defended cells a different colour so we can see where the defense is active. This adds a negative feedback. With the defense, more chemical in a cell leads to stiffer walls. Since the diffusion coefficient is 0.00001 divided by the stiffness, stiffer walls lower the diffusion, so the chemical spreads more slowly to the next cells. So more chemical now leads to less spreading, which works against the positive feedback from question 3. The defended cells could act like a barrier that slows down or even stops the infection. Counting the interactions in the same way as in question 3: more chemical now increases the stiffness (a positive interaction), stiffness still has a negative effect on the diffusion coefficient (a negative interaction), and higher diffusion still increases the chemical in the neighbouring cells (a positive interaction). There is only one negative interaction, so the loop is negative.
