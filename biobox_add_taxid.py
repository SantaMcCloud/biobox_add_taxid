import argparse
import os
from typing import Optional

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="biobox_add_taxid",
        description="Scrip for adding the taxids into the biobox format for CAMI Amber from BAT or GTDB-Tk with the help of different tools. \
            When using GTDB as tool type you also have to include the gtdb_to_taxdump [ncbi-gtdb_map.py] output and the taxonkit [name2taxid.py] output as input!",
        usage="TODO",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True
    )

    optional = parser.add_argument_group('optional arguments')

    parser.add_argument("biobox_file", type=str, help="Input the binning file in biobox format here")
    parser.add_argument("tool_type", type=str, choices=["BAT", "GTDB"], help="Select the tool from which the output is used here")
    parser.add_argument("tool_output", type=str, help="Include the output of the chosen tool. For BAT use the bin2classification file while for GTDB use the summary file.")
    parser.add_argument("--input_dir", type=str, default="./", help="Input the directory where the inputs file are stored")
    optional.add_argument("--gtdb_to_taxdum", "-g", type=str, help="When GTDB is selected as tool_type you can include the ncbi-gtdb_map.py output here")
    optional.add_argument("--taxonkit", "-t", type=str, help="When GTDB is selected as tool_type you can include the name2taxid.py output here")
    parser.add_argument("--version", action="version", version="0.1")
    
    parser.print_usage = parser.print_help

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_arguments()
    