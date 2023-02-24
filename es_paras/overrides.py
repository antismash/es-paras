#  License: GNU Affero General Public License v3 or later
#  A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

'''
Override the antiSMASH nrps_pks/specific_analysis.py functions.
'''

import logging

from antismash.common.secmet import Record, Region
from antismash.config import ConfigType

from antismash.modules.nrps_pks.orderfinder import analyse_biosynthetic_order
from antismash.modules.nrps_pks.parsers import calculate_consensus_prediction
from antismash.modules.nrps_pks.results import NRPS_PKS_Results
from antismash.modules.nrps_pks.specific_analysis import get_a_domains_from_cds_features
from antismash.modules.nrps_pks.substrates import run_pks_substr_spec_predictions

from antismash.modules.nrps_pks.nrpys import run_nrpys

from .paras import run_paras


def specific_analysis(
        record: Record,
        results: NRPS_PKS_Results,
        options: ConfigType
        ) -> NRPS_PKS_Results:
    """ Runs the various NRPS/PKS analyses on a record and returns their results """
    nrps_pks_genes = record.get_nrps_pks_cds_features()

    if not nrps_pks_genes:
        logging.debug("No NRPS or PKS genes found, skipping analysis")
        return results

    a_domains = get_a_domains_from_cds_features(record, nrps_pks_genes)
    if a_domains:
        logging.info("Predicting A domain substrate specificities with nrpys")
        results.add_method_results("nrpys", run_nrpys(a_domains, options))
        logging.info("Predicting A domain substrate specificities with PARAS")
        results.add_method_results("paras", run_paras(a_domains))

    pks_results = run_pks_substr_spec_predictions(nrps_pks_genes)
    for method, method_results in pks_results.items():
        results.add_method_results(method, method_results)
    consensus_pair = calculate_consensus_prediction(nrps_pks_genes, results.domain_predictions)
    results.consensus, results.consensus_transat = consensus_pair

    candidate_cluster_predictions = analyse_biosynthetic_order(
        nrps_pks_genes, results.consensus, record)
    for prediction in candidate_cluster_predictions:
        candidate_cluster = record.get_candidate_cluster(prediction.candidate_cluster_number)
        region = candidate_cluster.parent
        assert isinstance(region, Region), type(region)
        results.region_predictions[region.get_region_number()].append(prediction)
    return results
