import glob
import os
import shutil

from antismash.common import path
from antismash.common.html_renderer import FileTemplate
from antismash.common.layers import OptionsLayer as _OriginalOptionsLayer, RecordLayer
from antismash.common.module_results import ModuleResults
from antismash.common.secmet import Record
from antismash.custom_typing import AntismashModule
from antismash.config import ConfigType
from antismash.outputs import html as _original_html
from antismash.outputs.html import (
    check_options,
    check_prereqs,
    get_arguments,
    is_enabled,
    write as _original_write,
)
from antismash.outputs.html.generator import (
    TEMPLATE_PATH,
    build_antismash_js_url,
    build_json_data,
    docs_link,
    generate_html_sections,
    generate_searchgtr_htmls,
    tfbs,
    tta,
    write_regions_js,
)

NAME = _original_html.NAME
SHORT_DESCRIPTION = "experimentalSMASH HTML override"


class OptionsLayer(_OriginalOptionsLayer):
    @property
    def base_url(self):
        return "https://experimentalsmash.secondarymetabolites.org"


def write(records: list[Record], results: list[dict[str, ModuleResults]],
          options: ConfigType, all_modules: list[AntismashModule]) -> None:
    """ Writes all results to a webpage, where applicable. Writes to options.output_dir

        Arguments:
            records: the list of Records for which results exist
            results: a list of dictionaries containing all module results for records
            options: antismash config object

        Returns:
            None
    """
    # do everything the normal function does
    _original_write(records, results, options, all_modules)
    # then copy the extra images across
    source = path.get_full_path(__file__, "images", "*")
    target_dir = os.path.join(options.output_dir, "images")
    for filename in glob.glob(source):
        shutil.copy2(filename, target_dir)


def generate_webpage(records: list[Record], results: list[dict[str, ModuleResults]],
                     options: ConfigType, all_modules: list[AntismashModule]) -> str:
    """ Generates the HTML itself """

    generate_searchgtr_htmls(records, options)
    json_records, js_domains, js_results = build_json_data(records, results, options, all_modules)
    write_regions_js(json_records, options.output_dir, js_domains, js_results)

    template = FileTemplate(os.path.join(path.get_full_path(__file__, "templates", "overview.html")),
                            extra_paths=[TEMPLATE_PATH])

    options_layer = OptionsLayer(options, all_modules)
    record_layers_with_regions = []
    record_layers_without_regions = []
    results_by_record_id: dict[str, dict[str, ModuleResults]] = {}
    for record, record_results in zip(records, results):
        if record.get_regions():
            record_layers_with_regions.append(RecordLayer(record, None, options_layer))
        else:
            record_layers_without_regions.append(RecordLayer(record, None, options_layer))
        results_by_record_id[record.id] = record_results

    regions_written = sum(len(record.get_regions()) for record in records)
    job_id = os.path.basename(options.output_dir)
    page_title = options.output_basename
    if options.html_title:
        page_title = options.html_title

    html_sections = generate_html_sections(record_layers_with_regions, results_by_record_id, options)

    svg_tooltip = ("Shows the layout of the region, marking coding sequences and areas of interest. "
                   "Clicking a gene will select it and show any relevant details. "
                   "Clicking an area feature (e.g. a candidate cluster) will select all coding "
                   "sequences within that area. Double clicking an area feature will zoom to that area. "
                   "Multiple genes and area features can be selected by clicking them while holding the Ctrl key."
                   )
    doc_target = "understanding_output/#the-antismash-5-region-concept"
    svg_tooltip += f"<br>More detailed help is available {docs_link('here', doc_target)}."

    as_js_url = build_antismash_js_url(options)

    content = template.render(records=record_layers_with_regions, options=options_layer,
                              version=options.version, extra_data=js_domains,
                              regions_written=regions_written, sections=html_sections,
                              results_by_record_id=results_by_record_id,
                              config=options, job_id=job_id, page_title=page_title,
                              records_without_regions=record_layers_without_regions,
                              svg_tooltip=svg_tooltip, get_region_css=_original_html.js.get_region_css,
                              as_js_url=as_js_url, tta_name=tta.__name__,
                              tfbs_name=tfbs.__name__,
                              )
    return content

_original_html.generate_webpage = generate_webpage
