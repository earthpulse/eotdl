# Use Case A - Unsupervised Learning

SSL4EO-S12 dataset published by TUM. 

Original publication and info at: https://mediatum.ub.tum.de/1660427?v=1

Github repository: https://github.com/zhu-xlab/SSL4EO-S12


## Description

The dataset is released in three separate compressed tar archives, one for each product (Sentinel-1 GRD, Sentinel-2 L1C, Sentinel-2 L2A).
Dataset source is Google Earth Engine.


Each archive consist of 251079 sub-directories, one for each sampled location, each holding four different seasonally spaced acquisitions.


## Listing the acquisition directories of each archive for metadata (e.g., datetime / bounding box) extraction

It is recommended to extract the list of acquisition samples for each archive prior to extracting them using tar -t, avoiding complications due to volume.

i.e., the following:

```bash
tar -tf <archive_name>.tar.gz | grep metadata.json | sed 's/metadata.json//' > list_of_acquisition_directories.txt
```

is a valid way of listing all the directories in a text file, however there are numerous effective options even post archive extraction.


## row\_factory.py

Component script that defines the metadata row generation process provided an acquisition directory path.
Used by run\_extraction.sh script.

Outputs a csv row with a date and bounding box formatted as `%Y-%m-%d` and `[lower_left_x, lower_left_y, top_right_x, top_right_y]` respectively, as expected by the sentinel-hub api.


## run\_extraction.sh

A bash script that expects as inputs a file with paths of acquisition directories to process and the name of a file to output generated rows. It simply executes a loop process  during which each acquisition directory row is passed to the row factory script and its output is appended to the provided output file.

i.e.,

```bash
./run_extraction.sh list_of_acquisition_directories.txt acquisitions_metadata.txt
```

As the archives are over 500GB each, iterating through them can be a long process. Running in background and disowning is advised.

