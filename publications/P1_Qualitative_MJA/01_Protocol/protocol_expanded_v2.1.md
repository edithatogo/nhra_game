# Protocol: Structural Analysis of the National Health Reform Agreement using Game Theory (Expanded v2.1)
**Author:** Dylan A Mordaunt

## 1. Background & Rationale
The National Health Reform Agreement (NHRA), signed in 2011, fundamentally shifted the Australian public hospital funding landscape from historical block grants to Activity Based Funding (ABF). While the stated objective was to drive efficiency and transparency (Duckett, 2021), the implementation of such a complex, multi-layered incentive system often leads to unintended strategic behaviors. These behaviors, collectively termed **"Strategic Gaming,"** involve organizations optimizing for metric reporting and symbolic compliance rather than substantive improvements in system performance or clinical quality.

Strategic Gaming in this context is a sophisticated form of **Symbolic Compliance**, where agents (Local Health Networks, LHNs) prioritize the "appearance" of meeting key performance indicators (KPIs) to secure maximum National Weighted Activity Unit (NWAU) revenue. This phenomenon is grounded in **Institutional Isomorphism** (DiMaggio & Powell, 1983), where regulatory and competitive pressures force healthcare organizations to adopt similar "masks" of high performance. In the context of the NHRA, the financial penalties associated with Hospital Acquired Complications (HACs) and the performance rankings based on Patient Safety Indicator 90 (PSI-90) indicators create a high-stakes environment. However, when these indicators are noisy or decoupled from actual clinical effort, the rational strategy for a Local Health Network (LHN) may shift from genuine performance improvement to Strategic Gaming (reporting optimization).

Despite the widespread clinical and administrative recognition of these gaming behaviors, there remains a critical gap in the systematic identification of the structural vulnerabilities that enable them. Recent methodological reviews (Baez Hernandez, 2025) highlight that while game theory is increasingly recognized as a valuable instrument for public policy decision-making, its specific application to the structural mapping of legal and statutory agreements is underdeveloped. Public policy, as a field, often relies on descriptive or econometric evaluations that capture outcomes but fail to map the underlying strategic interactions defined by the rules of the game. This study addresses this gap by applying a rigorous game-theoretic framework to the legal text of the NHRA.

## 2. Theoretical Framework: The IAD Approach
We utilize Elinor Ostrom’s **Institutional Analysis and Development (IAD)** framework (Ostrom, 2005) as the primary lens for document analysis. The IAD framework is uniquely suited for this task as it provides a structured "grammar" for institutions. It allows for the systematic breakdown of the NHRA into "Action Situations," where "Players" (Federal and State governments, LHN Boards) interact based on a specific set of "Rules" (statutory clauses) and "Information Sets."

### 2.1 IAD Component Mapping
We map the components of the NHRA to the seven universal rules defined by Ostrom:
1.  **Boundary Rules:** Defining who can participate in the health funding pool.
2.  **Position Rules:** Establishing roles such as the "Administrator of the National Health Funding Pool" and "Pricing Authority."
3.  **Choice Rules:** Specifying the actions available to LHNs (e.g., coding, discharge management).
4.  **Information Rules:** Dictating data submission timelines and transparency requirements.
5.  **Payoff Rules:** The ABF price weights, caps, and safety-based penalties.
6.  **Aggregation Rules:** How individual LHN data is aggregated into State-level growth caps.
7.  **Scope Rules:** The geographical and service-type boundaries of the Agreement.

### 2.2 Constructive Ambiguity
The NHRA is characterized by **Constructive Ambiguity**—intentional vagueness in policy text designed to facilitate political consensus among jurisdictions with divergent interests. While politically expedient, this ambiguity creates "undefined states" in the formal game tree. Using the IAD framework, we can identify these gaps where the "Rules-in-Use" may diverge significantly from the "Rules-on-Paper," permitting non-cooperative equilibria such as cost-shifting and reporting manipulation.

## 3. Taxonomy of Strategic Gaming
To guide the qualitative coding, we define a preliminary taxonomy of Strategic Gaming behaviors hypothesized to exist within the NHRA structure:
*   **Upcoding (Classification Shifting):** Strategic selection of diagnostic codes to maximize NWAU weight without corresponding clinical resource consumption.
*   **Cost-Shifting (Boundary Gaming):** Moving clinical activity between ABF-funded and block-funded streams (or between State and Federal funding pools) to bypass growth caps.
*   **Selective Disclosure:** Managing the submission of noisy indicators (like PSI-90) to present a symbolic mask of high quality while minimizing audit risk.
*   **Hysteretic Crisis Response:** Strategic escalation of system "pressure signals" to trigger political bailout mechanisms (side-payments) outside the formal ABF formula.

## 4. Objectives
1.  **Map the Formal Game Structure:** Systematically decompose the NHRA and its 2017 and 2020-2025 Addendums into an Extensive Form Game tree, identifying Players, Action Sets (Moves), and Payoff Functions.
2.  **Structural Incoherence Analysis:** Identify nodes in the game tree where "Constructive Ambiguity" leads to undefined payoffs or circular logic, facilitating strategic decoupling.
3.  **Equilibrium Determination:** Mathematically determine the conditions under which **Strategic Gaming** becomes the dominant strategy for LHNs, specifically accounting for the trade-off between **Financial Payoffs** (NWAU revenue) and **Reputational Payoffs** (Public rankings and political standing).
4.  **Policy Stress Testing:** Evaluate the sensitivity of the system to specific policy levers, such as the introduction of "Transparency Surges" or "Audit Pressure."

## 5. Methods

### 5.1 Study Design
This is a qualitative document analysis study using an **Extensive Form Game with Imperfect Information** approach. Extensive Form games (Schelling, 1960) allow for the modeling of sequential decision-making where players respond to the moves of others over time. This methodology is particularly suited for modeling the NHRA environment, where players (e.g., LHNs) have private information about their true state that is only noisily revealed to the regulator (e.g., IHACPA) through lagged data submissions.

### 5.2 Information Sources
The census of analyzed documents includes:
*   **National Health Reform Agreement (2011):** The foundation text.
*   **Addendums (2017, 2020-2025):** The operational updates defining the current funding caps and safety penalties.
*   **National Health Reform Act 2011 (Cth):** The statutory instrument providing legal force to the Agreement.
*   **IHACPA Pricing Frameworks (2024-25):** The detailed rules for NEP determination and HAC adjustment (IHACPA, 2024).
*   **AIHW Performance Reports:** Providing the context for noisy performance signals (AIHW, 2024).

### 5.3 Data Collection (Blinded Mapping Protocol)
To ensure auditability and minimize bias, the analysis uses a "Clean Room" protocol with two independent coding passes simulated through divergent analytical lenses.
*   **Pass A (Rule-Strict):** Codes strictly based on the explicit legal constraints and mandatory requirements found in the statutory text.
*   **Pass B (Context-Applied):** Codes based on the operational interpretation and known historical work-arounds documented in policy evaluations (Hermans et al., 2014).

**Extraction Categories:**
*   *Players:* Identifying the primary decision-makers and their alignment (e.g., the Commonwealth as the principal, States as agents, LHNs as sub-agents).
*   *Moves:* Mapping atomic actions (e.g., data submission) and **Iterative Negotiation Cycles** defined in the 2020 Addendum (Clauses 127-130).
*   *Information Sets:* Distinguishing between **Strategic Uncertainty** (opponent actions) and **Stochastic Uncertainty** (the noise in PSI-90 data).
*   *Payoffs:* Quantifying utility through both direct financial transfers (NWAU) and indirect reputational standing.

### 5.4 Analysis & Synthesis
The extracted logic will be reconciled by Dylan A Mordaunt, using the Statutory Lens to resolve discrepancies in clause interpretation. The final game tree will be validated for logical closure and analyzed for Nash Equilibria using the NHRA Game Engine. The synthesis will specifically look for "Fragility Nodes"—points in the agreement where a small change in information quality (audit pressure) causes a large shift in player strategy (from Honest to Gaming).

### 5.5 Reflexivity & Bias (Simulated)
This study acknowledges the "Model Bias" toward standardized policy interpretations inherent in the use of automated analytical agents. To mitigate this, multiple analytical lenses are adopted, and all steps of the deliberation are logged for peer audit. The use of a single author (Dylan A Mordaunt) ensuring consistency across these lenses provides a unified critical framework for the final synthesis.

## 6. Reporting Standards
This study complies with the **SRQR (Standards for Reporting Qualitative Research)** and utilizes the **PRISMA-ScR** checklist for the systematic identification of supplementary policy literature.