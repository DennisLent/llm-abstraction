use thiserror::Error;

#[derive(Debug, Error)]
pub enum AbstractionError {
    #[error("I/O error during abstraction: {0}")]
    Io(#[from] std::io::Error),

    #[error("Failed to parse cache JSON: {0}")]
    Json(#[from] serde_json::Error),

    #[error("Homomorphism computation failed due to error: {error:?}")]
    Computation { error: String },

    #[error("BFS exhausted and no solution to the world found")]
    BFSExhausted,
}
