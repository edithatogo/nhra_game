use std::collections::BTreeMap;

use paignia_core::{ActionEdge, ActionId, Game, Node, NodeId, PlayerId};
use paignia_solve::{
    backward_induction_with_config, pure_nash_equilibria_with_comparisons, solve_mixed_nash,
    MixedNashAlgorithm, MixedNashConfig, NormalFormGame, PureNashComparison, Solution,
    SolverConfig, DEFAULT_MAX_VISITED_NODES, MAX_NORMAL_FORM_PROFILES,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

fn actions(count: usize) -> Vec<ActionId> {
    (0..count)
        .map(|index| ActionId(index.to_string()))
        .collect()
}

fn payoff_shape(row: &[Vec<f64>], column: &[Vec<f64>]) -> PyResult<(usize, usize)> {
    let height = row.len();
    let width = row.first().map_or(0, Vec::len);
    if height == 0
        || width == 0
        || height.saturating_mul(width) > MAX_NORMAL_FORM_PROFILES
        || height != column.len()
        || row.iter().chain(column).any(|line| line.len() != width)
    {
        return Err(PyValueError::new_err(
            "Expected two complete bounded payoff tables of the same shape",
        ));
    }
    Ok((height, width))
}

#[pyfunction]
fn pure_profiles(
    row: Vec<Vec<f64>>,
    column: Vec<Vec<f64>>,
    binary32: [bool; 2],
) -> PyResult<Vec<(usize, usize)>> {
    let (height, width) = payoff_shape(&row, &column)?;
    let row_player = PlayerId("row".into());
    let column_player = PlayerId("column".into());
    let row_actions = actions(height);
    let column_actions = actions(width);
    let mut payoffs = BTreeMap::new();
    for (i, row_action) in row_actions.iter().enumerate() {
        for (j, column_action) in column_actions.iter().enumerate() {
            payoffs.insert(
                BTreeMap::from([
                    (row_player.clone(), row_action.clone()),
                    (column_player.clone(), column_action.clone()),
                ]),
                BTreeMap::from([
                    (row_player.clone(), row[i][j]),
                    (column_player.clone(), column[i][j]),
                ]),
            );
        }
    }
    let game = NormalFormGame {
        players: vec![row_player.clone(), column_player.clone()],
        strategies: BTreeMap::from([
            (row_player.clone(), row_actions),
            (column_player.clone(), column_actions),
        ]),
        payoffs,
    };
    let rules = BTreeMap::from([
        (row_player.clone(), comparison(binary32[0])),
        (column_player.clone(), comparison(binary32[1])),
    ]);
    let config = SolverConfig {
        tolerance: 1.0e-9,
        ..SolverConfig::default()
    };
    pure_nash_equilibria_with_comparisons(&game, config, &rules)
        .map_err(|error| PyValueError::new_err(error.to_string()))?
        .into_iter()
        .map(|profile| {
            let row = profile[&row_player].0.parse::<usize>();
            let column = profile[&column_player].0.parse::<usize>();
            row.and_then(|i| column.map(|j| (i, j)))
                .map_err(|error| PyValueError::new_err(error.to_string()))
        })
        .collect()
}

fn comparison(binary32: bool) -> PureNashComparison {
    if binary32 {
        PureNashComparison::AlternativeMinusBinary32
    } else {
        PureNashComparison::AlternativeMinusBinary64
    }
}

type MixedProfile = (Vec<f64>, Vec<f64>);

#[pyfunction]
fn mixed_profile(row: Vec<Vec<f64>>, column: Vec<Vec<f64>>) -> PyResult<Option<MixedProfile>> {
    if payoff_shape(&row, &column)? != (2, 2) {
        return Err(PyValueError::new_err("Expected two 2-by-2 payoff tables"));
    }
    let result = solve_mixed_nash(
        &row,
        &column,
        MixedNashAlgorithm::SupportEnumeration,
        MixedNashConfig::default(),
    )
    .map_err(|error| PyValueError::new_err(error.to_string()))?;
    Ok(result
        .candidates
        .into_iter()
        .find(|candidate| candidate.row_support.len() == 2 && candidate.column_support.len() == 2)
        .map(|candidate| (candidate.row_strategy, candidate.column_strategy)))
}

#[pyfunction]
fn commitment_choice(leader: Vec<Vec<f64>>, follower: Vec<Vec<f64>>) -> PyResult<(usize, usize)> {
    let (rows, columns) = payoff_shape(&leader, &follower)?;
    if rows + rows * columns + 1 > DEFAULT_MAX_VISITED_NODES {
        return Err(PyValueError::new_err(
            "Commitment tree exceeds the node budget",
        ));
    }
    let leader_player = PlayerId("leader".into());
    let follower_player = PlayerId("follower".into());
    let root = NodeId("root".into());
    let row_digits = (rows - 1).to_string().len();
    let column_digits = (columns - 1).to_string().len();
    let mut root_edges = Vec::with_capacity(rows);
    let mut follower_nodes = Vec::with_capacity(rows);
    let mut nodes = BTreeMap::new();
    for (row, (leader_payoffs, follower_payoffs)) in leader.iter().zip(&follower).enumerate() {
        let decision = NodeId(format!("follower:{row}"));
        root_edges.push(ActionEdge {
            action: ActionId(format!("{row:0row_digits$}")),
            target: decision.clone(),
        });
        let mut edges = Vec::with_capacity(columns);
        for (column, (&leader_payoff, &follower_payoff)) in
            leader_payoffs.iter().zip(follower_payoffs).enumerate()
        {
            let terminal = NodeId(format!("terminal:{row}:{column}"));
            edges.push(ActionEdge {
                action: ActionId(format!("{column:0column_digits$}")),
                target: terminal.clone(),
            });
            nodes.insert(
                terminal,
                Node::Terminal {
                    payoffs: BTreeMap::from([
                        (leader_player.clone(), leader_payoff),
                        (follower_player.clone(), follower_payoff),
                    ]),
                },
            );
        }
        nodes.insert(
            decision.clone(),
            Node::Decision {
                player: follower_player.clone(),
                edges,
            },
        );
        follower_nodes.push(decision);
    }
    nodes.insert(
        root.clone(),
        Node::Decision {
            player: leader_player,
            edges: root_edges,
        },
    );
    let config = SolverConfig {
        tolerance: 0.0,
        ..SolverConfig::default()
    };
    let solution = backward_induction_with_config(
        &Game {
            root: root.clone(),
            nodes,
        },
        config,
    )
    .map_err(|error| PyValueError::new_err(error.to_string()))?;
    let row = selected_index(&solution, &root)?;
    let column = selected_index(&solution, &follower_nodes[row])?;
    Ok((row, column))
}

fn selected_index(solution: &Solution, node: &NodeId) -> PyResult<usize> {
    solution
        .choices
        .get(node)
        .ok_or_else(|| PyValueError::new_err("Missing commitment action"))?
        .0
        .parse::<usize>()
        .map_err(|error| PyValueError::new_err(error.to_string()))
}

#[pymodule]
fn _paignia(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("MAX_COMMITMENT_NODES", DEFAULT_MAX_VISITED_NODES)?;
    module.add_function(wrap_pyfunction!(pure_profiles, module)?)?;
    module.add_function(wrap_pyfunction!(mixed_profile, module)?)?;
    module.add_function(wrap_pyfunction!(commitment_choice, module)?)
}
