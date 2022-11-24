import cTENOR
import csv, argparse, re
import os

def replace_unknown(out, file, outname):
    # check file exist
    filename = outname + '.align'
    if os.path.isfile(filename):
        os.remove(filename)

    # create dictionary of unknown
    rep = []
    del out[0]
    for o in out:
        if o[2] != 'RepeatModeler':
            if o[1] != 'Unknown':
                rep.append(o[0:2])
    rep = dict(rep)

    with open(file) as f:
        for fline in f:
            # Find Unknown line
            if '#Unknown' in fline:
                id_fline = re.findall('(\S+)#', fline)[0]
                te_dict = rep.get(id_fline)
                if te_dict == None:
                    te_dict = 'Unknown'
                print(id_fline, te_dict)
                newline = re.sub('#\S+', '#'+te_dict, fline)
                print('FounD!', fline, newline)

            else:
                newline = fline

            # write the line
            with open(filename, mode='a', encoding='utf-8') as outfile:
                outfile.write(newline)
            

    pass

if __name__ == '__main__':
    print("alignmentfile replace with cTENOR")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-a", "--align_file", help="Alignment file of RepeatMasker; *.align", required=True)
    parser.add_argument("-i", "--input", help="Result txt file of deepTE -> TEclass -> RF", required=True)
    parser.add_argument("-o", "--output", help="Prefix of output file name")
    args = parser.parse_args()

    # out file name
    if args.output:
        outname = args.output
    else:
        outname = 'cTENOR_replace'

    # check the header of the file
    out = cTENOR.labeling(args.input)
    replace_unknown(out, args.align_file, outname)