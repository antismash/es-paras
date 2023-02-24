# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.
"""Run experimentalSMASH - PARAS"""

import sys

import antismash
import antismash.modules.nrps_pks
from antismash.__main__ import main as as_main

import es_paras
import es_paras.overrides


antismash.modules.nrps_pks.specific_analysis = es_paras.overrides.specific_analysis


def main(args: list[str]) -> int:
    """Run experimentalSMASH - PARAS"""
    return as_main(args)


def entrypoint() -> None:
    """This is needed for the script generated by setuptools."""
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__':
    entrypoint()