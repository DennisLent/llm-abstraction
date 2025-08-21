use serde::{Deserialize, Serialize};
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

use crate::core::game::state::State;

// Cache entry: the world configuration and computed abstraction.
#[derive(Serialize, Deserialize)]
pub struct AbstractionEntry {
    pub config: Vec<Vec<char>>,
    pub states: Vec<State>,
    pub clusters: Vec<Vec<isize>>,
}

// Load the cache file (if it exists)
pub fn load_cache<P: AsRef<Path>>(path: P) -> std::io::Result<Vec<AbstractionEntry>> {
    if !path.as_ref().exists() {
        return Ok(Vec::new());
    }
    let mut f = File::open(path)?;
    let mut buf = String::new();
    f.read_to_string(&mut buf)?;
    if buf.trim().is_empty() {
        return Ok(Vec::new());
    }
    let v = serde_json::from_str(&buf)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
    Ok(v)
}

// Write the entire cache back out to the file
pub fn save_cache<P: AsRef<Path>>(path: P, cache: &[AbstractionEntry]) -> std::io::Result<()> {
    let mut f = OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(true)
        .open(path)?;
    let s = serde_json::to_string_pretty(cache)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
    f.write_all(s.as_bytes())?;
    Ok(())
}
