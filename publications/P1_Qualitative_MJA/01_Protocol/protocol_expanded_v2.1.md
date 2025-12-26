# Protocol: Structural Analysis of the National Health Reform Agreement using Game Theory (Expanded v2.1)
*Author:* Dylan A Mordaunt

## 1. Background & Rationale
The National Health Reform Agreement (NHRA), signed in 2011, fundamentally shifted the Australian public hospital funding landscape from historical block grants to Activity Based Funding (ABF). While the stated objective was to drive efficiency and transparency (Duckett, 2021), the implementation of such a complex, multi-layered incentive system often leads to unintended strategic behaviors. These behaviors, collectively termed *"Strategic Gaming,"* involve organizations optimizing for metric reporting and symbolic compliance rather than substantive improvements in system performance or clinical quality.

This phenomenon is grounded in *Institutional Isomorphism* (DiMaggio & Powell, 1983), where regulatory and competitive pressures force healthcare organizations to adopt similar "masks" of high performance. In the context of the NHRA, the financial penalties associated with Hospital Acquired Complications (HACs) and the performance rankings based on Patient Safety Indicator 90 (PSI-90) indicators create a high-stakes environment. However, when these indicators are noisy or decoupled from actual clinical effort, the rational strategy for a Local Health Network (LHN) may shift from genuine performance improvement to *Strategic Gaming* (reporting optimization).

Despite the widespread clinical and administrative recognition of these behaviors, there remains a critical gap in the systematic identification of the structural vulnerabilities that enable them. Recent methodological reviews (Baez Hernandez, 2025) highlight that while game theory is increasingly recognized as a valuable instrument for public policy decision-making, its specific application to the structural mapping of legal and statutory agreements is underdeveloped. This study addresses this gap by applying a rigorous game-theoretic framework to the legal text of the NHRA.

## 2. Theoretical Framework: The IAD Approach
We utilize Elinor Ostrom’s *Institutional Analysis and Development (IAD)* framework (Ostrom, 2005) as the primary lens for document analysis. The IAD framework allows for the systematic breakdown of the NHRA into "Action Situations," where "Players" (Federal and State governments, LHN Boards) interact based on a specific set of "Rules" (statutory clauses) and "Information Sets."

The NHRA is characterized by *Constructive Ambiguity*—intentional vagueness in policy text designed to facilitate political consensus among jurisdictions with divergent interests. While politically expedient, this ambiguity creates "undefined states" in the formal game tree, permitting non-cooperative equilibria such as cost-shifting and reporting manipulation.

## 3. Objectives
1.  *Map the Formal Game Structure:* Systematically decompose the NHRA and its 2017 and 2020-2025 Addendums into an Extensive Form Game tree, identifying Players, Action Sets (Moves), and Payoff Functions.
2.  *Structural Incoherence Analysis:* Identify nodes in the game tree where "Constructive Ambiguity" leads to undefined payoffs or circular logic, facilitating strategic decoupling.
3.  *Equilibrium Determination:* Mathematically determine the conditions under which *Strategic Gaming* becomes the dominant strategy for LHNs, specifically accounting for the trade-off between *Financial Payoffs* (NWAU revenue) and *Reputational Payoffs* (Public rankings and political standing).
4.  *Policy Stress Testing:* Evaluate the sensitivity of the system to specific policy levers, such as the introduction of "Transparency Surges" or "Audit Pressure."

## 4. Methods

### 4.1 Study Design
This is a qualitative document analysis study using an *Extensive Form Game with Imperfect Information* approach. This methodology is particularly suited for modeling sequential decision-making in environments where players (e.g., LHNs) have private information about their true state that is only noisily revealed to the regulator through lagged data submissions.

### 4.2 Information Sources
The census of analyzed documents includes:
*   *National Health Reform Agreement (2011):* The foundation text.
*   *Addendums (2017, 2020-2025):* The operational updates defining the current funding caps and safety penalties.
*   *National Health Reform Act 2011 (Cth):* The statutory instrument providing legal force to the Agreement.
*   *IHACPA Pricing Frameworks (all available years, 2012–13 to 2026–27):* The detailed rules for National Efficient Price (NEP) determination and Hospital Acquired Complications (HAC) adjustment.

#### IHACPA Pricing Frameworks — Available years
The IHACPA Pricing Frameworks for Australian Public Hospital Services are available for the following financial years (links go to IHACPA resource pages):

| Year | IHACPA Pricing Framework |
|------|--------------------------|
| 2026–27 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2026-27 |
| 2025–26 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2025-26 |
| 2024–25 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25 |
| 2023–24 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2023-24 |
| 2022–23 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2022-23 |
| 2021–22 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2021-22 |
| 2020–21 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2020-21 |
| 2019–20 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2019-20 |
| 2018–19 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2018-19 |
| 2017–18 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2017-18 |
| 2016–17 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2016-17 |
| 2015–16 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2015-16 |
| 2014–15 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2014-15 |
| 2013–14 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2013-14 |
| 2012–13 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2012-13 |

### 4.3 Data Collection (Blinded Mapping Protocol)
To ensure auditability and minimize bias, the analysis uses a "Clean Room" protocol with two independent coding passes simulated through divergent analytical lenses.
*   *Pass A (Rule-Strict):* Codes strictly based on the explicit legal constraints and mandatory requirements.
*   *Pass B (Context-Applied):* Codes based on the operational interpretation and known historical work-arounds.

*Extraction Categories:*
*   *Players:* Identifying the primary decision-makers and their alignment.
*   *Moves:* Mapping atomic actions and *Iterative Negotiation Cycles* defined in the 2020 Addendum (Clauses 127-130).
*   *Information Sets:* Distinguishing between *Strategic Uncertainty* (opponent actions) and *Stochastic Uncertainty* (data noise/PSI-90 lag).
*   *Payoffs:* Quantifying utility through both direct financial transfers and indirect reputational standing.

### 4.4 Analysis & Synthesis
The extracted logic will be reconciled to resolve discrepancies in clause interpretation. The final game tree will be validated for logical closure and analyzed for Nash Equilibria using the NHRA Game Engine.

### 4.5 Reflexivity & Bias (Simulated)
This study acknowledges the "Model Bias" toward standardized policy interpretations. To mitigate this, multiple analytical lenses are adopted, and all steps of the deliberation are logged for peer audit.

## 5. Reporting Standards
This study complies with the *SRQR (Standards for Reporting Qualitative Research)* and utilizes the *PRISMA-ScR* checklist for the systematic identification of supplementary policy literature.