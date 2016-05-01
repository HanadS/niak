"""
This module is an executable that should be able
- to create a niak target and, give it a name (default is version_number).
- to update the target link in the niak distro.
- push the target to a git repo (or lfs) with the name as a tag.

@ TODO: Have the release made from specific commit using hash numbers.
"""


import argparse
import logging
import os
import sys

sys.path.append("../")

try:
    from ..pyniak import config
    from ..pyniak import process
except SystemError:
    from pyniak import config
    from pyniak import process


# @TODO Write doc!
__author__ = 'Pierre-Olivier Quirion <pioliqui@gmail.com>'

def main(args=None):


    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Create and release new Niak target')

    parser.add_argument('--branch', '-b', help='the niak branch where to put the version')

    parser.add_argument('--dry_run', '-d', action='store_true', help='no commit no push!')

    parser.add_argument('--niak_path', '-N', help='the path to the Niak repo',
                        default=config.NIAK.PATH)

    parser.add_argument('--niak_url', '-O', help='the url to the Niak git repo',
                        default=config.NIAK.URL)

    parser.add_argument('--psom_path', '-P', help='the path to the Niak repo',
                        default=config.PSOM.PATH)

    parser.add_argument('--psom_url', '-M', help='the url to the Niak git repo',
                        default=config.PSOM.URL)




    parser.add_argument('--release_target', '-r', action='store_true', help='If True, will push the target to the'
                                                                     'repo and update Niak so niak_test_all point '
                                                                     'to the target')

    parser.add_argument('--no_niak_release', '-n', action='store_false', help='Will not push niak to '
                                                                              'url repo if this option is given')

    parser.add_argument('--redo_target', '-R', help='will recompute target event if already present')


    parser.add_argument('--target_path', '-T', help='the path to the target ',
                        default=config.TARGET.PATH)

    parser.add_argument('--target_url', '-U', help='the url to the target',
                        default=config.TARGET.URL)

    parser.add_argument('--target_name', '-G', help='the name of the target ',
                        default=config.TARGET.TAG_NAME)



    parser.add_argument('--target_work_dir', '-w', help='the path to the Target work dir',
                        default=config.TARGET.WORK_DIR)


    # parser.add_argument('--hash', '-h', help='the hash number of the niak version')


    parsed = parser.parse_args(args)

    new_target = process.TargetRelease(dry_run=parsed.dry_run,
                                       niak_path=parsed.niak_path,
                                       niak_url=parsed.niak_url,
                                       target_path=parsed.target_path,
                                       target_name=parsed.target_name,
                                       work_dir=parsed.target_work_dir,
                                       new_target=parsed.release_target,
                                       psom_path=parsed.psom_path,
                                       psom_url=parsed.psom_url)  # ,
                                       # no_niak_release=parser.no_niak_release)


    new_target.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
