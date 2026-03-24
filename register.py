import argparse
from pathlib import Path

from pySC import generate_SC
from pySC.configuration.load_config import load_yaml

# CS injection keys (not configuration keys)

INJECTION = [
    "x",
    "px",
    "y",
    "py",
    "tau",
    "delta",
    "betx",
    "alfx",
    "bety",
    "alfy",
    "x_error_syst",
    "px_error_syst",
    "y_error_syst",
    "py_error_syst",
    "tau_error_syst",
    "delta_error_syst",
    "x_error_stat",
    "px_error_stat",
    "y_error_stat",
    "py_error_stat",
    "tau_error_stat",
    "delta_error_stat",
    "gemit_x",
    "gemit_y",
    "bunch_length",
    "energy_spread",
    "n_particles"
]


def parse():
    parser = argparse.ArgumentParser(description="SC test")
    parser.add_argument("--configuration", default="configuration.yaml", help="Configuration")
    parser.add_argument("--seed", type=int, default=1, help="SC random seed")
    return parser.parse_args()


def get_names(SC, indices):
    return [SC.lattice.design[int(index)].FamName for index in indices]


def get_indices(names):
    return sorted({int(name.split("/")[0]) for name in names})

def main():

    args = parse()
    path = Path(args.configuration)
    configuration = load_yaml(str(path))

    print("------------------------------------------------------")
    print("Options")
    print("------------------------------------------------------")
    print(f"Config file: {path.resolve()}")
    print(f"Seed: {args.seed}")
    print()

    print("Generating SC...")
    SC = generate_SC(str(path), seed=args.seed)
    print("Done...")

    print("------------------------------------------------------")
    print("Lattice")
    print("------------------------------------------------------")
    print(f"file: {SC.configuration['lattice']['lattice_file']}")
    print(f"simulator: {SC.configuration['lattice']['simulator']}")
    print(f"elements: {len(SC.lattice.design)}")
    print(f"bpms: {len(SC.bpm_system.names)}")
    print(f"tuning correctors: {len(SC.tuning.CORR)}")
    print()

    print("------------------------------------------------------")
    print("Injection (input)")
    print("------------------------------------------------------")
    injection = configuration.get("injection", {})
    for key, value in injection.items():
        print(f"{key}: {value}")
    print()

    print("------------------------------------------------------")
    print("Injection (SC)")
    print("------------------------------------------------------")
    for field in INJECTION:
        if hasattr(SC.injection, field):
            print(f"{field}: {getattr(SC.injection, field)}")
    print()

    print("------------------------------------------------------")
    print("Magnets")
    print("------------------------------------------------------")
    for family_name in SC.magnet_arrays.keys():
        indices = SC.magnet_arrays[family_name]
        names = get_names(SC, indices)
        unique_names = list(dict.fromkeys(names))
        print(f"{family_name}: {len(indices)} magnets")
        print(f"  names: {unique_names}")
    print()

    print("------------------------------------------------------")
    print("Control")
    print("------------------------------------------------------")
    for family_name in SC.control_arrays.keys():
        controls = SC.control_arrays[family_name]
        control_indices = get_indices(controls)
        family_names = get_names(SC, control_indices)
        print(f"{family_name}: {len(controls)} controls")
        print(f"  controls: {controls}")
        print(f"  families: {family_names}")
    print()

    print("------------------------------------------------------")
    print("BPMs")
    print("------------------------------------------------------")
    print(f"count: {len(SC.bpm_system.names)}")
    print(f"names: {SC.bpm_system.names}")
    print()

    print("------------------------------------------------------")
    print("RF")
    print("------------------------------------------------------")
    for rf_name, rf_conf in configuration.get("rf", {}).items():
        print(f"{rf_name}: regex={rf_conf.get('regex')}")
    print()

    print("------------------------------------------------------")
    print("Supports")
    print("------------------------------------------------------")
    for idx, support in enumerate(configuration.get("supports", []), start=1):
        print(
            f"{idx}: name={support.get('name')} "
            f"start_regex={support.get('start_endpoints', {}).get('regex')} "
            f"end_regex={support.get('end_endpoints', {}).get('regex')}"
        )
    print()

    print("------------------------------------------------------")
    print("Tuning")
    print("------------------------------------------------------")
    print(f"HCORR: {len(SC.tuning.HCORR)} controls")
    print(f"VCORR: {len(SC.tuning.VCORR)} controls")
    print(f"multipoles: {len(SC.tuning.multipoles)} controls")
    print(f"bba magnets: {len(SC.tuning.bba_magnets)} controls")
    print(f"tune controls 1: {len(SC.tuning.tune.controls_1)}")
    print(f"tune controls 2: {len(SC.tuning.tune.controls_2)}")
    print(f"c_minus controls: {len(SC.tuning.c_minus.controls)}")
    print(f"HCORR: {SC.tuning.HCORR}")
    print(f"VCORR: {SC.tuning.VCORR}")
    print(f"tune controls 1: {SC.tuning.tune.controls_1}")
    print(f"tune controls 2: {SC.tuning.tune.controls_2}")
    print(f"c_minus: {SC.tuning.c_minus.controls}")
    print()


if __name__ == "__main__":
    main()
