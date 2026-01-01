from nhra_gt.game_theory.registry import GameDefinition, GameRegistry


def get_populated_registry() -> GameRegistry:
    registry = GameRegistry()

    definition_game = GameDefinition(
        id="definition_game",
        title="Definition Game",
        players=["Commonwealth", "State"],
        strategies=["Realism", "Strictness"],
        payoffs={
            "Realism": {"Commonwealth": "Higher Cost", "State": "Lower Risk"},
            "Strictness": {"Commonwealth": "Lower Cost", "State": "Higher Risk"},
        },
        nash_equilibrium="Strictness (by default)",
        strategic_insight="The Commonwealth has an incentive to define hospital services strictly to minimize funding, while States prefer realism to cover actual costs.",
        evidence_link="NHRA Addendum 2020-2025",
        key_parameter="Definition Tightness",
    )
    registry.register(definition_game)

    bargaining = GameDefinition(
        id="bargaining_game",
        title="Bargaining Game",
        players=["Federal", "State"],
        strategies=["Agree", "Defer"],
        payoffs={
            "Agree": {"Federal": "Stability", "State": "Funding Certainty"},
            "Defer": {"Federal": "Status Quo", "State": "Potential Gain/Loss"},
        },
        nash_equilibrium="Depends on Discount Rate",
        strategic_insight="States must decide whether to agree to current terms or defer in hopes of a better deal, risking fiscal cliffs.",
        evidence_link="Federal Financial Relations Act 2009",
        key_parameter="Discount Rate",
    )
    registry.register(bargaining)

    cost_shifting = GameDefinition(
        id="cost_shifting_game",
        title="Cost Shifting Game",
        players=["Hospital (State)", "Primary Care (Federal)"],
        strategies=["Invest", "Shift"],
        payoffs={
            "Invest": {"State": "Higher Cost", "Federal": "Better Outcomes"},
            "Shift": {"State": "Lower Cost", "Federal": "Higher Burden"},
        },
        nash_equilibrium="Shift",
        strategic_insight="Fragmentation incentivizes shunting costs to the other jurisdiction rather than investing in holistic care.",
        evidence_link="Senate Inquiry into Hospital Funding 2016",
        key_parameter="Cost Shift Rate",
    )
    registry.register(cost_shifting)

    discharge = GameDefinition(
        id="discharge_game",
        title="Discharge Game",
        players=["Acute Care", "Aged Care/NDIS"],
        strategies=["Coordinate", "Fragment"],
        payoffs={
            "Coordinate": {"Acute": "Faster Flow", "Aged": "Resource Strain"},
            "Fragment": {"Acute": "Bed Block", "Aged": "Resource Preservation"},
        },
        nash_equilibrium="Fragment",
        strategic_insight="Bed block arises because downstream providers lack incentives to accept complex patients quickly.",
        evidence_link="AMA Public Hospital Report Card 2024",
        key_parameter="Discharge Coordination Friction",
    )
    registry.register(discharge)

    governance = GameDefinition(
        id="governance_game",
        title="Governance Game",
        players=["LHN", "MOH"],
        strategies=["Integrate", "Separate"],
        payoffs={
            "Integrate": {"LHN": "Autonomy Loss", "MOH": "Control"},
            "Separate": {"LHN": "Autonomy", "MOH": "Agency Loss"},
        },
        nash_equilibrium="Separate",
        strategic_insight="LHNs seek autonomy while central agencies seek control, leading to a principal-agent problem.",
        evidence_link="Victorian Health Services Review 2024",
        key_parameter="Centralization Index",
    )
    registry.register(governance)

    compliance = GameDefinition(
        id="compliance_game",
        title="Compliance Game",
        players=["Administrator", "Provider"],
        strategies=["Tight Audit", "Light Audit"],
        payoffs={
            "Tight": {"Admin": "High Discovery", "Provider": "High Compliance Cost"},
            "Light": {"Admin": "Low Discovery", "Provider": "Low Compliance Cost"},
        },
        nash_equilibrium="Mixed Strategy",
        strategic_insight="Auditors balance detection against cost, while providers balance compliance against risk of detection.",
        evidence_link="IHACPA National Efficient Price Determination",
        key_parameter="Audit Frequency",
    )
    registry.register(compliance)

    internal_lhn = GameDefinition(
        id="internal_lhn_competition",
        title="Internal LHN Competition",
        players=["LHN A (Urban)", "LHN B (Regional)"],
        strategies=["Revenue Capture", "Service Pressure"],
        payoffs={
            "p1_strategies": ["Revenue Capture", "Service Pressure"],
            "p2_strategies": ["Revenue Capture", "Service Pressure"],
            "matrix": [
                [("Surplus (High)", "Surplus (High)"), ("Surplus (High)", "Deficit (Severe)")],
                [("Deficit (Severe)", "Surplus (High)"), ("Crowding (Low)", "Crowding (Low)")],
            ],
        },
        nash_equilibrium="Revenue Capture (Urban dominance)",
        strategic_insight="LHNs compete for activity-based funding, often incentivizing profitable services over community need.",
        evidence_link="Productivity Commission Report on efficiency 2022",
        key_parameter="ABF Price Signal Strength",
    )
    registry.register(internal_lhn)

    electoral = GameDefinition(
        id="electoral_game",
        title="Electoral Game",
        players=["Incumbent", "Opposition"],
        strategies=["Salience (Health)", "Fiscal Responsibility"],
        payoffs={
            "p1_strategies": ["Salience (Health)", "Fiscal Responsibility"],
            "p2_strategies": ["Salience (Health)", "Fiscal Responsibility"],
            "matrix": [
                [
                    ("Votes + / Budget -", "Criticism (Weak)"),
                    ("Votes ++ / Budget --", "Attack (Failed)"),
                ],
                [
                    ("Budget + / Votes --", "Criticism (Strong)"),
                    ("Budget ++ / Votes -", "Attack (Effective)"),
                ],
            ],
        },
        nash_equilibrium="Salience Wars",
        strategic_insight="Health is a highly salient political issue, driving cycles of funding boosts followed by efficiency dividends.",
        evidence_link="AES Election Study 2022",
        key_parameter="Political Salience",
    )
    registry.register(electoral)

    return registry
