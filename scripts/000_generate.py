#!/usr/bin/env python

import argparse
from pathlib import Path

from pySC import generate_SC

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--factor', type=float, default=1.0, help='multiplication factor for all errors')
    parser.add_argument('--cut', type=float, default=2.0, help='random error distribution cut')
    parser.add_argument('--seed', type=int, default=1, help='random seed (run id)')
    parser.add_argument('--config', default='configuration.yaml', help='configuration file')
    parser.add_argument('--machine', default='elettra', help='output file prefix')
    parser.add_argument('--data', default='data', help='data directory path')
    return parser.parse_args()


def main():

    arguments = parser()

    sc = generate_SC(
        arguments.config,
        seed=arguments.seed,
        scale_errors=arguments.factor,
        sigma_truncate=arguments.cut
    )

    path = Path(arguments.data)
    sc.import_knob(str(path / 'tune_knobs.json'))
    sc.import_knob(str(path / 'c_minus_knobs.json'))

    path = Path("seeds")
    path.mkdir(parents=True, exist_ok=True)
    sc.to_json(path / f"{arguments.machine}_00_seed{arguments.seed}.json")


if __name__ == '__main__':
    print('STARTING...')
    main()
    print('DONE...')

