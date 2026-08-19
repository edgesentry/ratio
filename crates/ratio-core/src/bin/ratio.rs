//! Edge CLI: derive shareable-product metadata. Does not publish raw data.

use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

use ratio_core::product::{build_shareable_product, DeriveInput, Scenario};

fn usage() -> ExitCode {
    eprintln!(
        "usage:\n  ratio derive --scenario K1|S1|S2 --pointer local://… [--id URN] [--ts RFC3339] [-o FILE]"
    );
    ExitCode::from(2)
}

fn arg_value<'a>(args: &'a [String], flag: &str) -> Option<&'a str> {
    args.iter()
        .position(|a| a == flag)
        .and_then(|i| args.get(i + 1))
        .map(|s| s.as_str())
}

fn flag_set(args: &[String], flag: &str) -> bool {
    args.iter().any(|a| a == flag)
}

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.get(1).map(String::as_str) != Some("derive") {
        return usage();
    }
    if flag_set(&args, "-h") || flag_set(&args, "--help") {
        return usage();
    }
    let scenario = match arg_value(&args, "--scenario").and_then(Scenario::parse) {
        Some(s) => s,
        None => {
            eprintln!("error: --scenario K1|S1|S2 required");
            return ExitCode::from(2);
        }
    };
    let pointer = match arg_value(&args, "--pointer") {
        Some(p) => p,
        None => {
            eprintln!("error: --pointer local://… required");
            return ExitCode::from(2);
        }
    };
    let id = arg_value(&args, "--id").unwrap_or("urn:uuid:00000000-0000-0000-0000-000000000001");
    let ts = arg_value(&args, "--ts").unwrap_or("2026-08-18T00:00:00Z");
    let input = DeriveInput::stub_for(scenario, id, ts, pointer);
    let product = match build_shareable_product(&input) {
        Ok(p) => p,
        Err(e) => {
            eprintln!("error: {e}");
            return ExitCode::from(1);
        }
    };
    let json = match product.to_json() {
        Ok(s) => s + "\n",
        Err(e) => {
            eprintln!("error: {e}");
            return ExitCode::from(1);
        }
    };
    if let Some(path) = arg_value(&args, "-o").or_else(|| arg_value(&args, "--out")) {
        if let Err(e) = fs::write(PathBuf::from(path), &json) {
            eprintln!("error: {e}");
            return ExitCode::from(1);
        }
    } else {
        print!("{json}");
    }
    ExitCode::SUCCESS
}
