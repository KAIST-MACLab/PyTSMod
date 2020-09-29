import sys
sys.path.append('./')

from pytsmod import ola, wsola
from pytsmod import phase_vocoder as pv
from pytsmod import phase_vocoder_int as pv_int
import argparse
import soundfile as sf


def run():
    parser = argparse.ArgumentParser(description='Processing time-scale modification for given audio file.')
    parser.add_argument('algorithm', nargs='?', choices=['ola', 'wsola', 'pv', 'pv_int', 'hp'])
    # parser.add_argument('--help', action='store_true')

    args, sub_args = parser.parse_known_args()

    if args.algorithm == 'ola':
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', type=str)
        parser.add_argument('output_file', type=str)
        parser.add_argument('alpha', type=float)
        parser.add_argument('--win_type', '-wt', default='hann', type=str)
        parser.add_argument('--win_size', '-ws', default=1024, type=int)
        parser.add_argument('--syn_hop_size', '-sh', default=512, type=int)

        params = parser.parse_args(sub_args)

        x, sr = sf.read(params.input_file)

        y = ola(x, params.alpha, win_type=params.win_type,
                win_size=params.win_size, syn_hop_size=params.syn_hop_size)
    elif args.algorithm == 'wsola':
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', type=str)
        parser.add_argument('output_file', type=str)
        parser.add_argument('alpha', type=float)
        parser.add_argument('--win_type', '-wt', default='hann', type=str)
        parser.add_argument('--win_size', '-ws', default=1024, type=int)
        parser.add_argument('--syn_hop_size', '-sh', default=512, type=int)
        parser.add_argument('--tolerance', '-t', default=512, type=int)

        params = parser.parse_args(sub_args)

        x, sr = sf.read(params.input_file)

        y = wsola(x, params.alpha, win_type=params.win_type,
                  win_size=params.win_size, syn_hop_size=params.syn_hop_size,
                  tolerance=params.tolerance)
    elif args.algorithm == 'pv':
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', type=str)
        parser.add_argument('output_file', type=str)
        parser.add_argument('alpha', type=float)
        parser.add_argument('--win_type', '-wt', default='sin', type=str)
        parser.add_argument('--win_size', '-ws', default=2048, type=int)
        parser.add_argument('--syn_hop_size', '-sh', default=512, type=int)
        parser.add_argument('--zero_pad', '-z', default=0, type=int)
        parser.add_argument('--restore_energy', '-e', action='store_true')
        parser.add_argument('--fft_shift', '-fs', action='store_true')
        parser.add_argument('--phase_lock', '-pl', action='store_true')

        params = parser.parse_args(sub_args)

        x, sr = sf.read(params.input_file)

        y = pv(x, params.alpha, win_type=params.win_type,
               win_size=params.win_size, syn_hop_size=params.syn_hop_size,
               zero_pad=params.zero_pad, restore_energy=params.restore_energy,
               fft_shift=params.fft_shift, phase_lock=params.phase_lock)
    elif args.algorithm == 'pv_int':
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', type=str)
        parser.add_argument('output_file', type=str)
        parser.add_argument('alpha', type=int)
        parser.add_argument('--win_type', '-wt', default='hann', type=str)
        parser.add_argument('--win_size', '-ws', default=2048, type=int)
        parser.add_argument('--syn_hop_size', '-sh', default=512, type=int)
        parser.add_argument('--zero_pad', '-z', default=None, type=int)
        parser.add_argument('--restore_energy', '-e', action='store_true')
        parser.add_argument('--fft_shift', '-fs', action='store_true')

        params = parser.parse_args(sub_args)
        print(params.zero_pad)

        x, sr = sf.read(params.input_file)

        y = pv_int(x, params.alpha, win_type=params.win_type,
                   win_size=params.win_size, syn_hop_size=params.syn_hop_size,
                   zero_pad=params.zero_pad,
                   restore_energy=params.restore_energy,
                   fft_shift=params.fft_shift)
    # elif args.algorithm == 'hp':
    #     pass

    sf.write(params.output_file, y, sr)


if __name__ == '__main__':
    run()
