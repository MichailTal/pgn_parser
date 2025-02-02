use std::io;
use std::fs::File;
use std::process::exit;
use pyo3::prelude::*;
use regex::Regex;


#[pyclass]
pub struct PGNReader {
    #[pyo3(get)]
    metadata: Vec<(String, String)>,
    #[pyo3(get)]
    moves: Vec<String>

}

#[pyfunction]
fn parse_pgn(pgn: &str) -> PyResult<PGNReader> {
    let metadata_regex: Regex = Regex::new(r#"\[([^\]]+)\]"#).unwrap();
    let move_regex: Regex = Regex::new(r"(\b[a-h][1-8]|[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8]=?[NBRQ]?[+#]?)").unwrap();

    let metadata: Vec<(String, String)> = metadata_regex.captures_iter(pgn).map(|cap: regex::Captures<'_>| {
        let parts: Vec<&str> = cap[1].splitn(2, " ").collect();
        (parts[0].to_string(), parts.get(1).unwrap_or(&"").trim_matches('"').to_string())
    }).collect();

    let moves: Vec<String> = move_regex.find_iter(pgn).map(|m: regex::Match<'_>| m.as_str().to_string()).collect();

    Ok(PGNReader { metadata, moves})
}

#[pymodule]
fn pgn_parser(py: Python, module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(parse_pgn, module)?)?;
    module.add_class::<PGNReader>()?;
    Ok(())
} 
