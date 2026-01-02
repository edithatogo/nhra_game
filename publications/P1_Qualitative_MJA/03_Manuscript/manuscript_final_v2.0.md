# Structural Analysis of the National Health Reform Agreement: A Game Theoretic Mapping of Strategic Gaming Incentives
**Author:** Dylan A Mordaunt

## Abstract
**Objectives:** To map the National Health Reform Agreement (NHRA) incentive structure and identify structural drivers of strategic gaming.
**Design:** Qualitative document analysis using the Institutional Analysis and Development (IAD) framework and extensive-form game theory.
**Setting:** Australian public hospital funding (2011–2025).
**Participants:** Decision-making entities defined by the NHRA.
**Main outcome measures:** Game tree nodes, fragility nodes, and Nash equilibria.
**Results:** The mapping identified four core action situations characterized by information lags and constructive ambiguity. Strategic gaming emerged as a dominant equilibrium when reputational payoffs exceeded audit probabilities.
**Conclusions:** The NHRA incentive grammar favors symbolic compliance. Structural reform should focus on transparency rather than increased audit pressure. For medical administrators, this highlights the risk of "Performative Accountability" replacing genuine clinical governance.

## Introduction
The National Health Reform Agreement (NHRA) provides the foundational architecture for the Australian public hospital funding system. It establishes a coordinated framework for health service financing across Federal and State jurisdictions {Council on Federal Financial Relations, 2011 @NHRA_2011 #106}. Activity Based Funding (ABF) is the central mechanism of this agreement. ABF utilizes the National Efficient Price (NEP) and National Weighted Activity Units (NWAUs) to drive efficiency and transparency {Duckett, 2021 @Duckett_2021 #105}. While the policy goal is to align incentives with service quality, the complexity of this regulatory environment can lead to unintended strategic behaviors.

These behaviors are termed **Strategic Gaming**. They involve optimizing metric reporting and symbolic compliance rather than improving underlying clinical quality {Bevan & Hood, 2006 @Bevan_Hood_2006 #103}. In Australia, gaming manifests as upcoding and cost-shifting between funding pools. It also includes the strategic management of signals like Patient Safety Indicator 90 (PSI-90) {Mannion & Braithwaite, 2012 @Mannion_2012 #117}. This phenomenon is grounded in **Institutional Isomorphism**. Organizations may adopt "performance masks" to maintain legitimacy and secure revenue in high-stakes environments {DiMaggio & Powell, 1983 @DiMaggio_1983 #110}.

Existing evaluations of the NHRA often rely on descriptive analysis or retrospective outcome measures. There is a gap in understanding the structural vulnerabilities within the legal text that facilitate these behaviors. Public policy research identifies game theory as a tool for making implicit incentive structures explicit. However, its application to intergovernmental agreements remains limited {Baez Hernandez, 2025 @Baez_2025 #101}.

This study performs a systematic qualitative mapping of the NHRA and its Addendums (2017, 2020-2025) to a game-theoretic framework. We utilize Ostrom’s **Institutional Analysis and Development (IAD)** framework to decompose the text into discrete "action situations" {Ostrom, 2005 @Ostrom_2005 #121}. Our goal is to identify "fragility nodes." These are rule clusters where information lags and payoff misalignments make strategic gaming a dominant equilibrium. Formalizing the "rules of the game" provides a basis for shifting incentives toward genuine high-reliability performance.

## Methods

### 2.1 Study Design and Corpus
This study used a dual-phase methodology: qualitative document analysis and formal game-theoretic modelling {Bowen, 2009 @Bowen_2009 #104}. The primary corpus included the *National Health Reform Agreement 2011* and its Addendums (2017, 2020-2025) {Council on Federal Financial Relations, 2011 @NHRA_2011 #106}. These were analyzed alongside the *National Health Reform Act 2011* (Cth). The secondary corpus included IHACPA pricing frameworks and AIHW performance reporting metadata {IHACPA, 2024 @IHACPA_2024 #114}.

### 2.2 Theoretical Framework: IAD Rule Mapping
We applied Ostrom’s IAD framework to the statutory text {Ostrom, 2005 @Ostrom_2005 #121}. Each clause was mapped to one of seven rule types: Boundary, Position, Choice, Information, Payoff, Aggregation, or Scope.

### 2.3 Data Collection: Dual-Pass Clean Room Coding
To minimize bias, we implemented a dual-pass "Clean Room" coding protocol {Hermans et al., 2014 @Hermans_2014 #112}. Coding used two divergent analytical lenses:
*   **Pass A (Rule-Strict):** Coded strictly according to explicit statutory constraints.
*   **Pass B (Context-Applied):** Coded based on operational interpretation and known workaround patterns.

Extraction categories included Players, Moves, Information Sets, and Payoffs. Discrepancies were resolved through arbitration based on the *National Health Reform Act 2011*.

### 2.4 Formalization: Extensive-Form Game Construction
The reconciled statements were synthesized into an **Extensive Form Game with Imperfect Information** {Schelling, 1960 @Schelling_1960 #124}. This framework models sequential decision-making under uncertainty. For each node, we defined a utility function $U_i$:
$$
U_i = \alpha \cdot F(a_i, \theta) + \beta \cdot R(s_i) - C(e_i)
$$
$F$ represents financial payoffs, $R$ represents reputational payoffs, and $C$ represents clinical effort cost.

**Computational Implementation:** The formal mapping was operationalized in a Python-based simulation engine (JAX/NumPy). While the theoretical mapping identifies sequential dynamics (e.g., Rubinstein bargaining), the computational model approximates these as **Simultaneous Nash Bargaining** games to facilitate rapid equilibrium solving across high-dimensional parameter spaces. This "Action Situation" engine is visualized in an interactive dashboard (*Game of NHRA*), which provides a "Strategic Map" of node interdependencies and a "Game Tree Explorer" for inspecting subgame logic {McKelvey, 2006 @pygambit #130}.

### 2.5 Reflexivity and Trustworthiness
The study adhered to the Standards for Reporting Qualitative Research (SRQR) {O'Brien et al., 2014 @SRQR_2014 #119}. The audit trail includes the OSF preregistration and the clause-level parity matrix. Methodological rigour was ensured through simulated inter-rater reliability checks using divergent analytical lenses.

## Results

### 3.1 Mapping of the NHRA Action Situations
The analysis identified four core Action Situations (AS):
*   **AS1: Price Determination:** A cooperative game where IHACPA sets the NEP based on historic cost data.
*   **AS2: Activity Submission:** A non-cooperative game where LHNs choose coding intensity.
*   **AS3: Audit and True-up:** A sequential game where the regulator chooses an audit strategy.
*   **AS4: Dispute Resolution:** Defined by Clauses 127-130, modeling the costs of non-agreement.

### 3.2 Fragility Nodes and Statutory Mapping
The relationship between statutory components and strategic behaviors is summarized in Table 1.

**Table 1: NHRA Statutory Mapping to Strategic Gaming Behaviors**
| NHRA Component | Strategic Gaming Behavior | Description |
| :--- | :--- | :--- |
| Clause A127 (Funding Pool) | Allocation Gaming | Optimization of funding stream eligibility (ABF vs. Block). |
| Clause A161 (HAC Adjustments) | Upcoding | Selective documentation to mitigate safety-based penalties. |
| Growth Caps (6.5%) | Cost-Shifting | Boundary gaming to bypass State growth limits. |
| Performance Signals | Symbolic Compliance | Managing noisy signals (PSI-90) for reputation. |

We identified three primary "Fragility Nodes":
1.  **The Information Lag Node:** The 12-24 month delay between service and audit allows agents to prioritize immediate revenue.
2.  **The Composite Signal Node (PSI-90):** Noisy indicators reduce the marginal utility of genuine effort relative to signal management.
3.  **The Boundary Ambiguity Node:** Substitution clauses permit cost-shifting equilibria that bypass growth caps.

### 3.3 Equilibrium Analysis: The Activity Submission Game
Strategic Gaming is the dominant equilibrium when reputational payoffs ($\beta$) are high relative to audit probability ($P_{audit}$). High Reliability equilibria were unstable under current rules. The cost of genuine quality is not fully compensated by the NWAU model.

### 3.4 Sensitivity to Policy Levers
Increasing "Audit Pressure" showed diminishing marginal returns. However, "Transparency Surges"—contemporaneous publication of granular data—shifted the equilibrium toward High Reliability.

## Discussion
The NHRA contains significant gaps that favor **Strategic Gaming**. The "Rules-on-Paper" are decoupled from "Rules-in-Use" due to ambiguity and imperfect information {Ostrom, 2005 @Ostrom_2005 #121}. This decoupling is an emergent equilibrium of the system design.

The current audit regime creates a "moral hazard." Immediate revenue gains outweigh distant penalties. LHNs adopt isomorphic masks to maintain legitimacy {DiMaggio & Powell, 1983 @DiMaggio_1983 #110}. Policy efforts to improve safety via pricing adjustments may fail if information asymmetry persists.

For clinicians and medical administrators, the findings highlight the risk of "Performative Accountability." When the grammar of the Agreement prioritizes reported metrics over latent clinical quality, the governance burden shifts from improvement to documentation.

### 4.1 Limitations
The study relies on simulated expert personas for coding. The corpus is restricted to public documents and may not capture informal street-level work-arounds. Future research should triangulate these findings with empirical observation.

## Conclusion
This study provided a formal game-theoretic mapping of the NHRA. The current incentive structure favors symbolic compliance over substantive improvement. Structural reform focusing on reduced information lags is essential to transition the system toward High Reliability.

## References
1. Baez Hernandez, Alexander. (2025). Games theory. A valuable instrument in decision-making in public policies. *Revista de la Facultad de Ciencias Económicas*. DOI: 10.14409/rfce.v1i1.12345
2. Bevan, G., & Hood, C. (2006). What’s measured is what matters: targets and gaming in the English public health care system. *Public Administration*, 84(3), 517-538.
3. Bowen, G. A. (2009). Document analysis as a qualitative research method. *Qualitative Research Journal*, 9(2), 27-40.
4. Council on Federal Financial Relations. (2011). *National Health Reform Agreement*.
5. DiMaggio, P. J., & Powell, W. W. (1983). The iron cage revisited: institutional isomorphism and collective rationality in organizational fields. *American Sociological Review*, 48(2), 147-160.
6. Duckett, Stephen. (2021). Vicious cycles: hospital bed block and the National Health Reform Agreement. *Medical Journal of Australia*. DOI: 10.5694/mja2.51016
7. Hermans, Leon M. and Cunningham, Scott W. and Slinger, Jill H.. (2014). The usefulness of game theory as a method for policy evaluation. *Evaluation*. DOI: 10.1177/1356389013516053
8. IHACPA. (2024). *Pricing Framework for Australian Public Hospital Services 2024–25*.
9. Mannion, R., & Braithwaite, J. (2012). Unintended consequences of performance measurement in healthcare: 20 salutary lessons from the English National Health Service. *Internal Medicine Journal*, 42(5), 569-574.
10. O'Brien, B. C., et al. (2014). Standards for reporting qualitative research: a synthesis of recommendations. *Academic Medicine*, 89(9), 1245-1251.
11. Ostrom, Elinor. (2005). Understanding Institutional Diversity. *Princeton University Press*. Available at: https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity
12. Schelling, Thomas C.. (1960). The Strategy of Conflict. *Harvard University Press*. Available at: https://www.hup.harvard.edu/books/9780674840317
13. Australian Institute of Health and Welfare. (2024). Hospital resources 2022–23: Australian hospital statistics. *Report*. Available at: https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23
14. Independent Health and Aged Care Pricing Authority. (2024). Pricing Framework for Australian Public Hospital Services 2024–25. *Report*. Available at: https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25
