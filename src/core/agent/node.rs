use std::cell::RefCell;
use std::collections::HashSet;
use std::fmt;
use std::rc::{Rc, Weak};

use crate::core::game::*;
use rand::rngs::StdRng;
use rand::Rng;
use state::State;
use utils::actions::Action;

#[derive(Debug)]
pub enum MCTSError {
    TreeError,
}

pub type NodeRef = Rc<RefCell<MCTSNode>>;

pub struct MCTSNode {
    state: State,
    parent: Option<Weak<RefCell<MCTSNode>>>,
    children: Vec<NodeRef>,
    visits: i32,
    reward: f32,
    q: f32,
    depth: i32,
    action: Action,
    done: bool,
    index: i32,
    c: f32,
    gamma: f32,
    untried_actions: Vec<Action>,
}

impl fmt::Debug for MCTSNode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Python-style "[END]" marker if terminal
        let end_flag = if self.done { " [END]" } else { "" };
        // Q(s,a) = total_q / visits
        let q_val = if self.visits > 0 {
            self.q / self.visits as f32
        } else {
            0.0
        };

        write!(
            f,
            "{end_flag} Node{} Depth:{} [Action: {:?}] | \
             Visits={}, R(s,a)={:.4} ΣQ(s,a)={:.4} Q(s,a)={:.4}",
            self.index,
            self.depth,
            self.action, // or `{}` if Action: Display
            self.visits,
            self.reward,
            self.q,
            q_val,
        )
    }
}

impl MCTSNode {
    pub fn new(
        state: State,
        parent: Option<Weak<RefCell<MCTSNode>>>,
        action: Action,
        depth: i32,
        reward: f32,
        done: bool,
        index: i32,
        c: f32,
        gamma: f32,
    ) -> Self {
        let valid_moves = state.valid_moves().to_vec();

        MCTSNode {
            state,
            parent,
            children: Vec::new(),
            visits: 0,
            reward,
            q: 0.0,
            depth,
            action,
            done,
            index,
            c,
            gamma,
            untried_actions: valid_moves,
        }
    }

    pub fn get_state(&self) -> State {
        self.state.clone()
    }

    pub fn get_depth(&self) -> i32 {
        self.depth
    }

    pub fn add_child(&mut self, child_node: NodeRef) {
        self.children.push(child_node);
    }

    pub fn is_terminal(&self) -> bool {
        self.done
    }

    fn n(&self) -> i32 {
        self.visits
    }

    fn q(&self) -> f32 {
        if self.visits > 0 {
            return self.q / self.visits as f32;
        }
        0.0
    }

    pub fn best_child(&self, c_param: Option<f32>) -> Result<NodeRef, MCTSError> {
        if self.children.is_empty() {
            return Err(MCTSError::TreeError);
        }

        let c = c_param.unwrap_or(self.c);
        let n = self.n() as f32;
        let ln_n = n.ln();

        let (best, _) = self
            .children
            .iter()
            .map(|child_rc| {
                let child = child_rc.borrow();
                let ni = child.n() as f32;

                let uct = if ni == 0.0 {
                    f32::INFINITY
                } else {
                    child.q() + c * ((ln_n / ni).sqrt())
                };

                (Rc::clone(child_rc), uct)
            })
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
            .unwrap();

        Ok(best)
    }

    pub fn find_leaf_node(start: &NodeRef) -> NodeRef {
        let mut current = Rc::clone(start);

        loop {
            {
                let node = current.borrow();
                if node.is_terminal() || !node.untried_actions.is_empty() {
                    break;
                }
            }

            let c = current.borrow().c;

            let next_res = {
                let node_ref = current.borrow();
                node_ref.best_child(Some(c))
            };

            match next_res {
                Ok(child) => current = child,
                Err(_) => break,
            }
        }

        current
    }

    pub fn expand(&mut self, rng: &mut StdRng) -> Action {
        // Can do this as we only select nodes that still have actions
        let idx = rng.random_range(0..self.untried_actions.len());
        self.untried_actions.remove(idx)
    }

    pub fn backpropagate(start: &NodeRef, mut value_estimate: f32) {
        let mut current: Option<NodeRef> = Some(Rc::clone(start));

        while let Some(node_rc) = current.take() {
            {
                let mut node = node_rc.borrow_mut();

                node.visits += 1;

                node.q += node.reward + node.gamma * value_estimate;

                value_estimate = node.reward + node.gamma * value_estimate;

                current = node
                    .parent
                    .as_ref()
                    .and_then(|weak_parent| weak_parent.upgrade());
            }
        }
    }

    pub fn best_action(&self) -> Action {
        return self.best_child(Some(0.0)).unwrap().borrow().action;
    }

    pub fn print_tree(root: &NodeRef) {
        // Find best path
        let mut best_path: HashSet<i32> = HashSet::new();
        let mut cur_opt = Some(Rc::clone(root));
        while let Some(cur_rc) = cur_opt {
            let cur = cur_rc.borrow();
            best_path.insert(cur.index);
            cur_opt = if cur.children.is_empty() {
                None
            } else {
                Some(cur.best_child(Some(0.0)).unwrap())
            };
        }

        // Print tree
        recurse_print(root, "", true, &best_path);
    }
}

fn recurse_print(node_ref: &NodeRef, prefix: &str, is_last: bool, best_path: &HashSet<i32>) {
    const BOLD_GREEN: &str = "\x1b[1;32m";
    const RESET: &str = "\x1b[0m";

    let node = node_ref.borrow();

    print!("{}", prefix);
    if node.parent.is_some() {
        if is_last {
            print!("└──");
        } else {
            print!("├──");
        }
    }

    if best_path.contains(&node.index) {
        println!("{}{:?}{}", BOLD_GREEN, *node, RESET);
    } else {
        println!("{:?}", *node);
    }

    let mut child_prefix = prefix.to_string();
    if node.parent.is_some() {
        if is_last {
            child_prefix += "    ";
        } else {
            child_prefix += "│   ";
        }
    }

    let last_i = node.children.len().saturating_sub(1);
    for (i, child_rc) in node.children.iter().enumerate() {
        let last = i == last_i;
        recurse_print(child_rc, &child_prefix, last, best_path);
    }
}
