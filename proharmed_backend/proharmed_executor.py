import os
import zipfile

from mqhandler import filter_ids as fi
from mqhandler.mq_utils.plotting import *
from mqhandler import remap_genenames as rmg
from mqhandler import map_orthologs as mo
from mqhandler import reduce_genenames as rdg
from mqhandler import intersection_analysis as ia




from proharmed_backend.task_hook import TaskHook


def getFiles(uid, skip):
    dict = {'csv': {}, 'png': {}, 'txt': {}, 'zip': {}, 'other': {}}
    zip_name = uid + '.zip'
    from proharmed_backend.views import get_wd
    wd = get_wd(uid)
    zip_path = os.path.join(wd, zip_name)
    zip = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for file in os.listdir(wd):
        if file in skip:
            continue
        if file != zip_name:
            file_path = os.path.join(wd, file)
            zip.write(file_path, os.path.relpath(file_path, os.path.join(wd, '..')))
            if file.endswith('.csv'):
                dict['csv'][file] = file_path
            elif file.endswith('.png'):
                dict['png'][file] = file_path
            elif file.endswith('.txt'):
                dict['txt'][file] = file_path
            else:
                dict['other'][file] = file_path
    zip.close()
    dict['zip'][zip_name] = zip_path
    return dict


def get_delimiter(file, type):
    if type == 'tsv':
        return '\t'
    if type == 'csv':
        return ','
    import csv
    sniffer = csv.Sniffer()
    with open(file, 'r') as fh:
        for line in fh.readlines():
            return sniffer.sniff(line).delimiter
    return ","


def get_output_file_name(filename, suffix, type):
    if len(type) > 0:
        filename = filename.replace(f".{type}", f"_{suffix}.{type}")
    else:
        filename = f"{filename}_{suffix}"
    return filename


def run_intersect(hook: TaskHook):
    from proharmed_backend.views import get_wd
    hook.set_progress(0.1, "Preparing")
    data = hook.parameters
    wd = get_wd(data.get('uid'))
    dfs = list()
    columns = data.get('columns')
    out_name = f'intersection_{data.get("uid")}.csv'
    for f in data.get('filenames'):
        file = f.split('.')
        type = f[len(file) - 1]
        sep = get_delimiter(os.path.join(wd, f), type)
        dfs.append(pd.read_csv(os.path.join(wd, f), sep=sep))
    hook.set_progress(0.15, "Reading data")
    r = ia.load_multi_files(dfs, columns)
    hook.set_progress(0.2, "Executing")
    result = ia.count_intersection(data=r, threshold=int(data.get('threshold')))
    hook.set_progress(0.5, "Writing files")
    result.to_csv(os.path.join(wd, out_name), index=False, sep=',')
    hook.set_progress(0.7, "Plotting")
    ia.plot_intersections(data= r, out_dir=wd, file_type = "png")
    hook.set_progress(0.9, "Collecting results")
    hook.set_files(files=getFiles(uid=data.get('uid'), skip=[]), uid=data.get("uid"))
    hook.set_results(out_name)


def run_filter(hook: TaskHook):
    from proharmed_backend.views import get_wd
    hook.set_progress(0.1, "Preparing")
    data = hook.parameters
    wd = get_wd(data.get('uid'))
    file = data.get('filename').split('.')
    type = file[len(file) - 1]
    out_name = get_output_file_name(data.get('filename'), "filtered", type)
    sep = get_delimiter(os.path.join(wd, data.get('filename')), type)
    hook.set_progress(0.15, "Reading data")
    df = pd.read_csv(os.path.join(wd, data.get('filename')), sep=sep)
    hook.set_progress(0.2, "Executing")
    R_filtered_df, R_log_dict = fi.filter_protein_ids(data=df, protein_column=data.get('column'),
                                                      organism=data.get('organism'), rev_con=data.get('revCon'),
                                                      keep_empty=data.get('keep'), reviewed=data.get('reviewed'),
                                                      res_column=data.get('resultColumn'))
    hook.set_progress(0.5, "Writing files")

    R_filtered_df.to_csv(os.path.join(wd, out_name), index=False, sep=sep)
    R_log_dict['Overview_Log'].to_csv(os.path.join(wd, 'overview_log.txt'))
    R_log_dict['Detailed_Log'].to_csv(os.path.join(wd, 'detailed_log.txt'))
    hook.set_progress(0.7, "Plotting")
    create_overview_plot(logging=R_log_dict["Overview_Log"], out_dir=wd, file_type="png")

    create_filter_detailed_plot(logging=R_log_dict["Detailed_Log"],
                                organism=data.get('organism'),
                                out_dir=get_wd(data.get('uid')), file_type="png")
    hook.set_progress(0.9, "Collecting results")
    hook.set_files(files=getFiles(uid=data.get('uid'), skip=[data.get('filename')]), uid=data["uid"])
    hook.set_results(out_name)


def run_remap(hook: TaskHook):
    from proharmed_backend.views import get_wd
    hook.set_progress(0.1, "Preparing")
    data = hook.parameters
    wd = get_wd(data.get('uid'))
    file = data.get('filename').split('.')
    type = file[len(file) - 1]
    out_name = get_output_file_name(data.get('filename'), "remapped", type)
    sep = get_delimiter(os.path.join(wd, data.get('filename')), type)

    hook.set_progress(0.15, "Reading data")
    df = pd.read_csv(os.path.join(wd, data.get('filename')), sep=sep)
    fasta = os.path.join(wd, data.get('fast')) if 'fasta' in data else None
    hook.set_progress(0.2, "Executing")
    R_remapped_df, R_log_dict = rmg.remap_genenames(data=df, mode=data.get('mode'), protein_column=data.get('p_column'),
                                                    gene_column=data.get('g_column'), skip_filled=data.get('skip'),
                                                    organism=data.get('organism'), keep_empty=data.get('keep'),
                                                    res_column=data.get('resultColumn'), fasta=fasta)
    hook.set_progress(0.5, "Writing files")
    R_remapped_df.to_csv(os.path.join(wd, out_name), index=False, sep=sep)
    R_log_dict['Overview_Log'].to_csv(os.path.join(wd, 'overview_log.txt'))
    R_log_dict['Detailed_Log'].to_csv(os.path.join(wd, 'detailed_log.txt'))
    hook.set_progress(0.7, "Plotting")
    create_overview_plot(logging=R_log_dict["Overview_Log"], out_dir=wd, file_type="png")
    hook.set_progress(0.9, "Collecting results")
    hook.set_files(files=getFiles(data.get('uid'), skip=[data.get('filename')]), uid=data["uid"])
    hook.set_results(out_name)


def run_reduce(hook: TaskHook):
    from proharmed_backend.views import get_wd
    hook.set_progress(0.1, "Preparing")
    data = hook.parameters
    wd = get_wd(data.get('uid'))
    file = data.get('filename').split('.')
    type = file[len(file) - 1]
    out_name = get_output_file_name(data.get('filename'), "reduced", type)
    sep = get_delimiter(os.path.join(wd, data.get('filename')), type)

    hook.set_progress(0.15, "Reading data")
    df = pd.read_csv(os.path.join(wd, data.get('filename')), sep=sep)
    hook.set_progress(0.2, "Executing")
    R_remapped_df, R_log_dict = rdg.reduce_genenames(data=df, mode=data.get('mode'), gene_column=data.get('g_column'),
                                                     organism=data.get('organism'), keep_empty=data.get('keep'),
                                                     res_column=data.get('resultColumn'))
    hook.set_progress(0.5, "Writing files")
    R_remapped_df.to_csv(os.path.join(wd, out_name), index=False, sep=sep)
    R_log_dict['Overview_Log'].to_csv(os.path.join(wd, 'overview_log.txt'))
    R_log_dict['Detailed_Log'].to_csv(os.path.join(wd, 'detailed_log.txt'))

    hook.set_progress(0.7, "Plotting")
    create_overview_plot(logging=R_log_dict["Overview_Log"], out_dir=wd, file_type="png")
    create_reduced_detailed_plot(logging=R_log_dict["Detailed_Log"], out_dir=get_wd(data.get('uid')), file_type="png")

    hook.set_progress(0.9, "Collecting results")
    hook.set_files(files=getFiles(data.get('uid'), skip=[data.get('filename')]), uid=data["uid"])
    hook.set_results(out_name)


def run_ortho(hook: TaskHook):
    from proharmed_backend.views import get_wd
    hook.set_progress(0.1, "Preparing")
    data = hook.parameters
    wd = get_wd(data.get('uid'))
    file = data.get('filename').split('.')
    type = file[len(file) - 1]
    out_name = get_output_file_name(data.get('filename'), "ortho_mapped", type)
    sep = get_delimiter(os.path.join(wd, data.get('filename')), type)

    hook.set_progress(0.15, "Reading data")
    df = pd.read_csv(os.path.join(wd, data.get('filename')), sep=sep)
    hook.set_progress(0.2, "Executing")

    R_remapped_df, R_log_dict = mo.map_orthologs(data=df, gene_column=data.get('g_column'),
                                                 organism=data.get('organism'), keep_empty=data.get('keep'),
                                                 res_column=data.get('resultColumn'),
                                                 tar_organism=data.get('t_organism'))
    hook.set_progress(0.5, "Writing files")
    R_remapped_df.to_csv(os.path.join(wd, out_name), index=False, sep=sep)
    R_log_dict['Overview_Log'].to_csv(os.path.join(wd, 'overview_log.txt'))
    R_log_dict['Detailed_Log'].to_csv(os.path.join(wd, 'detailed_log.txt'))
    hook.set_progress(0.7, "Plotting")

    create_overview_plot(logging=R_log_dict["Overview_Log"], out_dir=wd, file_type="png")
    create_ortholog_detailed_plot(logging=R_log_dict["Detailed_Log"], out_dir=get_wd(data.get('uid')), file_type="png",
                                  organism=data.get('organism'))

    hook.set_progress(0.9, "Collecting results")
    hook.set_files(files=getFiles(data.get('uid'), skip=[data.get('filename')]), uid=data["uid"])
    hook.set_results(out_name)
