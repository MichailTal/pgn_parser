use pyo3::prelude::*;
use regex::Regex;
use pyo3::exceptions::PyValueError;

#[pyclass]
pub struct PGNReader {
    #[pyo3(get)]
    metadata: Vec<(String, String)>,
    #[pyo3(get)]
    moves: Vec<String>,
}

/// Parses a PGN (Portable Game Notation) string and returns a PGNReader object.
///
/// # Arguments
/// * `pgn` - A string containing the PGN data.
///
/// # Returns
/// A `PGNReader` object containing metadata and moves.
///
/// # Errors
/// Returns a `PyValueError` if the PGN string is invalid or cannot be parsed.
#[pyfunction]
fn parse_pgn(pgn: &str) -> PyResult<PGNReader> {
    let metadata_regex: Regex = Regex::new(r#"\[([^\]]+)\]"#).map_err(|e: regex::Error| {
        PyValueError::new_err(format!("Failed to compile metadata regex: {}", e))
    })?;

    let move_regex: Regex = Regex::new(r"(\b[a-h][1-8]|[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8]=?[NBRQ]?[+#]?)").map_err(|e: regex::Error| {
        PyValueError::new_err(format!("Failed to compile move regex: {}", e))
    })?;

    // Check empty pgn
    if pgn.len() == 0 {
        return Err(PyValueError::new_err(format!("PGN is empty.")))
    }

    // Extract metadata
    let metadata: Vec<(String, String)> = metadata_regex
        .captures_iter(pgn)
        .map(|cap: regex::Captures<'_>| {
            let parts: Vec<&str> = cap[1].splitn(2, ' ').collect();
            if parts.len() < 2 {
                return Err(PyValueError::new_err("Invalid metadata format in PGN"));
            }
            Ok((parts[0].to_string(), parts[1].trim_matches('"').to_string()))
        })
        .collect::<PyResult<_>>()?;

    // Extract moves
    let moves: Vec<String> = move_regex
        .find_iter(pgn)
        .map(|m: regex::Match<'_>| m.as_str().to_string())
        .collect();

    Ok(PGNReader { metadata, moves })
}

/// Python module for parsing PGN files.
#[pymodule]
fn pgn_parser(_py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(parse_pgn, module)?)?;
    module.add_class::<PGNReader>()?;
    Ok(())
}