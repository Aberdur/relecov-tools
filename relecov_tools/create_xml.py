from email import utils
import json as j
import xml.etree.cElementTree as e


class xml_creation:
    def __init__(self, source_path=None, output_path=None):
        if source_path is None:
            self.source_path = utils.prompt_source_path()
        else:
            self.source_path = source_path
        if output_path is None:
            self.output_path = utils.prompt_destination_path()
        else:
            self.output_path = output_path

        # LOAD VALIDATED json
        with open(self.source_path) as json_format_file:
            json_data = j.load(json_format_file)

        # project_relecov.xml
        r = e.Element("PROJECT_SET")
        project = e.SubElement(r, "PROJECT")
        project.set("alias", "RELECOV")
        e.SubElement(
            project, "TITLE"
        ).text = "Example project for ENA submission RELECOV"
        e.SubElement(
            project, "DESCRIPTION"
        ).text = "This study was created as part of an ENA submissions example RELECOV"
        submission = e.SubElement(project, "SUBMISSION_PROJECT")
        e.SubElement(submission, "SEQUENCING_PROJECT")
        a = e.ElementTree(r)
        a.write("project_relecov.xml")

        # sample_relecov.xml
        data_keys = list(json_data.keys())
        r = e.Element("SAMPLE_SET")
        sample = e.SubElement(r, "SAMPLE")
        sample.set("alias", "SARS Sample 1 programmatic")
        e.SubElement(sample, "TITLE").text = "SARS Sample 1"
        sample_name = e.SubElement(sample, "SAMPLE_NAME")
        e.SubElement(sample_name, "TAXON_ID").text = "2697049"
        e.SubElement(
            sample_name, "SCIENTIFIC_NAME"
        ).text = "Severe acute respiratory syndrome coronavirus 2"
        e.SubElement(sample, "DESCRIPTION").text = "SARS-CoV-2 Sample #1"
        sample_attributes = e.SubElement(sample, "SAMPLE_ATTRIBUTES")
        for i in json_data:
            sample_attribute = e.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
            e.SubElement(sample_attribute, "TAG").text = str(i)
            e.SubElement(sample_attribute, "VALUE").text = json_data[i]
