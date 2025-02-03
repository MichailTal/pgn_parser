use std::ffi::OsStr;
use std::path::Path;
use std::{fs::File, io::Read};

use pyo3::prelude::*;
use regex::Regex;
use pyo3::exceptions::PyValueError;
use pyo3::exceptions::PyOSError;

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
/// 
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

fn check_file_extension(file_path: &str) -> PyResult<()> {
    let file_extension: Option<&str> = Path::new(file_path).extension().and_then(OsStr::to_str);

    if file_extension != Some("pgn") {
        return Err(PyOSError::new_err(format!("Found incompatible file extension: {:?}", file_extension)));
    }

    Ok(())
}

fn open_single_pgn_file_content(file_path: &str) -> std::io::Result<String> {  
    check_file_extension(file_path)?;
    let mut file: File = File::open(file_path)?;
    let mut contents: String = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

#[pyfunction]
fn parse_single_pgn_file(file_path: &str) -> Result<PGNReader, PyErr> {
    match open_single_pgn_file_content(file_path) {
        Ok(content) => parse_pgn(&content).map_err(|e: PyErr| PyErr::from(e)),
        Err(error) => Err(PyOSError::new_err(format!("File under the path {} could not be opened: {}", file_path, error))),
    }
}


/// Python module for parsing PGN files.
#[pymodule]
fn pgn_parser(_py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(parse_pgn, module)?)?;
    module.add_function(wrap_pyfunction!(parse_single_pgn_file, module)?)?;
    module.add_class::<PGNReader>()?;
    Ok(())
}