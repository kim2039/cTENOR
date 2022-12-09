import argparse
import pandas as pd
import numpy as np
import glob
import re
import subprocess, os
import urllib.request

def run_process(fasta, dir, sp):
    if os.path.exists('./cTENOR_configure'):
        print("configure file found")
        with open('cTENOR_configure') as f:
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

        dir_path = dir + 'download_' + sp + '_model_dir/' + sp_name + '_model'
        print(dir_path, os.path.exists(dir_path))

        try:
            if os.path.exists(dir_path):
                cmd = ['python', deepTE_dir+'DeepTE.py', '-d', dir, '-o', dir, '-i', fasta, '-sp', sp, '-m_dir', dir_path]
            else:
                cmd = ['python', deepTE_dir+'DeepTE.py', '-d', dir, '-o', dir, '-i', fasta, '-sp', sp, '-m', sp]
            proc = subprocess.run(cmd, check=True)
            
            # RFSB
            cmd = ['transposon_classifier_RFSB', '-mode', 'classify', '-fastaFile', dir + 'opt_DeepTE.fasta', '-outputPredictionFile', dir + 'RFSB_result.txt']
            proc = subprocess.run(cmd, check=True)

            print('Done!')

        except subprocess.CalledProcessError as e:
            print(e)

    else:
        print("Error: run configure.py before running cTENOR")
        raise(InputFileError)


def labeling(itext):
    out = [['RMid', 'family', 'origin']]
    with open(itext) as f:
        flag = False
        for s_line in f:
            if not flag:
                if s_line[0] == '>':
                    id = re.findall('>(.+?)#', s_line)[0]
                    rm = re.findall('#(.+)__', s_line)[0]
                    print(">", id)

                    # RepeatModelerでUnknownの場合、DeepTEの結果を検索
                    if rm == 'Unknown':
                        dte = re.findall('__(.+?)\|', s_line)
                        dte = dte[0].split('_')

                        # DeepTEでもUnknownの場合、あるいは正確なドメインまでわからない場合はRFSBとTEclassの結果から導く
                        if dte[0] == 'unknown' or (len(dte) < 3 and not 'Helitron' in dte):
                            tec = re.findall('TEclass result: (.+)\|', s_line)[0]
                            flag = True

                        else: # DeepTEにアノテーションがついている場合
                            # データをRM形式に戻す
                            if 'Helitron' in dte:
                                odte = 'RC/Helitron'
                            elif 'SINE' in dte:
                                if len(dte) >= 4:
                                    odte = 'SINE/' + dte[3]
                                else:
                                    odte = 'SINE'
                            elif 'LINE' in dte:
                                if len(dte) >= 4:
                                    odte = 'LINE/' + dte[3]
                                else:
                                    odte = 'LINE'
                            else:
                                odte = dte[1] + '/' + dte[2]
                            out.append([id, odte, 'DeepTE'])
                            print('DeepTE: ', odte, '\n')
                        

                    else: # RepeatModelerでアノテーションがついている場合
                        out.append([id, rm, 'RepeatModeler'])
                        print('RepeatModeler: ', rm, '\n')

            else: # RFSBの読み込み
                flag = False
                rfsb = s_line.split(' ')[0].split(',')
                rfsb = [s.replace('DNATransposon', 'DNA').replace('Retrotransposon', 'Retro').replace('TIR', 'DNA').replace('Tc1-Mariner', 'TcMar') for s in rfsb]
                

                # Compare RFSB and TEclass
                if tec in rfsb:
                    if 'Helitron' in rfsb:
                        orfsb = 'RC/Helitron'
                    else:
                        if len(rfsb) >= 3:
                            orfsb = rfsb[1] + '/' + rfsb[0]
                        else:
                            orfsb = rfsb[-1]
                    out.append([id, orfsb, 'RFSB'])
                    print('RFSB and TEclass: ', orfsb,'\n')
                else:
                    out.append([id, 'Unknown', 'NA'])
                    print('unclear...ingnore the sequence', '\n')

    # Output the result
    with open('out_cTENOR.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(out)

    return out



class InputFileError(Exception):
    pass

if __name__ == '__main__':
    print("cTENOR version 0.2.0")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-f", "--fasta", help="library fasta file which is outputfile of RepeatModeler", required=True)
    parser.add_argument("-d", "--directory", help="Output directory", required=True)
    parser.add_argument("-sp", "--species", help="P or M or F or O. P:Plants, M:Metazoans, F:Fungi, and O: Others.", required=True)
    parser.add_argument("-s", "--skip", action='store_true', help="Skip running DeepTE and RFSB (Please assign the directory containing the results of the previous analysis)")

    args = parser.parse_args()
    
    if args.directory[-1] == '/':
        directory = args.directory
    else:
        directory = args.directory + '/'

    if not args.skip:
        print('Processing DeepTE and RFSB...')
        run_process(args.fasta, directory, args.species)

    else:  # Skipped
        print('Skipped')
    