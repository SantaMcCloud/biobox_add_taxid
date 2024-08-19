import argparse
import os


def parse_arguments():
    """
    This function is there to capture the arguments in the command line and to parse them to use them correctly.

    Please refer to the usage how to use this script.

    """

    parser = argparse.ArgumentParser(
        prog="biobox_add_taxid",
        description="Script for adding the taxids into the biobox format for CAMI Amber from BAT or GTDB-Tk with the help of different tools. \
            When using GTDB as tool type you also have to include the gtdb_to_taxdump [ncbi-gtdb_map.py] output and the taxonkit [name2taxid.py] output as input and the column in where the names are in the taxonkit output!",
        usage="biobox_add_taxid biobox_file {BAT | GTDB} input_dir [--gtdb_to_taxdump GTDB_TO_TAXDUM | -g GTDB_TO_TAXDUM] [ --taxonkit TAXONKIT | -t TAXONKIT] [--column COLUMN | -c COLUMN]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    optional = parser.add_argument_group("optional arguments")

    parser.add_argument(
        "biobox_file", type=str, help="Input the binning file in biobox format here"
    )
    parser.add_argument(
        "tool_type",
        type=str,
        choices=["BAT", "GTDB"],
        help="Select the tool from which the output is used here",
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="Include the directory where the input file(s) are stored here. When using BAT use the bin2classification file and when using GTDB then use the summary file",
    )
    parser.add_argument("--version", action="version", version="0.1")

    optional.add_argument(
        "--gtdb_to_taxdump",
        "-g",
        type=str,
        help="When GTDB is selected as tool_type you can include the ncbi-gtdb_map.py output here",
    )
    optional.add_argument(
        "--taxonkit",
        "-t",
        type=str,
        help="When GTDB is selected as tool_type you can include the name2taxid.py output here",
    )
    optional.add_argument(
        "--column",
        "-c",
        type=int,
        default=0,
        help="Set the column for the taxonkit [name2taxid] in which the names are",
    )

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
            line = line.replace("\n", "")
            seqid, binid = line.split("\t")
            biobox[seqid] = binid
    return biobox


def load_gtdb_files(input_dir):
    """
    When the tool_type is set to GTDB then this function will be call to save a certain mapping form the input, in this case the summary file from GTDB-Tk.

    We will map the binid to the names since each bin is classified to one name. The binid is in the first row and the name are in the second column.
    We have to split up the name since each are connected via semicolons to build up the lineage.
    After the split the tool take the last name since this is the classification of the bin and save it up in the mapping.

    As output the tool return the binid to name mapping to use it later.
    """
    gtdb_mapping = {}
    print("Start with extracting the names from the GTDB file.")
    for input in os.listdir(input_dir):
        print(f"Load file: {input}")
        with open(input_dir + input, "r") as f:
            for lines in f:
                if lines.startswith("user_genome") or lines.startswith("#"):
                    continue
                lines = lines.replace("\n", "")
                line = lines.split("\t")
                binid = line[0]
                if ";" in line[1]:
                    lineage = line[1].split(";")
                    name = lineage[-1]
                else:
                    name = line[1]
                gtdb_mapping[binid] = name
    return gtdb_mapping


def load_bat_file(input_dir):
    """
    When the tool_type is set to BAT then this function will be call to save a certain mapping form the input, in this case the bin2classification file from BAT.

    We will map the binid to the taxid. The binid is in the first column while the taxid is in the fourth column.
    To get the right taxid the tool have to split them by the semicolons since they show the lineage.
    After the splitting the tool will take the last taxid from the lineage since this is the deepest classification possible from BAT.

    As output the tool will return the binid to taxid mapping to use it later.
    """
    print("Start with extracting the taxid from the BAT file.")
    bat = {}
    for input in os.listdir(input_dir):
        print(f"Load {input}")
        with open(input_dir + input, "r") as file:
            for lines in file:
                if lines.startswith("#"):
                    continue
                lines = lines.replace("\n", "")
                line = lines.split("\t")
                binid = line[0].split(".")[0]
                taxid = line[3].split(";")[-1]
                bat[binid] = taxid
    return bat


def load_taxonkit(taxonkit_file, c):
    """
    When the tool_type is set to GTDB then the tool also need the output from the tool name2taxid from taxonkit. Since it copy the hole file which was taken as input
    the tool also need to know in which column the names are stated.

    In this function the tool map the ncbi_names to the taxids since the taxids are the important information the tool need later.
    First the tool have the get names from the column which is given as argument in this function. The taxids are always in the last column.

    Every row starting with # will be ignore in this function because the user dont have to write a new file each time and can take out row which they dont need.

    As output the tool will return the ncbi_name to taxid mapping to use it later.
    """
    taxonkit = {}
    print("Start with mapping the names to the taxids from the Taxonkit file.")
    print(f"Load {taxonkit_file}")
    with open(taxonkit_file, "r") as file:
        for lines in file:
            if lines.startswith("#"):
                continue
            lines = lines.replace("\n", "")
            line = lines.split("\t")
            name = line[c]
            taxid = line[-1]
            taxonkit[name] = taxid
    return taxonkit


def load_gtdb_to_taxdump(gtdb_to_taxdump_file):
    """
    When the tool_type is set to GTDB then the tool also need the output from the tool ncbi-gtdb_map.py from gtdb_to_taxdump.
    
    Here the tool use the first column as gtdb_name since and the second column are the ncbi_names since ncbi-gtdb_map.py take the gtdb_names and will output the ncbi taxonomy
    related the the gtdb_names.

    Every row starting with # will be ignore in this function because the user dont have to write a new file each time and can take out row which they dont need.

    As output the tool will return the gtdb_name to ncbi_name mapping to use it later.
    """
    gtdb_ncbi = {}
    print("Start with mapping the GTDB names to the NCBI names")
    print(f"Load {gtdb_to_taxdump_file}")
    with open(gtdb_to_taxdump_file, "r") as file:
        for lines in file:
            if lines.startswith("#") or lines.startswith("ncbi_taxonomy"):
                continue
            lines = lines.replace("\n", "")
            line = lines.split("\t")
            gtdb = line[0]
            ncbi = line[1]
            gtdb_ncbi[gtdb] = ncbi
    return gtdb_ncbi


def create_file(
    mode, biobox_file, biobox_dic, input_dic, taxonkit_dic, gtdb_to_taxdump_dic
):
    """
    In this function the tool will create the binning file, in biobox format, with the now new added taxid column. The argument are as followed:

    mode: The tool_type since the tool need more steps to get the taxid when the tool have a GTDB file as input
    biobox_file: The binning file to get the name of the file to recreate a new file.
    biobox_dic: The seqid to binid mapping from the function load_biobox_file.
    input_dic: Is either the binid to taxid mapping from load_bat_file when the tool_type is BAT or the binid to gtdb_name mapping when the tool_type is GTDB.
    taxonkit_dic: Is None since when the tool_type is BAT it is not needed or it is the ncbi_name to taxid mapping when the tool_type is GTDB.
    gtdb_to_taxdump_dic: Is None since when the tool_type is BAT it is not needed or it is the gtdb_name to ncbi_name mapping when the tool_type is GTDB.

    In here the tool will create a new file with the name of the biobox_file + _add_taxid + tool_type. In this file the tool will write the typical 4 rows since which are always in a binning file.

    The Tool always read out the seqid which are the keys in the biobox_dic to get the binid according to the seqid. After this step the tool have 2 different ways to get to the taxid according to the binid.

    When the tool_type is BAT:
    - Here the tool can directly read out the taxid since the input_dic has the binid to taxid mapping.
    - since the tool can read it out the tool can directly write the row with seqid \t binid \t taxid

    When the tool_type is GTDB:
    - The input_dic has a binid to gtdb_name mapping we first will save the gtdb_name according to the binid.
    - Then we use the gtdb_to_taxdump_dic since we have a gtdb_name to ncbi_name mapping to save the ncbi_name according to the gtdb_name.
    - With the taxonkit_dic we then can final access the taxid which is according gtdb_name with the ncbi_name since it has a ncbi_name to taxid mapping
    - After save the taxid the tool can write the row as followed: seqid \t binid \t taxid


    """
    print("Create the new binning file in biobox format with the added taxid column")
    file_name = biobox_file.split(".")
    with open(
        "./{0}_add_taxid_{1}.{2}".format(file_name[0].split("/")[-1], mode, file_name[1]), "w"
    ) as file:
        file.write("#CAMI Format for Binning\n")
        file.write("@Version:0.9.0\n")
        file.write("@SampleID:_SAMPLEID_\n")
        file.write("@@SEQUENCEID\tBINID\tTAXID\n")
        for seqid in biobox_dic.keys():
            binid = biobox_dic[seqid]
            if mode == "GTDB":
                gtdb_name = input_dic[binid]
                ncbi_name = gtdb_to_taxdump_dic[gtdb_name]
                if ncbi_name in taxonkit_dic.keys():
                    taxid = taxonkit_dic[ncbi_name]
                else:
                    ncbi_name = ncbi_name.split("_")[-1]
                    taxid = taxonkit_dic[ncbi_name]
            else:
                taxid = input_dic[binid]
                if "*" in taxid:
                    taxid = taxid[:-1]
            file.write(f"{seqid}\t{binid}\t{taxid}\n")


if __name__ == "__main__":
    args = parse_arguments()

    if args.input_dir.endswith("/"):
        input_dir = args.input_dir
    else:
        input_dir = args.input_dir + "/"

    if args.tool_type == "GTDB":
        if args.taxonkit is None or args.gtdb_to_taxdump is None:
            print(
                f"You used {args.tool_type} as tool type this means you also have to include the taxonkit [name2taxid] output and the gtdb_to_taxdump [ncbi-gtdb_map] output. \n The input here for Taxonkit was: {args.taxonkit} and the input here for gtdb_to_taxdump was: {args.gtdb_to_taxdump}"
            )
        else:
            biobox_dic = load_biobox_file(args.biobox_file)
            input_dic = load_gtdb_files(input_dir)
            taxonkit_dic = load_taxonkit(args.taxonkit, args.column)
            gtdb_to_taxdump_dic = load_gtdb_to_taxdump(args.gtdb_to_taxdump)
            create_file(
                args.tool_type,
                args.biobox_file,
                biobox_dic,
                input_dic,
                taxonkit_dic,
                gtdb_to_taxdump_dic,
            )
    else:
        biobox_dic = load_biobox_file(args.biobox_file)
        input_dic = load_bat_file(input_dir)
        create_file(args.tool_type, args.biobox_file, biobox_dic, input_dic, None, None)
