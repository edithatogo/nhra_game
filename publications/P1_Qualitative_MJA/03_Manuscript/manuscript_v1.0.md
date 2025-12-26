# Structural Analysis of the National Health Reform Agreement: A Game Theoretic Mapping of Strategic Gaming Incentives
**Author:** Dylan A Mordaunt

## Abstract
**Objectives:** To map the National Health Reform Agreement (NHRA) incentive structure and identify structural drivers of strategic gaming.
**Design:** Qualitative document analysis using the Institutional Analysis and Development (IAD) framework and extensive-form game theory.
**Setting:** Australian public hospital funding (2011–2025).
**Participants:** Decision-making entities defined by the NHRA.
**Main outcome measures:** Game tree nodes, fragility nodes, and Nash equilibria.
**Results:** [Drafting...]
**Conclusions:** [Drafting...]

## Introduction
The National Health Reform Agreement (NHRA) represents the foundational architecture of the Australian public hospital funding system, establishing a coordinated framework for the financing and delivery of health services across Federal and State jurisdictions {Council on Federal Financial Relations, 2011 @NHRA_2011 #106}. Central to this agreement is the mechanism of Activity Based Funding (ABF), which utilizes the National Efficient Price (NEP) and National Weighted Activity Units (NWAUs) to drive systemic efficiency and transparency {Duckett, 2021 @Duckett_2021 #105}. While the primary policy objective of ABF is to align financial incentives with service volume and quality, the complexity of the resulting regulatory environment frequently gives rise to unintended strategic behaviors among healthcare providers and jurisdictions.

These behaviors, characterized in the literature as **Strategic Gaming**, involve the systematic optimization of metric reporting and symbolic compliance rather than substantive improvements in clinical quality or latent system performance {Bevan & Hood, 2006 @Bevan_Hood_2006 #103}. In the Australian context, such gaming manifests as upcoding, cost-shifting between funding pools, and the strategic management of performance signals like Patient Safety Indicator 90 (PSI-90) and Hospital Acquired Complications (HACs) {Mannion & Braithwaite, 2012 @Mannion_2012 #117}. Sociologically, this phenomenon is grounded in **Institutional Isomorphism**, where organizations adopt "performance masks" to maintain legitimacy and secure maximum revenue in high-stakes regulatory environments {DiMaggio & Powell, 1983 @DiMaggio_1983 #110}.

Despite the pervasive nature of these strategic interactions, existing evaluations of the NHRA often rely on descriptive policy analysis or retrospective econometric outcome measures. There remains a critical gap in understanding the structural vulnerabilities within the legal and statutory text of the Agreement itself that facilitate these behaviors. Public policy research has increasingly identified game theory as a valuable instrument for making these implicit incentive structures explicit, yet its application to the formal mapping of intergovernmental agreements is limited {Baez Hernandez, 2025 @Baez_2025 #101}.

This study addresses this gap by performing a systematic qualitative mapping of the NHRA and its subsequent Addendums (2017, 2020-2025) to a rigorous game-theoretic framework. Utilizing Elinor Ostrom’s **Institutional Analysis and Development (IAD)** framework, we decompose the statutory text into discrete "action situations" to construct an extensive-form game with imperfect information {Ostrom, 2005 @Ostrom_2005 #121}. The primary objective is to identify "fragility nodes"—specific rule clusters where information lags, constructive ambiguity, and payoff misalignments make strategic gaming a mathematically dominant equilibrium response. By formalizing the "rules of the game," this analysis provides a structural basis for future policy reforms aimed at shifting incentives from symbolic compliance toward genuine high-reliability performance.

## Methods

### 2.1 Study Design and Corpus
This study utilized a dual-phase methodology comprising qualitative document analysis followed by formal game-theoretic formalization {Bowen, 2009 @Bowen_2009 #104}. The primary corpus consisted of the foundational *National Health Reform Agreement 2011* and its subsequent Addendums (2017, 2020-2025) {Council on Federal Financial Relations, 2011 @NHRA_2011 #106}. To ensure statutory accuracy, these were analyzed in conjunction with the *National Health Reform Act 2011* (Cth). The secondary corpus included operational pricing frameworks and determination reports from the Independent Health and Aged Care Pricing Authority (IHACPA) and performance reporting metadata from the Australian Institute of Health and Welfare (AIHW) {IHACPA, 2024 @IHACPA_2024 #114}.

### 2.2 Theoretical Framework: IAD Rule Mapping
We applied Ostrom’s IAD framework to decompose the statutory text into a structured institutional grammar {Ostrom, 2005 @Ostrom_2005 #121}. Each clause was mapped to one of seven universal rule types:
1.  **Boundary Rules:** Defining eligibility for the health funding pool.
2.  **Position Rules:** Establishing roles such as the National Health Funding Pool Administrator.
3.  **Choice Rules:** Specifying permissible strategic actions (e.g., data submission, audit response).
4.  **Information Rules:** Dictating transparency requirements and reporting lags.
5.  **Payoff Rules:** The ABF financial formulae and safety-based penalty adjustments.
6.  **Aggregation Rules:** Logic for State-level growth caps.
7.  **Scope Rules:** Geographical and service-type boundaries of the Agreement.

### 2.3 Data Collection: Dual-Pass Clean Room Coding
To minimize single-lens bias and identify the gap between formal rules and operational realities, we implemented a dual-pass "Clean Room" coding protocol {Hermans et al., 2014 @Hermans_2014 #112}. Coding was performed through two divergent analytical lenses:
*   **Pass A (Rule-Strict):** Coded strictly according to the explicit statutory constraints and mandatory requirements.
*   **Pass B (Context-Applied):** Coded based on operational policy interpretation and known historical "work-around" patterns identified in the secondary corpus.

Extraction categories included Players (decision-making entities), Moves (available actions), Information Sets (what a player knows at a given node), and Payoffs (financial and reputational utility). Discrepancies between passes were resolved through systematic arbitration based on the legal primacy of the *National Health Reform Act 2011*.

### 2.4 Formalization: Extensive-Form Game Construction
The reconciled rule statements were synthesized into an **Extensive Form Game with Imperfect Information** {Schelling, 1960 @Schelling_1960 #124}. This framework was selected for its capacity to model sequential decision-making in environments characterized by information asymmetry and time lags (e.g., the delay between hospital data submission and regulatory audit). For each decision node, we defined a player-specific utility function $U_i$:
$$U_i = \alpha \cdot F(a_i, \theta) + \beta \cdot R(s_i) - C(e_i)$$
Where $F$ represents financial payoffs (NWAU revenue), $R$ represents reputational payoffs (performance ranking visibility), and $C$ represents the cost of genuine clinical effort ($e_i$). The resulting game trees were validated for logical closure and analyzed for Nash and Subgame Perfect Equilibria using the NHRA Game Theory Model.

### 2.5 Reflexivity and Trustworthiness
Methodological rigor was maintained by adhering to the Standards for Reporting Qualitative Research (SRQR) {O'Brien et al., 2014 @SRQR_2014 #119}. Reflexivity was addressed by explicitly documenting the biases inherent in the simulated analytical lenses. The audit trail includes the frozen OSF preregistration, the clause-level parity matrix, and the final fragility-node register.

## Results

### 3.1 Mapping of the NHRA Action Situations
The qualitative extraction identified four core Action Situations (AS) that define the strategic interaction between jurisdictions and health services:
*   **AS1: Price Determination (Constitutional Phase):** A cooperative game where IHACPA sets the NEP, but information sets are constrained by historic cost data.
*   **AS2: Activity Submission (Operational Phase):** A non-cooperative game where LHNs choose coding intensity ($\theta$) and State Departments certify submissions.
*   **AS3: Audit and True-up (Financial Phase):** A sequential game where the Federal regulator chooses an audit targeting strategy ($A_t$) in response to anomaly signals.
*   **AS4: Dispute Resolution (Arbitration Phase):** Defined by Clauses 127-130 of the 2020 Addendum, this terminal node models the political costs of non-agreement.

### 3.2 Identification of Fragility Nodes and Undefined States
The analysis identified three primary "Fragility Nodes" where statutory ambiguity facilitates Strategic Gaming:
1.  **The Information Lag Node:** The 12-24 month delay between service delivery and final audit reconciliation creates a wide information set for LHN agents, allowing them to optimize for current-year revenue with low-probability future penalties.
2.  **The Composite Signal Node (PSI-90):** Because Patient Safety Indicators are composite and noisy, the marginal utility of genuine safety effort is lower than the marginal utility of "Signal Management" (selective documentation).
3.  **The Boundary Ambiguity Node:** Clauses relating to "substitute services" (block vs. ABF) permit cost-shifting equilibria that bypass the 6.5% Commonwealth growth cap.

### 3.3 Equilibrium Analysis: The Dominance of Strategic Gaming
Mathematical analysis of the formalized game tree indicates that Strategic Gaming becomes the dominant equilibrium strategy when the weighting of reputational payoffs ($\beta$) exceeds a threshold relative to the probability of audit ($P_{audit}$).
*   **Symbolic Compliance Equilibrium:** Occurs when LHNs adopt a "performance mask" that satisfies public metrics while maintaining high throughput efficiency.
*   **High Reliability Equilibrium:** Found to be unstable under current NHRA payoff rules, as the cost of genuine clinical quality ($C$) is not fully compensated by the NWAU valuation model ($F$).

### 3.4 Sensitivity to Policy Levers
Simulation of the extensive-form model revealed that increasing "Audit Pressure" ($A_t$) has a diminishing marginal return on deterring gaming behaviors. However, "Transparency Surges"—defined as the contemporaneous publication of granular performance data—shifted the equilibrium toward High Reliability by increasing the weight of long-term reputational risk over immediate financial gain.

## Discussion
The findings of this study suggest that the National Health Reform Agreement, while structurally robust in its financial mechanics, contains significant "grammar" gaps that favor **Strategic Gaming** over genuine system performance. By mapping the Agreement to Ostrom’s IAD framework, we have demonstrated that the "Rules-on-Paper" are frequently decoupled from the "Rules-in-Use" due to constructive ambiguity and imperfect information {Ostrom, 2005 @Ostrom_2005 #121}. This decoupling is not merely a managerial failure but an emergent equilibrium of the system's own design.

Our analysis of "Fragility Nodes" reveals that the current audit regime operates at a significant time lag, creating a "moral hazard" where immediate revenue gains outweigh distant, noisy penalties. This aligns with the sociological construct of **Institutional Isomorphism**, where LHNs are forced to adopt isomorphic masks of high performance to maintain legitimacy in a competitive funding pool {DiMaggio & Powell, 1983 @DiMaggio_1983 #110}. The dominance of the **Symbolic Compliance Equilibrium** suggests that current policy efforts to improve safety via pricing adjustments (e.g., HAC penalties) may be insufficient if they do not address the information asymmetry between the clinical coalface and the regulatory office.

Furthermore, the sensitivity analysis indicates that "Audit Surges" are a sub-optimal deterrent. Instead, structural reform should focus on "Transparency Surges"—the reduction of reporting lags and the contemporaneous publication of granular performance signals. By narrowing the information sets available to strategic agents, the regulator can shift the dominant strategy from gaming toward High Reliability.

### 4.1 Limitations
This study is limited by its reliance on simulated expert personas for coding, which may introduce a systematic "model bias" toward formal policy interpretations. Additionally, the corpus is restricted to public statutory and policy documents, which may not fully capture the informal "street-level" bureaucratic work-arounds that occur in practice. Future research should triangulate these game-theoretic findings with direct empirical observations of LHN coding behaviors.

## Conclusion
This study provided the first formal game-theoretic mapping of the National Health Reform Agreement, identifying the structural vulnerabilities that drive Strategic Gaming in the Australian hospital system. Our results show that the current incentive structure mathematically favors symbolic compliance over substantive system performance improvement. Structural reform of the Agreement's "incentive grammar"—specifically focusing on reducing information lags and neutralizing constructive ambiguity—is essential to transition the system toward a High Reliability equilibrium.

## References
1. Baez Hernandez, A. (2025). Games theory. A valuable instrument in decision-making in public policies. *Revista de la Facultad de Ciencias Económicas*.
2. Bevan, G., & Hood, C. (2006). What’s measured is what matters: targets and gaming in the English public health care system. *Public Administration*, 84(3), 517-538.
3. Bowen, G. A. (2009). Document analysis as a qualitative research method. *Qualitative Research Journal*, 9(2), 27-40.
4. Council on Federal Financial Relations. (2011). *National Health Reform Agreement*.
5. DiMaggio, P. J., & Powell, W. W. (1983). The iron cage revisited: institutional isomorphism and collective rationality in organizational fields. *American Sociological Review*, 48(2), 147-160.
6. Duckett, S. (2021). Vicious cycles: hospital bed block and the National Health Reform Agreement. *Medical Journal of Australia*, 214(8), 345-346.
7. Hermans, L. M., et al. (2014). The usefulness of game theory as a method for policy evaluation. *Evaluation*, 20(1), 10-25.
8. IHACPA. (2024). *Pricing Framework for Australian Public Hospital Services 2024–25*.
9. Mannion, R., & Braithwaite, J. (2012). Unintended consequences of performance measurement in healthcare: 20 salutary lessons from the English National Health Service. *Internal Medicine Journal*, 42(5), 569-574.
10. O'Brien, B. C., et al. (2014). Standards for reporting qualitative research: a synthesis of recommendations. *Academic Medicine*, 89(9), 1245-1251.
11. Ostrom, E. (2005). *Understanding Institutional Diversity*. Princeton University Press.
12. Schelling, T. C. (1960). *The Strategy of Conflict*. Harvard University Press.
