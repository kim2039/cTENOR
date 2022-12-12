import csv, argparse, re
import os

def replace_unknown(out, file, outname):
    outdir = os.path.dirname(out)
    # check file exist
    filename = outdir + '/' + outname + '.align'
    if os.path.isfile(filename):
        os.remove(filename)

    # create dictionary of unknown
    rep = []
    with open(out) as f:
        reader = csv.reader(f)
        for i, line in enumerate(reader):
            if i == 0:
                pass
            else:
                rep.append([line[1], line[-1]])
    rep = dict(rep)
    print("Running...")
    with open(file) as f:
        for fline in f:
            # Find Unknown line
            if '#Unknown' in fline or '#LTR/Unknown' in fline:
                id_fline = re.findall('(\S+#\S+)', fline)[0]
                te_dict = rep.get(id_fline)
                if te_dict == None:
                    te_dict = 'Unknown'
                newline = re.sub('#\S+', '#'+te_dict, fline)

            else:
                newline = fline

            # write the line
            with open(filename, mode='a', encoding='utf-8') as outfile:
                outfile.write(newline)
    print('Done!')

if __name__ == '__main__':
    version = '1.0.0'
    print("alignment file replace version " + version + " with cTENOR ")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-a", "--align_file", help="Alignment file of RepeatMasker; *.align", required=True)
    parser.add_argument("-i", "--input", help="Result csv file 'cTENOR_out.csv", required=True)
    parser.add_argument("--prefix", help="prefix the output")
    parser.add_argument("-v", "--version", action='version', help='show this version', version='')
    args = parser.parse_args()

    # out file name
    if args.prefix:
        outname = args.prefix
    else:
        outname = 'cTENOR_replace'

    # check the header of the file
    replace_unknown(args.input, args.align_file, outname)