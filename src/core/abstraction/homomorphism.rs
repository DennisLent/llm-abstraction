use crate::core::abstraction::*;
use crate::core::game::{utils::actions::Action, utils::errors::GameError, *};
use errors::AbstractionError;
use game_logic::Game;
use ordered_float::OrderedFloat;
use rayon::prelude::*;
use state::State;
use std::collections::{HashMap, HashSet, VecDeque};
use std::time::Instant;
use storing::{load_cache, save_cache, AbstractionEntry};

/// BFS to enumerate all reachable states from the initial game state.
/// Each unique state is assigned a unique index from [0, N].
/// N is the number of reachable states.
pub fn get_all_states(game: &Game) -> Result<Vec<State>, GameError> {
    // Hashset to track visited states
    let mut visited_states: HashSet<State> = HashSet::new();
    let mut possible_states = Vec::new();

    // Standard BFS queue starting with the root game state
    let mut state_queue = VecDeque::from([game.get_state()]);

    while let Some(current_state) = state_queue.pop_front() {
        // Skip states that have already been visited
        if visited_states.contains(&current_state) {
            continue;
        }

        // Mark state as visited
        visited_states.insert(current_state.clone());
        possible_states.push(current_state.clone());

        // Find new reachable states based on actions --> append to queue
        for action in current_state.valid_moves() {
            let new_state = match game.simulate(&current_state, &action) {
                Ok((state, _)) => state,
                Err(e) => return Err(e),
            };

            state_queue.push_back(new_state);
        }
    }

    // Assign each state an index
    for (index, state) in possible_states.iter_mut().enumerate() {
        state.index = Some(index as isize);
    }

    Ok(possible_states)
}

/// Compute the “signature” of one state under the current partitioning.
/// For each action, record (reward, next_partition_id).  
/// Sorting these pairs gives us a fingerprint used to decide which states are equivalent.
/// This version is specifically so it can be used in parallel with rayon.
pub fn compute_signature_parallel(
    state: &State,
    partition: &HashMap<isize, usize>,
    game: &Game,
    position_lookup: &HashMap<(usize, usize), isize>,
) -> Vec<(OrderedFloat<f32>, usize)> {
    let mut outcomes = vec![];

    // For each action, simulate and record (reward, partition_of_successor).
    for action in state.valid_moves.iter() {
        // Simulate next game state
        // WARNING: simulated game states do not have an index therefore mapping to indexes is done with unit position
        // Couldn't think of a better way to do this
        let (_, vars) = game.simulate(state, action).unwrap();
        let pos = game.simulate(state, action).unwrap().0.unit_position;

        // Get next state index from mapping to unit position
        let next_index = match position_lookup.get(&pos) {
            Some(idx) => *idx,
            None => {
                eprintln!("Simulated state not found in state set.");
                eprintln!("Missing position: {:?}", pos);
                eprintln!(
                    "State details: {:?}",
                    game.simulate(state, action).unwrap().0
                );
                panic!("Abstraction failed: new state was not found in state set.");
            }
        };

        // Find which partition that successor state currently belongs to.
        let partition_id = *partition
            .get(&next_index)
            .expect("Partition must contain all state indices");

        // Push the reward + partition pair.
        outcomes.push((OrderedFloat(vars.score), partition_id));
    }

    // Sort so that signature is order-invariant across action enumeration.
    outcomes.sort_by(|a, b| a.partial_cmp(b).unwrap());
    outcomes
}

/// Main loop of MDP‐homomorphism refinement:
///   1. Initialize coarse partition: terminal vs. nonterminal.
///   2. Repeat until (no change) or early-stop:
///        a) For *each* state, compute its signature.
///        b) Group states by identical signature.
///        c) Reassign each group a new unique partition id.
///   3. Return the final clusters of state‐indices.
pub fn compute_mdp_homomorphism(states: &[State], game: &Game) -> Vec<Vec<isize>> {
    let mut partition: HashMap<isize, usize> = HashMap::new();

    // Start with two partitions: goal‐states (pid=0) vs. everything else (pid=1)
    for state in states.iter() {
        let done = game.goal() == state.unit_position;
        partition.insert(
            state.index.expect("State must be indexed"),
            if done { 0 } else { 1 },
        );
    }

    // Build unit_position -> index lookup table
    // States that come from simulation don't have an index so we need to compare unit positions since they are unique
    // Used in the signature function, this spares us time having to recalculate it
    let mut position_lookup: HashMap<(usize, usize), isize> = HashMap::new();
    for state in states.iter() {
        position_lookup.insert(state.unit_position, state.index.unwrap());
    }

    // Heuristic early stop variables - tuned by just playing around
    // IMPORTANT HERE:
    // `min_iters`: Minimum amount of iterations before we early stop
    // `max_stagnant_iters`: How many iterations we see barely any change before we stop
    let total_states = states.len();
    let mut changed = true;
    let mut iteration = 0;
    let min_iters = 10000;
    let max_stagnant_iters = 100;
    let mut stagnant_count = 0;
    let mut prev_partition_count = 0;

    // Refinement
    // O(S * A * number of iterations)
    // Computationally very expensive, therefore using early stopping
    while changed {
        // Compute signatures in parallel with rayon to distribute over cores
        let sig_state_pairs: Vec<(Vec<(OrderedFloat<f32>, usize)>, isize)> = states
            .par_iter()
            .map(|state| {
                let sig = compute_signature_parallel(state, &partition, game, &position_lookup);
                (sig, state.index.unwrap())
            })
            .collect();

        // Regroup states by identical signature
        let mut groups_by_signature: HashMap<Vec<(OrderedFloat<f32>, usize)>, Vec<isize>> =
            HashMap::new();
        for (sig, idx) in sig_state_pairs {
            groups_by_signature.entry(sig).or_default().push(idx);
        }

        // Build a new partition map by assigning each group a new pid
        let mut new_partition: HashMap<isize, usize> = HashMap::new();
        let mut pid = 0;

        for group in groups_by_signature.values() {
            for idx in group.iter() {
                new_partition.insert(*idx, pid);
            }
            pid += 1;
        }

        // Get the new partitions and see how they have changed compared to the last cycle
        let new_partition_count = new_partition.len();
        if iteration >= min_iters {
            if new_partition_count == prev_partition_count {
                stagnant_count += 1;
            } else {
                stagnant_count = 0;
            }

            // If we get a `somewhat` stable grouping after `n` iterations we can assume its gtg
            // If partially or fully abstractable we would be able to converge to a different grouping over time
            if stagnant_count >= max_stagnant_iters {
                println!(
                    "Early stop after {} stagnant iterations ({} total states, {} groups)",
                    stagnant_count, total_states, new_partition_count
                );
                break;
            }
        }

        prev_partition_count = new_partition_count;
        iteration += 1;

        if new_partition == partition {
            changed = false;
        } else {
            partition = new_partition;
        }
    }

    // Convert final partition map into Vec<Vec<isize>>
    let mut groups: HashMap<usize, Vec<isize>> = HashMap::new();
    for (idx, group_id) in partition {
        groups.entry(group_id).or_default().push(idx);
    }

    // Group the abstraction by ground state index
    // Similar to how it was done in Python prototype to allow comparing the results
    let mut clusters: Vec<Vec<isize>> = groups
        .into_values()
        .map(|mut v| {
            v.sort_unstable();
            v
        })
        .collect();
    clusters.sort_unstable_by_key(|cluster| cluster[0]);

    println!("Required {} iterations to converge", iteration);

    clusters
}

/// Top-level API: either load from cache to save time or compute the exact homomorphism.
/// Returns (all_states, clusters), and saves to disk for next time.
pub fn get_abstraction(game: &Game) -> Result<(Vec<State>, Vec<Vec<isize>>), AbstractionError> {
    let now = Instant::now();
    let config = &game.world_configuration();
    let cache_file = "abstraction_cache.json";

    // Load cache if available
    let mut cache = load_cache(cache_file).map_err(AbstractionError::Io)?;

    // Look for config
    if let Some(entry) = cache.iter().find(|e| &e.config == config) {
        return Ok((entry.states.clone(), entry.clusters.clone()));
    }

    // No config so we get all states and run compute function
    let mut game_clone = game.clone();
    let all_states =
        get_all_states(&mut game_clone).map_err(|e| AbstractionError::Computation {
            error: e.to_string(),
        })?;

    let clusters = compute_mdp_homomorphism(all_states.as_slice(), game);

    // Save to file
    cache.push(AbstractionEntry {
        config: config.clone(),
        states: all_states.clone(),
        clusters: clusters.clone(),
    });
    println!("Saving config...");
    save_cache(cache_file, &cache).map_err(AbstractionError::Io)?;

    let elapsed_time = now.elapsed();
    println!(
        "Took {} seconds to calculate exact homomorphism",
        elapsed_time.as_secs()
    );

    Ok((all_states, clusters))
}
