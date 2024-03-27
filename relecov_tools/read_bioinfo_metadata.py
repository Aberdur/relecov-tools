#!/usr/bin/env python
import os
import sys
import logging
import glob
import rich.console
from datetime import datetime
from yaml import YAMLError
from bs4 import BeautifulSoup

import relecov_tools.utils
from relecov_tools.config_json import ConfigJson
from relecov_tools.long_table_parse import LongTableParse

# import relecov_tools.json_schema

log = logging.getLogger(__name__)
stderr = rich.console.Console(
    stderr=True,
    style="dim",
    highlight=False,
    force_terminal=relecov_tools.utils.rich_force_colors(),
)

# TODO: Create 2 master function that validates file presence/content and transfrom from csv,tsv,... to json.
# TODO: Cosider eval py + func property in json to be able to discriminate between collated files and sample-specific files.  
class BioinfoMetadata:
    def __init__(
        self,
        readlabmeta_json_file=None,
        input_folder=None,
        output_folder=None,
        software='viralrecon',
    ):
        if readlabmeta_json_file is None:
            readlabmeta_json_file = relecov_tools.utils.prompt_path(
                msg="Select the json file that was created by the read-lab-metadata"
            )
        if not os.path.isfile(readlabmeta_json_file):
            log.error("json file %s does not exist ", readlabmeta_json_file)
            stderr.print(f"[red] file {readlabmeta_json_file} does not exist")
            sys.exit(1)
        self.readlabmeta_json_file = readlabmeta_json_file

        if input_folder is None:
            self.input_folder = relecov_tools.utils.prompt_path(
                msg="Select the input folder"
            )
        else:
            self.input_folder = input_folder
        if output_folder is None:
            self.output_folder = relecov_tools.utils.prompt_path(
                msg="Select the output folder"
            )
        else:
            self.output_folder = output_folder
        
        self.bioinfo_json_file = os.path.join(os.path.dirname(__file__), "conf", "bioinfo_config.json")
        if software is None:
            software = relecov_tools.utils.prompt_path(
                msg="Select the software, pipeline or tool use in the bioinformatic analysis: "
            )
        self.software_name = software

        available_software = self.get_available_software(self.bioinfo_json_file)
        bioinfo_config = ConfigJson(self.bioinfo_json_file)
        if self.software_name in available_software:
            self.software_config = bioinfo_config.get_configuration(self.software_name)
        else:
            log.error(
                "No configuration available for %s. Currently, the only available software options are: %s", self.software_name, ", ".join(available_software)
            )
            stderr.print(f"[red]No configuration available for {self.software_name}. Currently, the only available software options are:: {', '.join(available_software)}")
            sys.exit(1)
        self.log_report = {'error': {}, 'valid': {}, 'warning': {}}
    
    def get_available_software(self, json):
        """Get list of available software in configuration"""
        config = relecov_tools.utils.read_json_file(json)
        available_software = list(config.keys())
        return available_software
    
    def update_log_report(self, method_name, status, message):
        if status == 'valid':
            self.log_report['valid'].setdefault(method_name, []).append(message)
        elif status == 'error':
            self.log_report['error'].setdefault(method_name, []).append(message)
        elif status == 'warning':
            self.log_report['warning'].setdefault(method_name, []).append(message)
        else:
            raise ValueError("Invalid status provided.")

    # TODO: Add log report
    def scann_directory(self):
        """Scanns bioinfo analysis directory and identifies files according to the file name patterns defined in the software configuration json."""
        total_files = sum(len(files) for _, _, files in os.walk(self.input_folder))
        files_found = {}

        for topic_key, topic_details  in self.software_config.items():
            if 'fn' not in topic_details: #try/except fn
                continue
            for root, _, files in os.walk(self.input_folder, topdown=True):
                matching_files = [os.path.join(root, file_name) for file_name in files if file_name.endswith(topic_details['fn'])]
                if len(matching_files) >= 1:
                    files_found[topic_key] = matching_files
        if len(files_found) < 1:
            self.update_log_report(
                self.scann_directory.__name__,
                'error', 
                f"No files found in {self.input_folder}"
            )
            log.error(
                "\tNo files found in %s according to %s file name patterns..",
                self.input_folder,
                os.path.basename(self.bioinfo_json_file)
            )
            stderr.print(f"\t[red]No files found in {self.input_folder} according to {os.path.basename(self.bioinfo_json_file)} file name patterns.")
            sys.exit(1)
        else:
            self.update_log_report(
                self.scann_directory.__name__,
                'valid', 
                "Scannig process succeed"
            )
            stderr.print(f"\t[green]Scannig process succeed (total scanned files: {total_files}).")
            return files_found

    def add_filepaths_to_software_config(self, files_dict):
        """
        Adds file paths to the software configuration JSON by creating the 'file_paths' property with files found during the scanning process.
        """
        cc = 0
        extended_software_config = self.software_config
        for key, value in files_dict.items():
            if key in extended_software_config:
                if len(value) != 0 or value:
                    extended_software_config[key]['file_paths'] = value
                    cc+=1
        if cc == 0:
            self.update_log_report(
                self.add_filepaths_to_software_config.__name__,
                'error', 
                "No files path added to configuration json"
            )
        else:
            self.update_log_report(
                self.add_filepaths_to_software_config.__name__,
                'valid', 
                "Files path added to configuration json"
            )
            stderr.print("\t[green]Files path added to their scope in bioinfo configuration file.")
        return extended_software_config

    def validate_software_mandatory_files(self, json):
        missing_required = []
        for key in json.keys():
            if json[key].get('required') is True:
                try:
                    json[key]['file_paths']
                    self.update_log_report(
                        self.validate_software_mandatory_files.__name__,
                        'valid', 
                        f"Found '{json[key]['fn']}'"
                    )
                except KeyError:
                    missing_required.append(key)
                    self.update_log_report(
                        self.validate_software_mandatory_files.__name__,
                        'error', 
                        f"Missing '{json[key]['fn']}'"
                    )
            else:
                continue
        if len(missing_required) >= 1:
            log.error("\tMissing required files:")
            stderr.print("[red]\tMissing required files:")
            for i in missing_required:
                log.error("\t- %s", i)
                stderr.print(f"[red]\t- {i} (file name expected pattern '{json[i]['fn']}')")
            sys.exit(1)
        else:
            stderr.print("[green]\tValidation passed.")
        return

    def add_bioinfo_results_metadata(self, bioinfo_dict, j_data):
        """
        Adds metadata from bioinformatics results to the JSON data.
        
        This method iterates over each property in the provided bioinfo_dict, which contains information about file paths (discovered during the scanning process), along with their specific file configuration.
        
        If the property specifies files per sample, it maps metadata for each sample-specific file.
        If the property specifies collated files.
        """
        for key in bioinfo_dict.keys():
            try:
                bioinfo_dict[key]['file_paths']
            except KeyError:
                self.update_log_report(
                    self.add_bioinfo_results_metadata.__name__,
                    'warning', 
                    f"No file path found for '{self.software_name}.{key}'"
                )
                continue
            # Parses sample-specific files (i.e: SAMPLE1.consensus.fa)
            if bioinfo_dict[key].get('file_per_sample') is True:
                j_data_mapped = self.map_metadata_persample_files(
                    bioinfo_dict[key],
                    j_data
                )
            # Parses collated files (i.e: mapping_illumina_stats.tab)
            elif bioinfo_dict[key].get('file_per_sample') is False:
                if len(bioinfo_dict[key].get('file_paths')) == 1:
                    bioinfo_dict[key]['file_paths'] = bioinfo_dict[key]['file_paths'][0]
                    j_data_mapped = self.map_metadata_collated_files(
                        bioinfo_dict[key], 
                        j_data
                        )
                else:
                    stderr.print(f"\t[yellow]Ignoring {key}. See log_report.")
                    self.update_log_report(
                        self.add_bioinfo_results_metadata.__name__,
                        'warning', 
                        f"Collated files can't have more han one matching file. Please check {self.bioinfo_json_file} section: : '{self.software_name}.{key}'"
                    )
            else:
                if key != 'fixed_values':
                    # TODO: update log file
                    stderr.print(f"\t[yellow]Value 'file_per_sample' is missing in {self.bioinfo_json_file} section: '{self.software_name}.{key}'. This field is required to properly handle file configuration.")
                    continue
        return j_data_mapped

    def map_metadata_persample_files(self, bioinfo_dict_scope, j_data):
        """The method processes metadata associated with per sample files and integrates it into the JSON data."""
        file_name = bioinfo_dict_scope['fn']
        file_format = bioinfo_dict_scope['ff']
        file_paths = bioinfo_dict_scope['file_paths']
        if file_format == ',' and 'pangolin' in file_name:
            pango_path = os.path.dirname(file_paths[0])
            j_data_mapped = self.include_pangolin_data(pango_path, j_data)
        elif file_format == 'fasta' and 'consensus' in file_name:
            j_data_mapped = self.handle_consensus_fasta(bioinfo_dict_scope, j_data)
        else:
            stderr.warning(f"[red]No available methods to parse file format '{file_format}' and file name '{file_name}'.")
            return
        return j_data_mapped
        
    # TODO: recover file format parsing errors
    def map_metadata_collated_files(self, bioinfo_dict_scope, j_data):
        """Handles different file formats in collated files, reads their content, and maps it to j_data"""
        # We will be able to add here as many handlers as we need
        file_extension_handlers = {
            "\t": self.handle_csv_file,
            ",": self.handle_csv_file,
            "html": self.handle_multiqc_html_file,
        }
        file_format = bioinfo_dict_scope['ff']
        if file_format in file_extension_handlers:
            handler_function = file_extension_handlers[file_format]
            j_data_mapped = handler_function(bioinfo_dict_scope, j_data)
            return j_data_mapped
        else:
            stderr.print(f"[red]Unrecognized defined file format {bioinfo_dict_scope['ff'] in {bioinfo_dict_scope['fn']}}")
            return None
    
    def handle_csv_file(self, bioinfo_dict_scope, j_data):
        """handle csv/tsv file and map it with read lab metadata (j_data)"""
        map_data = relecov_tools.utils.read_csv_file_return_dict(
            file_name = bioinfo_dict_scope['file_paths'],
            sep = bioinfo_dict_scope['ff'],
            key_position = (bioinfo_dict_scope['sample_col_idx']-1)
        )
        j_data_mapped = self.mapping_over_table(
            j_data, 
            map_data, 
            bioinfo_dict_scope['content'],
            bioinfo_dict_scope['file_paths']
        )
        return j_data_mapped

    def handle_multiqc_html_file(self, bioinfo_dict_scope, j_data):
        """Reads html file, finds table containing programs info, and map it to j_data"""
        program_versions = {}
        with open(bioinfo_dict_scope['file_paths'], 'r') as html_file:
            html_content = html_file.read()
        # Load HTML
        soup = BeautifulSoup(html_content, features="lxml")
        # Get version's div id
        div_id = "mqc-module-section-software_versions"
        versions_div = soup.find('div', id=div_id)
        # Get version's metadata data
        if versions_div:
            table = versions_div.find('table', class_='table')
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]: #skipping header
                    columns = row.find_all('td')
                    if len(columns) == 3:
                        program_name = columns[1].text.strip()
                        version = columns[2].text.strip()
                        program_versions[program_name] = version
                    else:
                        stderr.print(f"[red] HTML entry error in {columns}. HTML table expected format should be \n<th> Process Name\n</th>\n<th> Software </th>\n.")
            else:
                stderr.print(f"[red] Missing table containing software versions in {bioinfo_dict_scope['file_paths']}.")
                sys.exit(1)
        else:
            log.error(f"Required div section 'mqc-module-section-software_versions' not found in file {bioinfo_dict_scope['file_paths']}.")
            stderr.print(f"[red] No div section  'mqc-module-section-software_versions' was found in {bioinfo_dict_scope['file_paths']}.")
            sys.exit(1)
                        
        # mapping mqc sofware versions to j_data
        field_errors = {}
        for row in j_data:
            sample_name = row["submitting_lab_sample_id"]
            for field, values in bioinfo_dict_scope['content'].items():
                try:
                    row[field] = program_versions[values]
                except KeyError as e:
                    field_errors[sample_name] = {field: e}
                    row[field] =  "Not Provided [GENEPIO:0001668]"
                    continue
        return j_data

    def mapping_over_table(self, j_data, map_data, mapping_fields, table_name):
        """Auxiliar function to iterate over table's content and map it to metadata (j_data)"""
        errors = []
        field_errors = {}
        for row in j_data:
            sample_name = row["submitting_lab_sample_id"]
            if sample_name in map_data:
                for field, value in mapping_fields.items():
                    try:
                        row[field] = map_data[sample_name][value]
                    except KeyError as e:
                        field_errors[sample_name] = {field: e}
                        row[field] = "Not Provided [GENEPIO:0001668]"
                        continue
            else:
                errors.append(sample_name)
                for field in mapping_fields.keys():
                    row[field] = "Not Provided [GENEPIO:0001668]"
        if errors:
            lenerrs = len(errors)
            log.error(
                "\t{0} samples missing in {1}:\n\t{2}".format(lenerrs, table_name, errors)
            )
            stderr.print(f"\t[red]{lenerrs} samples missing in {table_name}:\n\t{errors}")
        if field_errors:
            log.error("\tFields not found in {0}:\n\t{1}".format(table_name, field_errors))
            stderr.print(f"\t[red]Missing values in {table_name}:\n\t{field_errors}")
        return j_data

    # TODO: haven't improved yet
    def include_pangolin_data(self, dir_path, j_data):
        """Include pangolin data collecting form each file generated by pangolin"""
        mapping_fields = self.software_config["mapping_pangolin"]["content"]
        missing_pango = []
        for row in j_data:
            # Get read lab sample id
            if "-" in row["submitting_lab_sample_id"]:
                sample_name = row["submitting_lab_sample_id"].replace("-", "_")
            else:
                sample_name = row["submitting_lab_sample_id"]
            # Get the name of pangolin csv file/s
            f_name_regex = sample_name + ".pangolin*.csv"
            f_path = os.path.join(dir_path, f_name_regex)
            pango_files = glob.glob(f_path)
            # Parse pangolin files
            if pango_files:
                if len(pango_files) > 1:
                    stderr.print(
                        "[yellow]More than one pangolin file found for sample",
                        f"[yellow]{sample_name}. Selecting the most recent one",
                    )
                try:
                    pango_files = sorted(
                        pango_files,
                        key=lambda dt: datetime.strptime(dt.split(".")[-2], "%Y%m%d"),
                    )
                    row["lineage_analysis_date"] = pango_files[0].split(".")[-2]
                except ValueError:
                    log.error("\tNo date found in %s pangolin files", sample_name)
                    stderr.print(
                        f"\t[red]No date found in sample {sample_name}. Pangolin filenames:",
                        f"\n\t[red]{pango_files}",
                    )
                    stderr.print("\t[yellow]Using mapping analysis date instead")
                    # If no date in pangolin files, set date as analysis date
                    row["lineage_analysis_date"] = row["analysis_date"]
                f_data = relecov_tools.utils.read_csv_file_return_dict(
                    pango_files[0], sep=","
                )
                pang_key = list(f_data.keys())[0]
                for field, value in mapping_fields.items():
                    row[field] = f_data[pang_key][value]
            else:
                missing_pango.append(sample_name)
                for field in mapping_fields.keys():
                    row[field] = "Not Provided [GENEPIO:0001668]"
        if len(missing_pango) >= 1:
            stderr.print(
                f"\t[yellow]{len(missing_pango)} samples missing pangolin.csv file:"
            )
            stderr.print(f"\t[yellow]{missing_pango}")
        return j_data

    def handle_consensus_fasta(self, bioinfo_dict_scope, j_data):
        """Include genome length, name, file name, path and md5 by preprocessing
        each file of consensus.fa"""
        mapping_fields = bioinfo_dict_scope["content"]
        missing_consens = []
        consensus_dir_path = os.path.dirname(bioinfo_dict_scope['file_paths'][0])
        # FIXME: Replace  sequencing_sample_id
        for row in j_data:
            if "-" in row["submitting_lab_sample_id"]:
                sample_name = row["submitting_lab_sample_id"].replace("-", "_")
            else:
                sample_name = row["submitting_lab_sample_id"]
            f_name = sample_name + ".consensus.fa"
            f_path = os.path.join(consensus_dir_path, f_name)
            try:
                record_fasta = relecov_tools.utils.read_fasta_return_SeqIO_instance(
                    f_path
                )
            except FileNotFoundError as e:
                missing_consens.append(e.filename)
                for item in mapping_fields:
                    row[item] = "Not Provided [GENEPIO:0001668]"
                continue
            row["consensus_genome_length"] = str(len(record_fasta))
            row["consensus_sequence_name"] = record_fasta.description
            row["consensus_sequence_filepath"] = self.input_folder
            row["consensus_sequence_filename"] = f_name
            row["consensus_sequence_md5"] = relecov_tools.utils.calculate_md5(f_path)
            if row["read_length"].isdigit():
                base_calculation = int(row["read_length"]) * len(record_fasta)
                if row["submitting_lab_sample_id"] != "Not Provided [GENEPIO:0001668]":
                    row["number_of_base_pairs_sequenced"] = str(base_calculation * 2)
                else:
                    row["number_of_base_pairs_sequenced"] = str(base_calculation)
            else:
                row["number_of_base_pairs_sequenced"] = "Not Provided [GENEPIO:0001668]"
        # TODO: WAIT TO FIXED IN POST ADAPTATION PR
        conserrs = len(missing_consens)
        if conserrs >= 1:
            log.error(
                "\t{0} Consensus files missing:\n\t{1}".format(
                    conserrs, missing_consens
                )
            )
            stderr.print(f"\t[yellow]{conserrs} samples missing consensus file:")
            stderr.print(f"\n\t[yellow]{missing_consens}")
        return j_data

    def include_custom_data(self, j_data):
        """Include custom fields like variant-long-table path"""
        condition = os.path.join(self.input_folder, "*variants_long_table*.csv")
        f_path = relecov_tools.utils.get_files_match_condition(condition)
        if len(f_path) == 0:
            long_table_path = "Not Provided [GENEPIO:0001668]"
        else:
            long_table_path = f_path[0]
        for row in j_data:
            row["long_table_path"] = long_table_path
        return j_data

    def add_fixed_values(self, j_data):
        """include the fixed data defined in configuration or feed custom empty fields"""
        f_values = self.software_config["fixed_values"]
        for row in j_data:
            for field, value in f_values.items():
                row[field] = value
        return j_data

    def collect_info_from_lab_json(self):
        """Create the list of dictionaries from the data that is on json lab
        metadata file. Return j_data that is used to add the rest of the fields
        """
        try:
            json_lab_data = relecov_tools.utils.read_json_file(self.readlabmeta_json_file)
        except ValueError:
            log.error("%s invalid json file", self.readlabmeta_json_file)
            stderr.print(f"[red] {self.readlabmeta_json_file} invalid json file")
            sys.exit(1)
        return json_lab_data

    def create_bioinfo_file(self):
        """Create the bioinfodata json with collecting information from lab
        metadata json, mapping_stats, and more information from the files
        inside input directory
        """
        stderr.print("[blue]Sanning input directory...")
        files_found_dict = self.scann_directory()
        stderr.print("[blue]Adding files found to bioinfo config json...")
        software_config_extended = self.add_filepaths_to_software_config(files_found_dict)
        stderr.print("[blue]Validating required files...")
        self.validate_software_mandatory_files(software_config_extended)
        stderr.print("[blue]Reading lab metadata json")
        j_data = self.collect_info_from_lab_json()
        stderr.print(f"[blue]Adding metadata from {self.input_folder} into read lab metadata...")
        j_data = self.add_bioinfo_results_metadata(software_config_extended, j_data)
        #TODO: This should be refactor according to new file-handling implementation
        #stderr.print("[blue]Adding variant long table path")
        #j_data = self.include_custom_data(j_data)
        stderr.print("[blue]Adding fixed values")
        j_data = self.add_fixed_values(j_data)
        file_name = (
            "bioinfo_" + os.path.splitext(os.path.basename(self.readlabmeta_json_file))[0] + ".json"
        )
        stderr.print("[blue]Writting output json file")
        os.makedirs(self.output_folder, exist_ok=True)
        file_path = os.path.join(self.output_folder, file_name)
        relecov_tools.utils.write_json_fo_file(j_data, file_path)
        stderr.print("[green]Sucessful creation of bioinfo analyis file")
        return True
