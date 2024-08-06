import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="biobox_add_taxid",
        description="Script for adding the taxids into the biobox format for CAMI Amber from BAT or GTDB-Tk with the help of different tools. \
            When using GTDB as tool type you also have to include the gtdb_to_taxdump [ncbi-gtdb_map.py] output and the taxonkit [name2taxid.py] output as input and the column in where the names are in the taxonkit output!",
        usage="biobox_add_taxid biobox_file {BAT | GTDB} input [--gtdb_to_taxdump GTDB_TO_TAXDUM | -g GTDB_TO_TAXDUM] [ --taxonkit TAXONKIT | -t TAXONKIT] [--column COLUMN | -c COLUMN]",
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
        "input",
        type=str,
        help="Include the input file here. When you using BAT as tool type then you can directly include the file here",
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


def load_gtdb_files(input):
    gtdb_mapping = {}
    print("Start with extracting the names from the GTDB file.")
    print(f"Load file: {input}")
    with open(input, "r") as f:
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


def load_bat_file(input):
    print("Start with extracting the taxid from the BAT file.")
    print(f"Load {input}")
    bat = {}
    with open(input, "r") as file:
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
    print("Create the new binning file in biobox format with the added taxid column")
    file_name = biobox_file.split(".")
    with open(
        "./{0}_add_taxid.{1}".format(file_name[0].split("/")[-1], file_name[1]), "w"
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

    if args.tool_type == "GTDB":
        if args.taxonkit is None or args.gtdb_to_taxdump is None:
            print(
                f"You used {args.tool_type} as tool type this means you also have to include the taxonkit [name2taxid] output and the gtdb_to_taxdump [ncbi-gtdb_map] output. \n The input here for Taxonkit was: {args.taxonkit} and the input here for gtdb_to_taxdump was: {args.gtdb_to_taxdump}"
            )
        else:
            biobox_dic = load_biobox_file(args.biobox_file)
            input_dic = load_gtdb_files(args.input)
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
        input_dic = load_bat_file(args.input)
        create_file(args.tool_type, args.biobox_file, biobox_dic, input_dic, None, None)
