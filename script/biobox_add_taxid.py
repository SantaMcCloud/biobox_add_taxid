#!/usr/bin/env python
import argparse
import sys


def parse_arguments():
    """
    This function is there to capture the arguments in the command line and to parse them to use them correctly.

    Please refer to the usage how to use this tool.

    """

    parser = argparse.ArgumentParser(
        prog="biobox_add_taxid",
        description="This tool was designed to add a 'TaxID' column in a binning file in biobox format.",
        usage="biobox_add_taxid biobox_file [(-c/--contig2taxid) CONTIG2TAXID/ (-b/--binid2taxid) BINID2TAXID] (-k_c/--key_col) KEY_COL (-t_c/--taxid_col) TAX_COL",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    parser.add_argument(
        "biobox_file", 
        type=str, 
        help="Input the binning file in biobox format here."
    )

    parser.add_argument(
        "--key_col",
        "-k_c",
        type=int,
        default=None,
        help="State the column in which the contigid or the binid is stated based on the which input is used"
    )

    parser.add_argument(
        "--taxid_col",
        "-t_c",
        type=int,
        default=None,
        help="State the column in which the taxid is stated"
    )
    
    parser.add_argument(
        "--contig2taxid",
        "-c",
        type=str,
        default=None,
        help="Input a contig2taxid file which is generate by kraken2." 
    )

    parser.add_argument(
        "--binid2taxid",
        "-b",
        type=str,
        default=None,
        help="Input a binid2taxid file. The first column should be the BINID column and the last column should be the TAXID column."
    )

    parser.add_argument(
        "--debug",
        default=False,
        action='store_true',
        help="Use this flag for debugging"
    )

    parser.add_argument("--version", action="version", version="1.0")

    parser.print_usage = parser.print_help

    args = parser.parse_args()

    return args

def load_biobox_file(biobox_file):
    """
    The binning file, in biobox format, is taken as argument to then map each row of the file such that the first column [seqid] 
    will be match to the second column [binid].

    Every row stating with @ or # will be skip in this function since they do not have any information needed to save for later.

    As output the tool will return the seqid to binid mapping which then will be used later!
    """
    print("Start with extracting of the biobox file.")
    print(f"Load {biobox_file}")
    biobox = {}
    with open(biobox_file, "r") as file:
        for line in file:
            if line.startswith("@") or line.startswith("#"):
                continue
            line = line.replace("\n","")
            seqid, binid = line.split("\t")
            biobox[seqid] = binid
    return biobox
    
def load_contig2taxid_file(contig2taxid_file, key_col, taxid_col):
    """
    Load the contig2taxid file into a dict to with the seqid as key and the taxid as value for each seqid.
    """
    print("Start with extracting of the biobox file.")
    print(f"Load {contig2taxid_file}")
    contig2taxid = {}
    with open(contig2taxid_file, "r") as file:
        for line in file:
            if line.startswith("#"):
                continue
            line = line.strip()
            line = line.split("\t")
            seqid = line[key_col - 1]
            taxid = line[taxid_col -1]
            contig2taxid[seqid] = taxid
    return contig2taxid

def laod_binid2taxid_file(binid2taxid_file, key_col, taxid_col):
    """
    Load the binid2taxid file into a dict with the binid as key and the taxid as value.
    """
    print("Start with extracting of the biobox file.")
    print(f"Load {binid2taxid_file}")
    binid2taxid = {}
    with open(binid2taxid_file, "r") as file:
        for line in file:
            if line.startswith("#"):
                continue
            line = line.strip()
            line = line.split("\t")
            binid = line[key_col - 1]
            taxid = line[taxid_col - 1]
            binid2taxid[binid] = taxid
    return binid2taxid 

def create_file(biobox, contig2taxid, binid2taxid):
    """
    Write the biobox file and add the TAXID column to it.
    """
    print("Create the new binning file in biobox format with the added taxid column")
    with open("./modified_biobox_file.tsv", "w") as file:
        file.write("#CAMI Format for Binning\n")
        file.write("@Version:0.9.0\n")
        file.write("@SampleID:_SAMPLEID_\n")
        file.write("@@SEQUENCEID\tBINID\tTAXID\n")
        for seqid in biobox.keys():
            binid = biobox[seqid]
            if contig2taxid is None:
                taxid = binid2taxid[binid]
            else:
                taxid = contig2taxid[seqid]
            file.write(f"{seqid}\t{binid}\t{taxid}\n")

if __name__ == "__main__":
    args = parse_arguments()
    if args.debug:
        print(f"\nBIOBOX FILE: {args.biobox_file}")
        print(f"BINID2TAXID FILE: {args.binid2taxid}")
        print(f"CONTIG2TAXID FILE: {args.contig2taxid}")
        print(f"KEY COLUMN: {args.key_col}")
        print(f"TAXID COLUMN: {args.taxid_col}\n")
    if args.contig2taxid is None and args.binid2taxid is None:
        print("Please input at least either a contig2taxid file or a binid2taxid file!")
        sys.exit()
    if args.key_col is None or args.taxid_col is None:
        print("Please enter the column where the BinID/ContigID is stated and enter the column where the TaxID is stated.")
        print("The followed was enter:")
        print(f"KEY_COL:  {args.key_col}")
        print(f"TAXID_COL: {args.taxid_col}")
        sys.exit()
    if args.contig2taxid is None:
        biobox =  load_biobox_file(args.biobox_file)
        binid2taxid = laod_binid2taxid_file(args.binid2taxid, args.key_col, args.taxid_col)
        create_file(biobox, None, binid2taxid)
    else:
        biobox =  load_biobox_file(args.biobox_file)
        contig2taxid = load_contig2taxid_file(args.contig2taxid, args.key_col, args.taxid_col)
        create_file(biobox, contig2taxid, None)