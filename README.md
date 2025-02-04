# biobox_add_taxid
This tool was designed to add a 'TaxID' column in a binning file in biobox format.

The main input of this tool is a binning file which can be generated by the cami amber utility script 'convert_fasta_bins_to_biobox_format.py'.

The second input of this tool can be either a contig2taxid file which can be generated by 'kraken2' or a 
binid2taxid file which looks as followed:

```
BinID   TaxID
test1   11056
test2   444944
ABC 888
....
```

It is important to state the column where either the BinID or the ContigID is stored together with the column where the TaxID is stored. The first column is 1 and the second 2 and so on!
