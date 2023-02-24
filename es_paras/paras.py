#  License: GNU Affero General Public License v3 or later
#  A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

'''
PARAS glue code
'''

from typing import Any

from antismash.common.html_renderer import Markup
from antismash.detection.nrps_pks_domains import ModularDomain
from antismash.modules.nrps_pks.data_structures import Prediction

from paras.run import run_paras_bulk


class ParasResult(Prediction):
    """ Holds all the relevant results from PARAS for an adenylation domain """
    def __init__(self, paras_predictions: list[tuple[float, str]]) -> None:
        super().__init__("PARAS")
        self.predictions = paras_predictions

    def get_classification(self, as_norine: bool = False) -> list[str]:
        if not self.predictions:
            return []

        predictions = [self.predictions[0]]
        for prediction in self.predictions[1:]:
            if prediction[0] == predictions[0][0]:
                predictions.append(prediction)
        return [prediction[1] for prediction in predictions]

    def as_html(self) -> Markup:
        if not self.predictions:
            return Markup("No hits above threshold.")

        raw_start = (
            "<dl><dt>PARAS prediction, score (0-1):</dt>"
            " <dd>"
            "  <dl>"
        )
        core = "\n".join(
            f"<dd></dd><dt>{name}: {score:.2f}</dt>" for score, name in self.predictions)
        raw_end = (
            "  </dl>"
            " </dd>"
            "</dl>"
        )
        return Markup(f"{raw_start}{core}{raw_end}")

    def to_json(self) -> dict[str, Any]:
        return dict(vars(self))

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Prediction:
        """ Creates a Prediction from a JSON representation """
        return ParasResult(json["predictions"])


def run_paras(a_domains: list[ModularDomain]) -> dict[str, Prediction]:
    """Actually run PARAS"""
    results: dict[str, Prediction] = {}
    sequences = []
    for domain in a_domains:
        sequences.append(domain.translation)
    predictions = run_paras_bulk(sequences, threshold=0.2)
    for i, domain in enumerate(a_domains):
        assert domain.domain_id
        prediction = predictions[i]
        results[domain.domain_id] = ParasResult(prediction)

    return results
