import streamlit as st

from nhra_gt.game_theory.registry import GameRegistry
from nhra_gt.game_theory.visualization import generate_payoff_matrix_figure


def render_game_encyclopedia(registry: GameRegistry) -> None:
    """
    Renders the Game Theoretic Encyclopedia UI component.
    """
    st.markdown("## Game Theoretic Encyclopedia")
    st.markdown("Explore the strategic interactions governing the NHRA ecosystem.")

    games = registry.list_all()
    game_titles = [g.title for g in games]

    # Selector
    selected_title = st.selectbox("Select a Strategic Game:", game_titles)

    # Find selected game
    game = next((g for g in games if g.title == selected_title), None)

    if game:
        st.subheader(game.title)

        # Layout: Left for Definition/Insight, Right for Matrix
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"**Players:** {', '.join(game.players)}")
            st.markdown(f"**Strategies:** {', '.join(game.strategies)}")
            st.markdown("### Strategic Insight")
            st.info(game.strategic_insight)

            st.markdown("### Nash Equilibrium")
            st.success(game.nash_equilibrium)

            st.markdown(f"**Key Parameter:** `{game.key_parameter}`")
            if game.evidence_link:
                st.markdown(f"**Evidence:** [{game.evidence_link}]")

        with col2:
            st.markdown("### Payoff Matrix")
            try:
                fig = generate_payoff_matrix_figure(game)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not render matrix: {e}")

        # Expander for raw rules/payoffs?
        with st.expander("View Raw Payoff Structure"):
            st.json(game.payoffs)


def render_mechanism_explainer(
    game_id: str, registry: GameRegistry, expanded: bool = False
) -> None:
    """
    Renders a collapsible explainer for a specific game, designed for contextual embedding.
    """
    game = registry.get(game_id)
    if not game:
        st.warning(f"Game '{game_id}' not found.")
        return

    with st.expander(f"🧩 Strategy Insight: {game.title}", expanded=expanded):
        st.markdown(f"**Why does this happen?** {game.strategic_insight}")

        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"**Key Driver:** `{game.key_parameter}`")
            st.success(f"**Nash Equilibrium:** {game.nash_equilibrium}")

        with c2:
            if game.evidence_link:
                st.markdown(f"[Evidence]({game.evidence_link})")
            # Maybe a small matrix button or link?
            # st.caption("See 'Game Encyclopedia' tab for full matrix.")
