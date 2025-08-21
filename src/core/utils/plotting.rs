use crate::core::game::state::State;
use plotters::prelude::*;
use std::fs;
use std::path::Path;

#[allow(dead_code)]
pub fn draw_world(
    world: &[Vec<char>],
    out_path: &str,
    cell_size: u32,
) -> Result<(), Box<dyn std::error::Error>> {
    // ensure output directory exists
    if let Some(dir) = Path::new(out_path).parent() {
        fs::create_dir_all(dir)?;
    }

    // convert sizes to i32
    let rows = world.len() as i32;
    let cols = if rows > 0 { world[0].len() as i32 } else { 0 };
    let cs = cell_size as i32;
    let width = cols * cs;
    let height = rows * cs;

    // create a bitmap backend; note it still takes (u32,u32)
    let root = BitMapBackend::new(out_path, ((width) as u32, (height) as u32)).into_drawing_area();
    root.fill(&WHITE)?;

    // draw grid lines
    for row in 0..=rows {
        let y = row * cs;
        root.draw(&PathElement::new(vec![(0, y), (width, y)], BLACK))?;
    }
    for col in 0..=cols {
        let x = col * cs;
        root.draw(&PathElement::new(vec![(x, 0), (x, height)], BLACK))?;
    }

    // draw each cell
    for (r, row) in world.iter().enumerate() {
        for (c, &ch) in row.iter().enumerate() {
            let x0 = (c as i32) * cs;
            let y0 = (r as i32) * cs;

            match ch {
                'X' => {
                    // filled black
                    root.draw(&Rectangle::new(
                        [(x0, y0), (x0 + cs, y0 + cs)],
                        BLACK.filled(),
                    ))?;
                }
                'G' => {
                    // green "G" centered
                    root.draw(&Text::new(
                        "G",
                        (x0 + cs / 3, y0 + cs / 4),
                        ("sans-serif", (cs / 2) as u32).into_font().color(&GREEN),
                    ))?;
                }
                _ => { /* leave blank */ }
            }
        }
    }

    root.present()?;
    Ok(())
}

#[allow(dead_code)]
pub fn draw_abstraction(
    world: &[Vec<char>],
    states: &[State],
    clusters: &[Vec<isize>],
    out_path: &str,
    cell_size: u32,
) -> Result<(), Box<dyn std::error::Error>> {
    // make sure the directory exists
    if let Some(dir) = Path::new(out_path).parent() {
        fs::create_dir_all(dir)?;
    }
    let rows = world.len() as i32;
    let cols = if rows > 0 { world[0].len() as i32 } else { 0 };
    let cs = cell_size as i32;
    let width = (cols * cs) as u32;
    let height = (rows * cs) as u32;

    let root = BitMapBackend::new(out_path, (width, height)).into_drawing_area();
    root.fill(&WHITE)?;

    // grid & terrain exactly same as draw_world
    for r in 0..=rows {
        let y = r * cs;
        root.draw(&PathElement::new(vec![(0, y), (cols * cs, y)], BLACK))?;
    }
    for c in 0..=cols {
        let x = c * cs;
        root.draw(&PathElement::new(vec![(x, 0), (x, rows * cs)], BLACK))?;
    }
    for (r, row) in world.iter().enumerate() {
        for (c, &ch) in row.iter().enumerate() {
            let x0 = (c as i32) * cs;
            let y0 = (r as i32) * cs;
            if ch == 'X' {
                root.draw(&Rectangle::new(
                    [(x0, y0), (x0 + cs, y0 + cs)],
                    BLACK.filled(),
                ))?;
            }
        }
    }

    // now overlay cluster‐IDs
    for (abs_id, cluster) in clusters.iter().enumerate() {
        let label = abs_id.to_string();
        for &state_idx in cluster {
            let State {
                unit_position: (x, y),
                ..
            } = &states[state_idx as usize];
            let x0 = (*x as i32) * cs;
            let y0 = (*y as i32) * cs;
            let cx = x0 + cs / 2;
            let cy = y0 + cs / 2;
            // radius just a bit smaller than half a cell
            let radius = (cs as f64) * 0.4;

            // lightly‐filled blue circle with thin border
            root.draw(&Circle::new((cx, cy), radius, BLUE))?;

            // then the cluster‐ID itself, in BLACK, roughly centered
            root.draw(&Text::new(
                label.clone(),
                (
                    cx - (cs as f64 * 0.15) as i32,
                    cy - (cs as f64 * 0.15) as i32,
                ),
                ("sans-serif", (cs as f64 * 0.5) as u32)
                    .into_font()
                    .color(&BLACK),
            ))?;
        }
    }

    root.present()?;
    Ok(())
}
