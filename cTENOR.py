import argparse
import pandas as pd
import glob
import re
import subprocess, os
import pathlib
import shutil

def run_process(fasta, dir, sp):
    conf = os.path.dirname(os.path.abspath(__file__))+'/cTENOR_configure'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(conf):
        print("configure file found")
        with open(conf) as f:
            s = f.read()
            deepTE_dir = s.split('\n')[0]
            RFSB_dir = s.split('\n')[1]

        # DeepTE

        # Check DeepTE h5 file exist
        if sp == 'P':
            sp_name = 'Plants'
        elif sp == 'M':
            sp_name = 'Metazoans'
        elif sp == 'F':
            sp_name = 'Fungi'
        else:
            sp_name = 'Others'

        # mkdir the download directory
        os.makedirs(str(base_dir)+'/tmp', exist_ok=True)

        dir_path = str(base_dir)+ '/tmp/download_' + sp + '_model_dir/' + sp_name + '_model'
        print(dir_path, os.path.exists(dir_path))

        try:
            if os.path.exists(dir_path):
                cmd = ['python', deepTE_dir+'DeepTE.py', '-d', dir, '-o', dir, '-i', fasta, '-sp', sp, '-m_dir', dir_path]
            else:
                cmd = ['python', deepTE_dir+'DeepTE.py', '-d', dir, '-o', dir, '-i', fasta, '-sp', sp, '-m', sp]
            print("Running DeepTE...")
            proc = subprocess.run(cmd, check=True)

            # move model dir
            if cmd[-1] == sp:
                print('moving model dir...')
                new_path = shutil.move(dir + '/download_' + sp + '_model_dir/', str(base_dir)+ '/tmp/')
                print('moved to ', new_path)


            print("Done")

            # RFSB
            print("Running RFSB...")
            cmd = ['transposon_classifier_RFSB', '-mode', 'classify', '-fastaFile', dir + '/opt_DeepTE.fasta', '-outputPredictionFile', dir + '/RFSB_result.txt']
            proc = subprocess.run(cmd, check=True)

            print('Done!')

        except subprocess.CalledProcessError as e:
            print(e)

    else:
        print("Error: run configure.py before running cTENOR")
        raise(InputFileError)

def replace(df, fasta, outdir):
    df = df.set_index('TE_name')
    # check file exist
    filename = '/cTENOR_out.fasta'
    if os.path.isfile(outdir+filename):
        os.remove(outdir+filename)
    with open(fasta) as f:
        for fline in f:
            # Find Unknown line
            if 'Unknown' in fline:
                id_fline = re.findall('(\S+)', fline)[0][1:]
                te_name = df.at[id_fline, 'Consensus']
                if te_name == None:
                    te_name = 'Unknown'
                newline = re.sub('#\S+', '#'+te_name, fline)

            else:
                newline = fline

            # write the line
            with open(outdir + filename, mode='a', encoding='utf-8') as outfile:
                outfile.write(newline)

    print('Save output fasta file as "cTENOR_out.fasta".')

def labeling(outdir, threshold):
    print("Start labeling...")
    # import and merge DeepTE files
    allres = pd.read_csv(outdir + '/store_temp_opt_dir/opt_DeepTE.txt', sep='\t', names=('TE_name', 'DeepTE'))
    allres = pd.concat([allres, allres['TE_name'].str.extract('#(.+)', expand=True).rename(columns={0: 'RepeatModeler'})], axis=1)

    filelist = glob.glob(outdir + '/store_temp_opt_dir/*_probability_results.txt')
    filelist.sort()

    for f in filelist:
        tmp = pd.read_csv(f, sep='\t')
        allres = pd.merge(allres, tmp, on='TE_name', how='left')
        
    #allres.to_csv('cTENOR_Prob.csv')
    allres['DeepTE'] = allres['DeepTE'].str.replace('unknown_nMITE', 'ClassII')
    allres['DeepTE'] = allres['DeepTE'].str.replace('unknown_unknown', 'ClassII')
    allres['DeepTE'] = allres['DeepTE'].str.replace('unknown_MITE', 'ClassII')
    allres['DeepTE'] = allres['DeepTE'].str.replace('_nMITE', '')
    allres['DeepTE'] = allres['DeepTE'].str.replace('_MITE', '')
    allres['DeepTE'] = allres['DeepTE'].str.replace('_unknown', '')


    # Classの確率を求める
    TEclass = allres['DeepTE'].str.extract('(ClassI+)')
    TEclass[0] = TEclass[0].str.replace('unknown', 'ClassII')

    for c in TEclass.itertuples():
        if pd.isnull(c[1]):
            allres.at[c[0], "DeepTE_Class_prob"] = float('nan')
        else:
            
            allres.at[c[0], "DeepTE_Class_prob"] = allres.at[c[0], c[1]]
        
    # Family の確率を求める
    for c in allres.itertuples():
        try:
            if c.DeepTE != 'ClassI' and c.DeepTE != 'ClassII':
                allres.at[c[0], "DeepTE_Family_prob"] = allres.at[c[0], c.DeepTE]

        except KeyError:
            allres.at[c[0], "DeepTE_Family_prob"] = float('nan')
            
    rest = allres[['TE_name', 'RepeatModeler', 'DeepTE', 'DeepTE_Class_prob', 'DeepTE_Family_prob']]
    
    # Initialize Dataframe
    rfsb_df = pd.DataFrame(index=[], columns=['TE_name', 'RFSB', 'RFSB_Class_prob', 'RFSB_Family_prob'])
    count = 0

    # RFSBのデータ
    with open(outdir + '/RFSB_result.txt') as f:
        for s_line in f:
            if s_line[0] != "\n" and s_line[0] != '#':
                if s_line[0] == '>':  # Header
                    TE_name = re.findall('>(.+?)__', s_line)[0]
                    
                else:  # Prob
                    # Class
                    rfsb = s_line.split(' ')[0].split(',')
                    rfsb = [s.replace('DNATransposon', 'DNA').replace('Retrotransposon', 'Retro').replace('TIR', 'DNA').replace('Tc1-Mariner', 'TcMar') for s in rfsb]
                    if 'Helitron' in rfsb:
                        rfsb = 'RC/Helitron'
                    else:
                        if len(rfsb) >= 3:
                            rfsb = rfsb[1] + '/' + rfsb[0]
                        else:
                            rfsb = rfsb[-1]

                    # Prob
                    irfsb = s_line.split(' ')[1]
                    dict_prob =  {'1':0, '1/1':1, '1/1/1':2, '1/1/2':3, '1/1/3':4, '1/2':5, '1/2/1':6, '1/2/2':7, '2':8, '2/1':9, '2/1/1':10, '2/1/2':11, '2/1/3':12, '2/1/4':13, '2/1/5':14, '2/1/6':15, '2/2':16, '2/3':17}
                    prfsb = s_line.split(' ')[3:-1]
                    class_rfsb = irfsb.split('/')[0]
                    
                    rfsb_df.loc[count] = [TE_name, rfsb, prfsb[dict_prob[class_rfsb]], prfsb[dict_prob[irfsb]]]
                    count += 1
                    
    rfsb_df

    # Rename
    res = pd.merge(rest, rfsb_df, on='TE_name')
    res['DeepTE'] = res['DeepTE'].str.replace('ClassIII_Helitron', 'RC/Helitron')
    res['DeepTE'] = res['DeepTE'].str.replace('ClassII_', '')
    res['DeepTE'] = res['DeepTE'].str.replace('ClassII', 'DNA')
    res['DeepTE'] = res['DeepTE'].str.replace('ClassI_', '')
    res['DeepTE'] = res['DeepTE'].str.replace('ClassI', 'Retroposon')
    res['DeepTE'] = res['DeepTE'].str.replace('nLTR_', '')
    res['DeepTE'] = res['DeepTE'].str.replace('nLTR', 'Retroposon')
    res['DeepTE'] = res['DeepTE'].str.replace('DIRS', 'LTR/DIRS')
    res['DeepTE'] = res['DeepTE'].str.replace('_', '/')
    res['RFSB_Family_prob'] = res['RFSB_Family_prob'].astype('float')
    res['RFSB_Class_prob'] = res['RFSB_Class_prob'].astype('float')

    for c in res.itertuples():
        if not "Unknown" in c.RepeatModeler:
            res.at[c[0], "Consensus"] = c.RepeatModeler
        else:
            # Unknown LTR classify
            if "LTR" in c.RepeatModeler:   
                #print(round(c.DeepTE_Family_prob, 1), c.RFSB_Family_prob)
                if "LTR/" in c.DeepTE and "LTR/" in c.RFSB:  # Both
                    if round(c.DeepTE_Family_prob, 1) >= c.RFSB_Family_prob:
                        if c.DeepTE_Family_prob >= threshold:
                            res.at[c[0], "Consensus"] = c.DeepTE
                        else:
                            res.at[c[0], "Consensus"] = c.RepeatModeler
                    else:
                        if c.RFSB_Family_prob >= threshold:
                            res.at[c[0], "Consensus"] = c.RFSB
                        else:
                            res.at[c[0], "Consensus"] = c.RepeatModeler
                        
                # Only DeepTE
                elif "LTR/" in c.DeepTE and not "LTR/" in c.RFSB:
                    if c.DeepTE_Family_prob >= threshold:
                        res.at[c[0], "Consensus"] = c.DeepTE
                    else:
                        res.at[c[0], "Consensus"] = c.RepeatModeler
                
                # Only RFSB   
                elif "LTR/" in c.RFSB and not "LTR/" in c.DeepTE:
                    if c.RFSB_Family_prob >= threshold:
                        res.at[c[0], "Consensus"] = c.RFSB
                    else:
                        res.at[c[0], "Consensus"] = c.RepeatModeler
                    
                else:
                    res.at[c[0], "Consensus"] = c.RepeatModeler
            
            # Unknown classify
            else:
                if c.DeepTE == c.RFSB:
                    res.at[c[0], "Consensus"] = c.DeepTE
                else: 
                    # same class
                    if c.DeepTE.split('/')[0] == c.RFSB.split('/')[0]:
                        if round(c.DeepTE_Family_prob, 1) >= c.RFSB_Family_prob:
                            if round(c.DeepTE_Family_prob, 1) >= threshold:
                                res.at[c[0], "Consensus"] = c.DeepTE
                            else:
                                res.at[c[0], "Consensus"] = c.DeepTE.split('/')[0]
                        else:
                            if c.RFSB_Family_prob >= threshold:
                                res.at[c[0], "Consensus"] = c.RFSB
                            else:
                                res.at[c[0], "Consensus"] = c.DeepTE.split('/')[0]                
                                
                    
                    # Not same class
                    else:
                        if round(c.DeepTE_Class_prob, 1) >= c.RFSB_Class_prob:
                            if c.DeepTE == 'RC/Helitron':
                                res.at[c[0], "Consensus"] = c.DeepTE
                            else:
                                if round(c.DeepTE_Family_prob, 1) >= threshold:
                                    res.at[c[0], "Consensus"] = c.DeepTE
                                else:
                                    res.at[c[0], "Consensus"] = c.DeepTE.split('/')[0]
                        else:
                            if c.RFSB_Family_prob >= threshold:
                                res.at[c[0], "Consensus"] = c.RFSB
                            else:
                                res.at[c[0], "Consensus"] = c.RFSB.split('/')[0]          
    res.to_csv(outdir + '/cTENOR_out.csv')
    print("Labeling completed!")
    return res

class InputFileError(Exception):
    pass

if __name__ == '__main__':
    version = '1.1.3'
    print("cTENOR version " + version)

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-f", "--fasta", help="library fasta file which is outputfile of RepeatModeler", required=True, type=pathlib.Path)
    parser.add_argument("-d", "--directory", help="Output directory", required=True, type=pathlib.Path)
    parser.add_argument("-sp", "--species", help="P or M or F or O. P:Plants, M:Metazoans, F:Fungi, and O: Others.", required=True, choices=['P', 'M', 'F', 'O'])
    parser.add_argument("-s", "--skip", action='store_true', help="Skip running DeepTE and RFSB (Please assign the directory containing the results of the previous analysis)")
    parser.add_argument("-t", "--threshold", type=float, help='set threshold for family classification', default=0.8)
    parser.add_argument("-v", "--version", action='version', help='show this version', version='')

    args = parser.parse_args()

    # check threthold
    if args.threshold > 1 or args.threshold <0:
        print('set threthold 0 <= t <= 1')
        raise(InputFileError)

    # Path convert
    fasta = str(args.fasta.resolve())
    directory = str(args.directory.resolve())

    # not skipping case
    if not args.skip:
        print('Processing DeepTE and RFSB...')
        run_process(fasta, directory, args.species)

    cternor_res = labeling(directory, args.threshold)
    replace(cternor_res, fasta, directory)