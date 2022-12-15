# cTENOR
cTENOR (classified TE Non-Overlapping Result) is tool for merging results of TE classify tools.  
Run DeepTE and RFSB to classify the Unknowns in the RepeatModeler results. The final classification is subsequently output based on the results of both tools.

## Requirements
- python 3.6 ~ (3.10 tested)
- DeepTE (Yan et al., 2020)
- RFSB (TransposonUltimate) (Riehl et al., 2022)
- pandas

## Install
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
# type the full path for both tools.
```

## Usage
```
cTENOR version 1.1.0
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

## Output file
- cTENOR_out.csv: Includes a consensus classification based on the probability of each tool
- cTENOR_out.fasta: The FASTA file that replaces the original RepeatModeler Unknown classification with the new classification.

## align file replace
It is possible to rewrite the contents of the align file even after RepeatMasker has already been executed. This is intended for use in `calcDivergenceFromAling.pl`.
- cTENOR_replace.align: This is an align file substituted with only the portions needed for analysis

```
alignment file replace version 1.0.0 with cTENOR
usage: alignreplace.py [-h] -a ALIGN_FILE -i INPUT [--prefix PREFIX] [-v]

options:
  -h, --help            show this help message and exit
  -a ALIGN_FILE, --align_file ALIGN_FILE
                        Alignment file of RepeatMasker; *.align
  -i INPUT, --input INPUT
                        Result csv file 'cTENOR_out.csv
  --prefix PREFIX       prefix the output
  -v, --version         show this version
```

## Citation
The cTENOR paper is currently in preparation; please cite the GitHub link and also cite the following two papers.
- Yuki Kimura. 2022. cTENOR. Github. https://github.com/kim2039/cTENOR.
- Haidong Yan, Aureliano Bombarely, Song Li 2020 DeepTE: a computational method for de novo classification of transposons with convolutional neural network. Bioinformatics, Volume 36, Issue 15, 1 August 2020, Pages 4269–4275. https://doi.org/10.1093/bioinformatics/btaa519
- Kevin Riehl, Cristian Riccio, Eric A Miska, Martin Hemberg, TransposonUltimate: software for transposon classification, annotation and detection, Nucleic Acids Research, 2022; gkac136, https://doi.org/10.1093/nar/gkac136