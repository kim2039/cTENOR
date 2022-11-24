import cTENOR
import csv, argparse

class InputFileError(Exception):
    pass


def divsum_parser(out, sum, outname):
    print('parsing divsum data...')
    with open(sum) as f:
        out_file = []
        for s_line in f:
            s_line = s_line.replace('\n', '')
            if len(s_line.split('\t')) == 5:
                if s_line[0:7] == 'Unknown':
                    line = s_line.split('\t')
                    qid = line[1] # Extract id of unknown

                    # search in "out" list
                    for l in out:
                        if qid in l:
                            family = l[1]
                            break

                    newline = [family, qid, line[2], line[3], line[4]]
                    out_file.append(newline)
                else: # No change for other lines
                    out_file.append(s_line.split('\t'))

    # save files as csv                    
    with open(outname+'.csv', 'w') as f:
        del out_file[1]
        tsv_writer = csv.writer(f)
        tsv_writer.writerows(out_file)

if __name__ == '__main__':
    print("divsumparser with cTENOR")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--divsum_file", help="Result divsum file of RepeatMasker and calcDivergenceFromAling.pl", required=True)
    parser.add_argument("-i", "--input", help="Result txt file of deepTE -> TEclass -> RF", required=True)
    parser.add_argument("-o", "--output", help="Prefix of output file name")
    args = parser.parse_args()

    # out file name
    if args.output:
        outname = args.output
    else:
        outname = 'cTENOR_divsum_summary'

    # check the header of the file
    with open(args.divsum_file) as f:
        firstline = f.readline().rstrip()
        if not firstline == 'Jukes/Cantor and Kimura subsitution levels adjusted for CpG sites':
            raise InputFileError('The input file is not divsum file! Please check the input file or run mode')
        else:
            out = cTENOR.labeling(args.input)
            divsum_parser(out, args.divsum_file, outname)