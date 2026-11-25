use std::collections::BTreeMap;

use paignia_core::{ActionId, PlayerId};
use paignia_solve::{
    pure_nash_equilibria_with_comparisons, NormalFormGame, PureNashComparison, SolverConfig,
    MAX_NORMAL_FORM_PROFILES,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

fn actions(count: usize) -> Vec<ActionId> {
    (0..count)
        .map(|index| ActionId(index.to_string()))
        .collect()
}

#[pyfunction]
fn pure_profiles(
    row: Vec<Vec<f64>>,
    column: Vec<Vec<f64>>,
    binary32: [bool; 2],
) -> PyResult<Vec<(usize, usize)>> {
    let height = row.len();
    let width = row.first().map_or(0, Vec::len);
    if height == 0
        || width == 0
        || height.saturating_mul(width) > MAX_NORMAL_FORM_PROFILES
        || height != column.len()
        || row.iter().chain(&column).any(|line| line.len() != width)
    {
        return Err(PyValueError::new_err(
            "Expected two complete bounded payoff tables of the same shape",
        ));
    }
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

#[pymodule]
fn _paignia(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(pure_profiles, module)?)
}
