# cTENOR
cTENOR is tool for merging results of TE classify tools.  
Run DeepTE and RFSB to classify the Unknowns in the RepeatModeler results. The final classification is subsequently output based on the results of both tools.

## Requirements
- python 3.6 ~ (3.10 tested)
- DeepTE (Yan et al., 2020)
- RFSB (TransposonUltimate) (Riehl et al., 2022)
- pandas

## install
```
$ conda create -n cTENOR python=3.10
$ conda activate cTENOR

# Install DeepTE
$ git clone https://github.com/LiLabAtVT/DeepTE.git
$ conda install biopython keras numpy tensorflow pandas

# Install RFSB
$ conda install -c derkevinriehl -c bioconda transposon_classifier_rfsb 

# Install cTENOR
$ git clone https://github.com/kim2039/cTENOR.git
$ cd cTENOR
$ python configure.py
# type the path for both tools.
```

## Usage
```
cTENOR version 1.0.0
usage: cTENOR.py [-h] -f FASTA -d DIRECTORY -sp SPECIES [-s] [-v]

options:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        library fasta file which is outputfile of RepeatModeler
  -d DIRECTORY, --directory DIRECTORY
                        Output directory
  -sp SPECIES, --species SPECIES
                        P or M or F or O. P:Plants, M:Metazoans, F:Fungi, and O: Others.
  -s, --skip            Skip running DeepTE and RFSB (Please assign the directory containing the results of the previous analysis)
  -v, --version         show this version
```
