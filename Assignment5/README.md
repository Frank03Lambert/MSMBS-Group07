# Assignment 5

KEN3170 Plant Tissue Simulations: Assignment

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

The pathogen divides when its area becomes larger than rel_cell_div_threshold times the base area, which is a fixed reference value of 1000 for all cells. The pathogen starts with an area of about 559, and in each simulation step its target area increases by 2. Since every step corresponds to 10 seconds (rd_dt = 10), a run of 2 hours is 720 steps, so the target area of the pathogen can only increase by about 1440, to a maximum of about 2000. We expected that a lower threshold would make the pathogen divide earlier and more often, and that more pathogen cells would make the infection spread faster.

Run 1: rel_cell_div_threshold = 1. 


<img width="158" height="154" alt="image" src="https://github.com/user-attachments/assets/4a6661a9-570b-4ef5-b57a-0065d331fa15" />




Run 2: rel_cell_div_threshold = 3. 


<img width="195" height="189" alt="image" src="https://github.com/user-attachments/assets/685d9c7c-3fdc-4ef1-8de6-11004f4199eb" />





In our runs, the infected region looked almost the same for all thresholds we tried (1, 3 and also 15), covering roughly the first two cell files after 2 hours. This can be explained by the numbers above: with a threshold of 3 or higher the pathogen would need an area of at least 3000 to divide, which it cannot reach within 2 hours, so it never divides and the threshold has no effect at all. Even with the default value of 2, the pathogen barely reaches the required area of 2000 by the end of the run. Only with a threshold of 1 (area larger than 1000) can the pathogen divide within 2 hours. Even then, the spread of the infection did not visibly change, which suggests that within this time the spread is mainly limited by how fast the chemical diffuses through the plant cell walls and not by the number of pathogen cells. To see a clear effect of the threshold, the simulation would have to run much longer, so that the pathogen reaches the division threshold several times.

**Why changing the threshold did not help.** The threshold only decides at which area the pathogen divides. It does not change how fast the pathogen grows, because its target area increases by a fixed 2 per step, whatever the threshold is. The first division therefore comes after about (threshold × 1000 − 559) / 2 steps of 10 seconds: about 221 steps (37 minutes) for threshold 1, 721 steps (just after 2 hours) for threshold 2 and 1221 steps (about 3 hours 24 minutes) for threshold 3. These are the earliest possible moments, because the division check uses the actual area, which follows the target area with a delay. In the run with threshold 1 the pathogen indeed divided only after about 68 minutes, not after 37, because its actual area crossed 1000 only then. So in a 2-hour run thresholds 2, 3 and 15 all mean "no division", which is why these runs looked the same, and only threshold 1 can lead to a division at all. In the output of the default run (threshold 2) the pathogen stays a single cell during the whole 2 hours (47 cells in every snapshot): its target area grows from 559 to 1999 as expected, but its actual area only reaches about 1600, so the division condition is never met. In the run with threshold 1 the pathogen consisted of 2 cells at the end (48 cells in total), but the number of infected plant cells was 11, the same as in the default run at 2 hours. It reached 11 after 63 minutes, before the division, and did not increase after it. This suggests that the spread is mainly set by how fast the chemical diffuses through the cell walls (question 3), and not by the number of pathogen cells. The threshold was therefore not a useful parameter to vary here. To see an effect, we would need a much longer run or a change to something that acts directly on the chemical or the walls, which is fixed in the model code.


## Question 5

In the auxin model, which is the other model we worked with, all cells are treated the same way: no cell is ever prevented from rearranging its walls with its neighbours. The infection model is different, because it is the only model that uses the cell veto (SetCellVeto in CellHouseKeeping). With wall reconfiguration switched on (compatibility_level = 65535), wall elements can be moved from one cell to a neighbouring cell, so cells can gain or lose neighbours. Healthy cells set their veto to true, so their walls cannot be moved and they keep their neighbours. Cells that have been weakened by the pathogen's chemical set their veto to false, so only in the infected part of the tissue can walls shift and cells change neighbours. Whether a cell can change neighbours therefore depends on its state, which fits a pathogen pushing its way between weakened cells. In addition, the exchange of chemical between two neighbours depends on the wall they share: the diffusion coefficient is calculated from the stiffness of both cells' sides of that wall, while in the auxin model passive diffusion uses the same D for every pair of neighbours.


## Question 6

The idea of the defense is that a plant cell that detects a lot of the chemical makes its walls stiffer instead of letting them be weakened. This would go in CellHouseKeeping, in the part that handles the plant cells, right after the infection level is calculated. The defense check needs to happen before the existing weakening rule, otherwise the weakening would overwrite it. We would also need two new parameters, a defense threshold and a defense stiffness that is higher than the normal value of 3. The defense threshold has to lie between 0.1 and 1.2 on the scale of the infection level: the infection level is capped at 1.2, so a threshold of 1.2 or higher can never be exceeded and the defense would never switch on, and with a threshold of 0.1 or lower the defense would take over from the weakening rule completely, so the cells would never be weakened first.
Pseudocode for CellHouseKeeping:
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

Optionally, in SetCellColor we could give defended cells a different colour so we can see where the defense is active.
This adds a negative feedback. With the defense, more chemical in a cell leads to stiffer walls. Since the diffusion coefficient is 0.00001 divided by the stiffness, stiffer walls lower the diffusion, so the chemical spreads more slowly to the next cells. So more chemical now leads to less spreading, which works against the positive feedback from question 3. The defended cells could act like a barrier that slows down or even stops the infection.
Counting the interactions in the same way as in question 3: more chemical now increases the stiffness (a positive interaction), stiffness still has a negative effect on the diffusion coefficient (a negative interaction), and higher diffusion still increases the chemical in the neighbouring cells (a positive interaction). There is only one negative interaction, so the loop is negative.
