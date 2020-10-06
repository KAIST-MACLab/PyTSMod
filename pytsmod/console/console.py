import sys
sys.path.append('./')

import soundfile as sf
from pytsmod import ola, wsola
from pytsmod import phase_vocoder as pv
from pytsmod import phase_vocoder_int as pv_int
from pytsmod import __path__ as path

import configparser
import argparse


def run():
    c = configparser.ConfigParser()
    c.read(path[0] + '/console/descs.conf')
    c = c['DEFAULT']

    a_parser = argparse.ArgumentParser(description=c['TSMOD_DESC'])
    subparsers = a_parser.add_subparsers(help=c['SUBPARSER_HELP'],
                                         dest='subparser_name')

    # create parser for OLA.
    parser_ola = subparsers.add_parser('ola', help=c['OLA_HELP'],
                                       description=c['OLA_DESC'])
    parser_ola.add_argument('input_file', type=str, help=c['INPUT_HELP'])
    parser_ola.add_argument('output_file', type=str, help=c['OUTPUT_HELP'])
    parser_ola.add_argument('alpha', type=float, help=c['A_HELP'])
    parser_ola.add_argument('--win_type', '-wt', default='hann', type=str,
                            help=c['WT_HELP'])
    parser_ola.add_argument('--win_size', '-ws', default=1024, type=int,
                            help=c['WS_HELP'])
    parser_ola.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                            help=c['SH_HELP'])

    # create parser for WSOLA.
    parser_wsola = subparsers.add_parser('wsola', help=c['WSOLA_HELP'],
                                         description=c['WSOLA_DESC'])
    parser_wsola.add_argument('input_file', type=str, help=c['INPUT_HELP'])
    parser_wsola.add_argument('output_file', type=str, help=c['OUTPUT_HELP'])
    parser_wsola.add_argument('alpha', type=float, help=c['A_HELP'])
    parser_wsola.add_argument('--win_type', '-wt', default='hann', type=str,
                              help=c['WT_HELP'])
    parser_wsola.add_argument('--win_size', '-ws', default=1024, type=int,
                              help=c['WS_HELP'])
    parser_wsola.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                              help=c['SH_HELP'])
    parser_wsola.add_argument('--tolerance', '-t', default=512, type=int,
                              help=c['TOL_HELP'])

    # create parser for phase-vocoder.
    parser_pv = subparsers.add_parser('pv', help=c['PV_HELP'],
                                      description=c['PV_DESC'])
    parser_pv.add_argument('input_file', type=str, help=c['INPUT_HELP'])
    parser_pv.add_argument('output_file', type=str, help=c['OUTPUT_HELP'])
    parser_pv.add_argument('alpha', type=float, help=c['A_HELP'])
    parser_pv.add_argument('--win_type', '-wt', default='sin', type=str,
                           help=c['WT_HELP'])
    parser_pv.add_argument('--win_size', '-ws', default=2048, type=int,
                           help=c['WS_HELP'])
    parser_pv.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                           help=c['SH_HELP'])
    parser_pv.add_argument('--zero_pad', '-z', default=0, type=int,
                           help=c['ZP_HELP'])
    parser_pv.add_argument('--restore_energy', '-e', action='store_true',
                           help=c['RE_HELP'])
    parser_pv.add_argument('--fft_shift', '-fs', action='store_true',
                           help=c['FS_HELP'])
    parser_pv.add_argument('--phase_lock', '-pl', action='store_true',
                           help=c['PL_HELP'])

    # create parser for phase-vocoder int.
    parser_pvi = subparsers.add_parser('pv_int', help=c['PVI_HELP'],
                                       description=c['PVI_DESC'])
    parser_pvi.add_argument('input_file', type=str, help=c['INPUT_HELP'])
    parser_pvi.add_argument('output_file', type=str, help=c['OUTPUT_HELP'])
    parser_pvi.add_argument('alpha', type=int, help=c['A_PVI_HELP'])
    parser_pvi.add_argument('--win_type', '-wt', default='hann', type=str,
                            help=c['WT_HELP'])
    parser_pvi.add_argument('--win_size', '-ws', default=2048, type=int,
                            help=c['WS_HELP'])
    parser_pvi.add_argument('--syn_hop_size', '-sh', default=512, type=int,
                            help=c['SH_HELP'])
    parser_pvi.add_argument('--zero_pad', '-z', default=None, type=int,
                            help=c['ZP_HELP'])
    parser_pvi.add_argument('--restore_energy', '-e', action='store_true',
                            help=c['RE_HELP'])
    parser_pvi.add_argument('--fft_shift', '-fs', action='store_true',
                            help=c['FS_HELP'])

    args = a_parser.parse_args()

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
