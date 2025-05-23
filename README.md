# cTENOR
cTENOR (classified TE Non-Overlapping Result) is tool for merging results of TE classify tools.  
Run DeepTE and RFSB to classify the Unknowns in the RepeatModeler results. The final classification is subsequently output based on the results of both tools.

## Docker build and run (Recommended)
After you get a output file of RepeatModeler, run below commands
```
docker build -t ctenor_env .
docker run -it -v $(pwd)/:/app/current/ ctenor_env
python cTENOR.py -f ./data/consensi.fa.classified -d TEST -sp M
```
It works in Apple Silicon M1 Macbook air  

## Usage
```
cTENOR version 1.2.0
Author: Yuki Kimura 2022-2025, MIT licence
usage: cTENOR.py [-h] -f FASTA -d DIRECTORY -sp {P,M,F,O} [-s] [-t THRESHOLD] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        library fasta file which is outputfile of RepeatModeler
  -d DIRECTORY, --directory DIRECTORY
                        Output directory
  -sp {P,M,F,O}, --species {P,M,F,O}
                        P or M or F or O. P:Plants, M:Metazoans, F:Fungi, and O: Others.
  -s, --skip            Skip running DeepTE and RFSB (Please assign the directory containing the results of the previous analysis)
  -t THRESHOLD, --threshold THRESHOLD
                        set threshold for family classification
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

## Requirements (not use Docker) 
- python 3.6 ~ (3.9 tested)
- DeepTE (Yan et al., 2020)
- RFSB (TransposonUltimate) (Riehl et al., 2022)
- pandas

## Install (It is NOT recommended, it's out of date!)
```
$ conda create -n cTENOR python=3.9
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

## Citation
The cTENOR paper is currently in preparation; please cite the GitHub link and also cite the following two papers.
- Yuki Kimura. 2022. cTENOR. Github. https://github.com/kim2039/cTENOR.
- Haidong Yan, Aureliano Bombarely, Song Li 2020 DeepTE: a computational method for de novo classification of transposons with convolutional neural network. Bioinformatics, Volume 36, Issue 15, 1 August 2020, Pages 4269–4275. https://doi.org/10.1093/bioinformatics/btaa519
- Kevin Riehl, Cristian Riccio, Eric A Miska, Martin Hemberg, TransposonUltimate: software for transposon classification, annotation and detection, Nucleic Acids Research, 2022; gkac136, https://doi.org/10.1093/nar/gkac136