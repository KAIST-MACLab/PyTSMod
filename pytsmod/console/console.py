import sys
sys.path.append('./')

from pytsmod import ola, wsola
from pytsmod import phase_vocoder as pv
from pytsmod import phase_vocoder_int as pv_int
from pytsmod.console import *
import argparse
import soundfile as sf


def run():
    parser = argparse.ArgumentParser(description=TSMOD_DESC)
    subparsers = parser.add_subparsers(help=SUBPARSER_HELP,
                                       dest='subparser_name')

    # create parser for OLA.
    parser_ola = subparsers.add_parser('ola', help=OLA_HELP,
                                       description=OLA_DESC)
    parser_ola.add_argument('input_file', type=str, help=INPUT_HELP)
    parser_ola.add_argument('output_file', type=str, help=OUTPUT_HELP)
    parser_ola.add_argument('alpha', type=float, help=A_HELP)
    parser_ola.add_argument('--win_type', '-wt', default='hann', type=str,
                            help=WT_HELP)
    parser_ola.add_argument('--win_size', '-ws', default=1024, type=int,
                            help=WS_HELP)
    parser_ola.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                            help=SH_HELP)

    # create parser for WSOLA.
    parser_wsola = subparsers.add_parser('wsola', help=WSOLA_HELP,
                                         description=WSOLA_DESC)
    parser_wsola.add_argument('input_file', type=str, help=INPUT_HELP)
    parser_wsola.add_argument('output_file', type=str, help=OUTPUT_HELP)
    parser_wsola.add_argument('alpha', type=float, help=A_HELP)
    parser_wsola.add_argument('--win_type', '-wt', default='hann', type=str,
                              help=WT_HELP)
    parser_wsola.add_argument('--win_size', '-ws', default=1024, type=int,
                              help=WS_HELP)
    parser_wsola.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                              help=SH_HELP)
    parser_wsola.add_argument('--tolerance', '-t', default=512, type=int,
                              help=TOL_HELP)

    # create parser for phase-vocoder.
    parser_pv = subparsers.add_parser('pv', help=PV_HELP,
                                      description=PV_DESC)
    parser_pv.add_argument('input_file', type=str, help=INPUT_HELP)
    parser_pv.add_argument('output_file', type=str, help=OUTPUT_HELP)
    parser_pv.add_argument('alpha', type=float, help=A_HELP)
    parser_pv.add_argument('--win_type', '-wt', default='sin', type=str,
                           help=WT_HELP)
    parser_pv.add_argument('--win_size', '-ws', default=2048, type=int,
                           help=WS_HELP)
    parser_pv.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                           help=SH_HELP)
    parser_pv.add_argument('--zero_pad', '-z', default=0, type=int,
                           help=ZP_HELP)
    parser_pv.add_argument('--restore_energy', '-e', action='store_true',
                           help=RE_HELP)
    parser_pv.add_argument('--fft_shift', '-fs', action='store_true',
                           help=FS_HELP)
    parser_pv.add_argument('--phase_lock', '-pl', action='store_true',
                           help=PL_HELP)

    # create parser for phase-vocoder int.
    parser_pvi = subparsers.add_parser('pv_int', help=PVI_HELP,
                                       description=PVI_DESC)
    parser_pvi.add_argument('input_file', type=str, help=INPUT_HELP)
    parser_pvi.add_argument('output_file', type=str, help=OUTPUT_HELP)
    parser_pvi.add_argument('alpha', type=int, help=A_PVI_HELP)
    parser_pvi.add_argument('--win_type', '-wt', default='hann', type=str,
                            help=WT_HELP)
    parser_pvi.add_argument('--win_size', '-ws', default=2048, type=int,
                            help=WS_HELP)
    parser_pvi.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                            help=SH_HELP)
    parser_pvi.add_argument('--zero_pad', '-z', default=None, type=int,
                            help=ZP_HELP)
    parser_pvi.add_argument('--restore_energy', '-e', action='store_true',
                            help=RE_HELP)
    parser_pvi.add_argument('--fft_shift', '-fs', action='store_true',
                            help=FS_HELP)

    args = parser.parse_args()

    x, sr = sf.read(args.input_file)

    if args.subparser_name == 'ola':
        y = ola(x, args.alpha, win_type=args.win_type, win_size=args.win_size,
                syn_hop_size=args.syn_hop_size)
    elif args.subparser_name == 'wsola':
        y = wsola(x, args.alpha, win_type=args.win_type,
                  win_size=args.win_size, syn_hop_size=args.syn_hop_size,
                  tolerance=args.tolerance)
    elif args.subparser_name == 'pv':
        y = pv(x, args.alpha, win_type=args.win_type, win_size=args.win_size,
               syn_hop_size=args.syn_hop_size, zero_pad=args.zero_pad,
               restore_energy=args.restore_energy, fft_shift=args.fft_shift,
               phase_lock=args.phase_lock)
    elif args.subparser_name == 'pv_int':
        y = pv_int(x, args.alpha, win_type=args.win_type,
                   win_size=args.win_size, syn_hop_size=args.syn_hop_size,
                   zero_pad=args.zero_pad,
                   restore_energy=args.restore_energy,
                   fft_shift=args.fft_shift)
    # elif args.subparser_name == 'hp':
    #     pass

    sf.write(args.output_file, y.T, sr)


if __name__ == '__main__':
    run()
