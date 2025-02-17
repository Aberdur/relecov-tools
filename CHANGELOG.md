# relecov-tools Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-10-11 : https://github.com/BU-ISCIII/relecov-tools/releases/tag/1.2.0

### Credits

Code contributions to the release:

- [Juan Ledesma](https://github.com/juanledesma78)
- [Pablo Mata](https://github.com/Shettland)
- [Sergio Olmos](https://github.com/OPSergio)

### Modules

- Included wrapper module to launch download, read-lab-metadata and validate processes sequentially [#322](https://github.com/BU-ISCIII/relecov-tools/pull/322)
- Changed launch-pipeline name for pipeline-manager when tools are used via CLI [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324)

#### Added enhancements

- Now also check for gzip file integrity after download. Moved cleaning process to end of workflow [#313](https://github.com/BU-ISCIII/relecov-tools/pull/313)
- Introduced a decorator in sftp_client.py to reconnect when conection is lost [#313](https://github.com/BU-ISCIII/relecov-tools/pull/313)
- Add Hospital Universitari Doctor Josep Trueta to laboratory_address.json [#316] (https://github.com/BU-ISCIII/relecov-tools/pull/316)
- samples_data json file is no longer mandatory as input in read-lab-metadata [#314](https://github.com/BU-ISCIII/relecov-tools/pull/314)
- Included handling of alternative column names to support two distinct headers using the same schema in read-lab-metadata [#314](https://github.com/BU-ISCIII/relecov-tools/pull/314)
- Included a new hospital (Hospital Universitario Araba) to laboratory_address.json [#315](https://github.com/BU-ISCIII/relecov-tools/pull/315) 
- More accurate cleaning process, skipping only sequencing files instead of whole folder [#321](https://github.com/BU-ISCIII/relecov-tools/pull/321)
- Now single logs summaries are also created for each folder during download [#321](https://github.com/BU-ISCIII/relecov-tools/pull/321)
- Introduced handling for missing/dup files and more accurate information in prompt for pipeline_manager [#321](https://github.com/BU-ISCIII/relecov-tools/pull/321)
- Included excel resize, brackets removal in messages and handled exceptions in log_summary.py [#322](https://github.com/BU-ISCIII/relecov-tools/pull/322)
- Included processed batchs and samples in read-bioinfo-metadata log summary [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324)
- When no samples_data.json is given, read-lab-metadata now creates a new one [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324)
- Handling for missing sample ids in read-lab-metadata [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324)
- Better logging for download, read-lab-metadata and wrapper [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324)

#### Fixes

- Fixed wrong city name in relecov_tools/conf/laboratory_address.json [#320](https://github.com/BU-ISCIII/relecov-tools/pull/320)
- Fixed wrong single-paired layout detection in metadata due to Capital letters [#321](https://github.com/BU-ISCIII/relecov-tools/pull/321)
- Error handling in merge_logs() and create_logs_excel() methods for log_summary.py [#322](https://github.com/BU-ISCIII/relecov-tools/pull/322)
- Included handling of multiple empty rows in metadata xlsx file [#322](https://github.com/BU-ISCIII/relecov-tools/pull/322)

#### Changed

- Renamed and refactored "bioinfo_lab_heading" for "alt_header_equivalences" in configuration.json [#314](https://github.com/BU-ISCIII/relecov-tools/pull/314)
- Included a few schema fields that were missing or outdated, related to bioinformatics results [#314](https://github.com/BU-ISCIII/relecov-tools/pull/314)
- Updated metadata excel template, moved to relecov_tools/assets [#320](https://github.com/BU-ISCIII/relecov-tools/pull/320)
- Now python lint only triggers when PR includes python files [#320](https://github.com/BU-ISCIII/relecov-tools/pull/320)
- Moved concurrency to whole workflow instead of each step in test_sftp-handle.yml [#320](https://github.com/BU-ISCIII/relecov-tools/pull/320)
- Updated test_sftp-handle.yml testing datasets [#320](https://github.com/BU-ISCIII/relecov-tools/pull/320)
- Now download skips folders containing "invalid_samples" in its name [#321](https://github.com/BU-ISCIII/relecov-tools/pull/321)
- read-lab-metadata: Some warnings now include label. Also removed trailing spaces [#322](https://github.com/BU-ISCIII/relecov-tools/pull/322)
- Renamed launch-pipeline for pipeline-manager and updated keys in configuration.json [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324)
- Pipeline manager now splits data based on enrichment_panel and version. One folder for each group [#324](https://github.com/BU-ISCIII/relecov-tools/pull/324) 

#### Removed

- Removed duplicated tests with pushes after PR was merged in test_sftp-handle [#312](https://github.com/BU-ISCIII/relecov-tools/pull/312)
- Deleted deprecated auto-release in pypi_publish as it does not work with tag pushes anymore [#312](https://github.com/BU-ISCIII/relecov-tools/pull/312)
- Removed first sleep time for reconnection decorator in sftp_client.py, sleep time now increases in the second attempt [#321](https://github.com/BU-ISCIII/relecov-tools/pull/321)

### Requirements

## [1.1.0] - 2024-09-13 : https://github.com/BU-ISCIII/relecov-tools/releases/tag/1.1.0

### Credits

Code contributions to the release:

- [Pablo Mata](https://github.com/Shettland)
- [Sara Monzón](https://github.com/saramonzon)

### Modules

- New logs-to-excel function to create an excel file given a list of log-summary.json files [#300](https://github.com/BU-ISCIII/relecov-tools/pull/300)

#### Added enhancements

- Included a way to extract pango-designation version in read-bioinfo-metadata [#299](https://github.com/BU-ISCIII/relecov-tools/pull/299)
- Now log_summary.py also creates an excel file with the process logs [#300](https://github.com/BU-ISCIII/relecov-tools/pull/300)
- Read-bioinfo-metadata splits files and data by batch of samples [#306](https://github.com/BU-ISCIII/relecov-tools/pull/306)
- Included a sleep time in test_sftp-handle to avoid concurrency check failure [#308](https://github.com/BU-ISCIII/relecov-tools/pull/308)

#### Fixes

- Fixes in launch_pipeline including creation of samples_id.txt and joined validated json [#303](https://github.com/BU-ISCIII/relecov-tools/pull/303)
- Fixed failing module_tests.yml workflow due to deprecated upload-artifact version [#308](https://github.com/BU-ISCIII/relecov-tools/pull/308)

#### Changed

- Changed pypi_publish action to publish on every release, no need to push tags [#308](https://github.com/BU-ISCIII/relecov-tools/pull/308)

#### Removed

- Removed only_samples argument in log_summary.py as it was not used in any module. [#300](https://github.com/BU-ISCIII/relecov-tools/pull/300)

### Requirements

## [1.0.0] - 2024-09-02 : https://github.com/BU-ISCIII/relecov-tools/releases/tag/1.0.0

### Credits

Code contributions to the inital release:

- [Sara Monzón](https://github.com/saramonzon)
- [Sarai Varona](https://github.com/svarona)
- [Guillermo Gorines](https://github.com/GuilleGorines)
- [Pablo Mata](https://github.com/Shettland)
- [Luis Chapado](https://github.com/luissian)
- [Erika Kvalem](https://github.com/ErikaKvalem)
- [Alberto Lema](https://github.com/Alema91)
- [Daniel Valle](https://github.com/Daniel-VM)
