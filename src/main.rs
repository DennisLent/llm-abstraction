use core_rust::core::game::game_logic::Game;
use core_rust::core::runner::Runner;

fn main() {
    let world_vector: Vec<Vec<char>> = vec![
        vec!['.', '.', '.'],
        vec!['.', '.', '.'],
        vec!['.', '.', 'G'],
    ];
    let game = Game::new(world_vector).unwrap();
    game.print();

    for abstracted_bool in [true, false] {
        for simulation_limit in [8, 16, 32, 64, 128] {
            for simulation_depth in [8, 16, 32, 64] {
                let mut runner = Runner::new(&game, abstracted_bool, None);
                let outputs = runner.run(
                    simulation_limit,
                    simulation_depth,
                    1.4,
                    0.85,
                    None,
                    10,
                    100,
                    false,
                    false,
                );

                let avg_score: f32 = {
                    let sum: f32 = outputs.iter().map(|&(_turns, ret, _)| ret).sum();
                    sum / (outputs.len() as f32)
                };

                println!(
                    "abstracted={:<5}  limit={:<3}  depth={:<3}  → avg_return = {:.4}",
                    abstracted_bool, simulation_limit, simulation_depth, avg_score
                );
            }
        }
    }
}
