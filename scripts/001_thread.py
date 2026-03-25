#!/usr/bin/env python

'''
Example:

python scripts/000_generate.py --seed=1 --factor=1.5
python scripts/001_thread.py --seed=1 --get=00 --set=01 --number-of-iterations=16 --run-injection-correction --run-last-corrector-wiggle --injection-regularization=100 --plot
python scripts/001_thread.py --seed=1 --get=01 --set=01 --rewrite --number-of-iterations=16 --run-tune-correction --run-injection-correction --injection-regularization=50 --plot
python scripts/001_thread.py --seed=1 --get=01 --set=01 --rewrite --number-of-iterations=16 --run-injection-correction --injection-regularization=50 --injection-gain=0.5 --plot
python scripts/001_thread.py --seed=1 --get=01 --set=01 --rewrite --number-of-iterations=16 --run-injection-correction --injection-regularization=50 --injection-gain=0.5 --injection-number-of-turns=2 --plot
python scripts/001_thread.py --seed=1 --get=01 --set=01 --rewrite --number-of-iterations=16 --run-tune-correction --run-injection-correction --injection-regularization=50 --injection-number-of-turns=2 --number-of-particles=256 --plot
'''

import argparse
from time import sleep
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from pySC import SimulatedCommissioning
from scipy.constants import alpha

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=1, help='random seed (run id)')
    parser.add_argument('--machine', default='elettra', help='machine name used in stage file names')
    parser.add_argument('--data', default='data', help='data directory path')
    parser.add_argument('--get', default='00', help='stage to get')
    parser.add_argument('--set', default='01', help='stage to set')
    parser.add_argument('--sleep', type=float, default=1.0, help='sleep time')
    parser.add_argument('--rewrite', action='store_true', help='overwrite the loaded input stage')
    parser.add_argument('--number-of-iterations', type=int, default=10, help='total number of iterations')
    parser.add_argument('--number-of-particles', type=int, default=1, help='number of particles')
    parser.add_argument('--transmission-threshold', type=float, default=0.4, help='beam transmission threshold')
    parser.add_argument('--enable-multipoles', action='store_true', help='flag to enable multipoles')
    parser.add_argument('--run-tune-correction', action='store_true', help='flag to run tune correction')
    parser.add_argument('--tune-number-of-iterations', type=int, default=1, help='number of tune correction iterations')
    parser.add_argument('--tune-gain', type=float, default=0.5, help='tune knobs gain')
    parser.add_argument('--tune-measurement-method', default='first_turn', help='tune measurement method passed')
    parser.add_argument('--run-injection-correction', action='store_true', help='flag to run injection correction')
    parser.add_argument('--injection-regularization', type=float, default=10, help='regularization parameter')
    parser.add_argument('--injection-number-of-repetitions', type=int, default=10, help='number of repeated orbit correction solves per injection correction call')
    parser.add_argument('--injection-number-of-turns', type=int, default=1, help='number of turns used for injection correction')
    parser.add_argument('--injection-gain', type=float, default=0.8, help='injection knobs gain')
    parser.add_argument('--run-last-corrector-wiggle', action='store_true', help='run last corrector wiggle')
    parser.add_argument('--wiggle-maximum-number-of-steps', type=int, default=100, help='maximum number of random wiggle attempts')
    parser.add_argument('--wiggle-maximum-setpoint', type=float, default=100e-6, help='maximum absolute corrector setpoint')
    parser.add_argument('--corrector-x-maximum', type=float, default=8.0e-4, help='horizontal corrector angle limit (plotting)')
    parser.add_argument('--corrector-y-maximum', type=float, default=5.0e-4, help='vertical corrector angle limit (plotting)')
    parser.add_argument('--plot', action='store_true', help='plot the orbit history during threading')
    return parser.parse_args()


def bpm_data(sc):
    return np.asarray(sc.lattice.twiss['s'][sc.bpm_system.indices], dtype=float)

def corrector_data(sc):
    hcorr_s = []
    hcorr_v = []
    for control in sc.tuning.HCORR:
        magnet_name, *_ = control.split('/')
        magnet_index = sc.magnet_settings.magnets[magnet_name].sim_index
        hcorr_s.append(float(sc.lattice.twiss['s'][magnet_index]))
        hcorr_v.append(float(sc.magnet_settings.get(control)))
    vcorr_s = []
    vcorr_v = []
    for control in sc.tuning.VCORR:
        magnet_name, *_ = control.split('/')
        magnet_index = sc.magnet_settings.magnets[magnet_name].sim_index
        vcorr_s.append(float(sc.lattice.twiss['s'][magnet_index]))
        vcorr_v.append(float(sc.magnet_settings.get(control)))
    return (hcorr_s, hcorr_v), (vcorr_s, vcorr_v)


def length(sc):
    *_, length = sc.lattice.twiss['s']
    return float(length)

def distance(sc, n_turns):
    xs, ys = sc.bpm_system.capture_injection(n_turns=n_turns)
    xs = xs.T.flatten()
    ys = ys.T.flatten()
    for index, (x, y) in enumerate(zip(xs, ys)):
        if np.isnan(x) or np.isnan(y):
            index = index - 1 if index else index
            break        
    size = len(sc.bpm_system.indices)
    *_, length = sc.lattice.twiss['s']
    return (sc.lattice.twiss['s'][sc.bpm_system.indices[index % size]] + length*(index // size))/length


def trajectory(sc, arguments):
    circumference = length(sc)
    s = bpm_data(sc)
    s = np.concatenate([s + turn * circumference for turn in range(arguments.injection_number_of_turns)])
    xs, ys = sc.bpm_system.capture_injection(n_turns=arguments.injection_number_of_turns)
    xs = xs.T.flatten()
    ys = ys.T.flatten()
    return s, 1e6*xs, 1e6*ys


def update(fig, sc, arguments, data_x, data_y, iteration, task, input, output, corrector_x_max, corrector_y_max):
    ss, xs, ys = trajectory(sc, arguments)
    data_x.append(xs.copy())
    data_y.append(ys.copy())
    msg = None
    if arguments.run_tune_correction:
        nux, nuy = sc.tuning.tune.estimate_from_first_turn()
        if nux is not None and nuy is not None:
            msg = f'(Qx, Qy)=({nux:.4f}, {nuy:.4f})'
    if msg is None:
        fraction = distance(sc, max(1, arguments.injection_number_of_turns))
        msg = f'fraction={fraction:.2f} '
    rms_x = float(np.nanstd(xs))
    rms_y = float(np.nanstd(ys))
    (hcorr_s, hcorr_v), (vcorr_s, vcorr_v) = corrector_data(sc)
    hcorr_v = 1e6*np.asarray(hcorr_v)
    vcorr_v = 1e6*np.asarray(vcorr_v)
    corrector_x_max *= 1e6
    corrector_y_max *= 1e6
    fig.clear()
    (ax, ay, az) = fig.subplots(3, 1, sharex=False, gridspec_kw={'height_ratios': [1.0, 1.0, 1.0]},)
    for axis, history, plane in zip(  (ax, ay, az), (data_x, data_y), ('x', 'y'), strict=False):
        for s in ss:
            axis.axvline(s, color='gray', linewidth=0.5, alpha=0.25, zorder=0)
        *most, last = history
        for previous in most:
            axis.plot(ss, previous, color='gray', alpha=0.25)
        axis.plot(ss, last, color='black')
        axis.set_ylim(-5000, 5000)
        axis.set_ylabel(f'{plane} [mkm]')
    ax.set_xlim(0, arguments.injection_number_of_turns*length(sc))
    ax.set_xlabel('s [m]')
    ay.set_xlim(0, arguments.injection_number_of_turns*length(sc))
    ay.set_xlabel('s [m]')
    az.axhline(corrector_x_max, color='red', linestyle='--', linewidth=1.0)
    az.axhline(-corrector_x_max, color='red', linestyle='--', linewidth=1.0)
    az.axhline(corrector_y_max, color='blue', linestyle='--', linewidth=1.0)
    az.axhline(-corrector_y_max, color='blue', linestyle='--', linewidth=1.0)
    if len(hcorr_s):
        az.bar(hcorr_s, hcorr_v, width=0.35, color='r', alpha=0.6)
    if len(vcorr_s):
        az.bar(vcorr_s, vcorr_v, width=0.35, color='b', alpha=0.6)
    for s in bpm_data(sc):
        az.axvline(s, color='gray', linewidth=0.5, alpha=0.25, zorder=0)
    az.set_xlim(0, length(sc))
    az.set_ylim(-1000, 1000)
    az.set_ylabel('corr [mkrad]')
    az.set_xlabel('s [m]')
    title = '\n'.join([
        f'iteration: {iteration}',
        f'task     : {task}',
        f'fraction : {msg}',
        f'input    : {input}',
        f'output   : {output}',
        f'rms      : ({rms_x:.1f}, {rms_y:.1f}) mkm',
        ''
    ])
    fig.suptitle(title, x=0.05, y=0.975, ha='left', va='top', fontfamily='monospace')
    fig.tight_layout()
    plt.pause(0.1)

def main():

    arguments = parser()

    stage = arguments.get if arguments.rewrite else arguments.set
    path = Path('./seeds') / f'{arguments.machine}_{arguments.get}_seed{arguments.seed}.json'
    sc = SimulatedCommissioning.from_json(path)
    sc.tuning.set_multipole_scale(scale=0.0)
    if arguments.enable_multipoles:
        sc.tuning.set_multipole_scale(scale=1.0)

    sc.injection.n_particles = arguments.number_of_particles
    if sc.injection.n_particles > 1:
        sc.bpm_system.transmission_threshold = arguments.transmission_threshold

    data_x = []
    data_y = []
    corrector_x_max = arguments.corrector_x_maximum
    corrector_y_max = arguments.corrector_y_maximum

    figure = None
    if arguments.plot:
        plt.ion()
        figure = plt.figure(num=1, figsize=(12, 8))
        update(figure, sc, arguments, data_x, data_y, 0, 'initial', arguments.get, stage, corrector_x_max, corrector_y_max)
        sleep(arguments.sleep)
        
    for iteration in range(arguments.number_of_iterations):

        if arguments.run_tune_correction:
            sleep(arguments.sleep)
            sc.tuning.tune.correct(
                n_iter=arguments.tune_number_of_iterations,
                gain=arguments.tune_gain,
                measurement_method=arguments.tune_measurement_method
            )
            if arguments.plot:
                update(figure, sc, arguments, data_x, data_y, iteration + 1, 'tune', arguments.get, stage, corrector_x_max, corrector_y_max)

        if arguments.run_injection_correction:
            sleep(arguments.sleep)
            sc.tuning.correct_injection(
                parameter=arguments.injection_regularization,
                n_reps=arguments.injection_number_of_repetitions,
                n_turns=arguments.injection_number_of_turns,
                gain=arguments.injection_gain
            )
            if arguments.plot:
                update(figure, sc, arguments, data_x, data_y, iteration + 1, 'injection', arguments.get, stage, corrector_x_max, corrector_y_max)

        if arguments.run_last_corrector_wiggle:
            sleep(arguments.sleep)
            sc.tuning.wiggle_last_corrector(
                max_steps=arguments.wiggle_maximum_number_of_steps,
                max_sp=arguments.wiggle_maximum_setpoint
            )
            if arguments.plot:
                update(figure, sc, arguments, data_x, data_y, iteration + 1, 'wiggle', arguments.get, stage, corrector_x_max, corrector_y_max)

    path = Path('./seeds') / f'{arguments.machine}_{stage}_seed{arguments.seed}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    sc.to_json(path)

    if arguments.plot:
        plt.ioff()
        plt.show()

if __name__ == '__main__':
    print('STARTING...')
    main()
    print('DONE...')
