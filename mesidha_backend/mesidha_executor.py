import zipfile

from mqhandler import filter_ids as fi
from mqhandler.mq_utils.plotting import *

from mesidha_backend.versions import save_version, get_version
from mesidha_backend.task_hook import TaskHook


def precompute_examples():
    version = get_version()
    if version is None:
        save_version()
    # from mesidha_backend.updater import run_examples
    # run_examples()


def validate(tar, tar_id, mode, ref, ref_id, enriched, runs, background_model, background_network, replace, distance,
             out_dir, uid,
             set_progress):
    if enriched is None:
        enriched = False
    if runs is None:
        runs = 1000
    if background_model is None:
        background_model = "complete"
    if replace is None:
        replace = 100
    return {}


def getFiles(uid, skip):
    dict = {'csv': {}, 'png': {}, 'txt': {}, 'zip': {}}
    zip_name = uid + '.zip'
    from mesidha_backend.views import get_wd
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
            if file.endswith('.png'):
                dict['png'][file] = file_path
            if file.endswith('.txt'):
                dict['txt'][file] = file_path
    zip.close()
    dict['zip'][zip_name] = zip_path
    return dict


def run_filter(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    from mesidha_backend.views import get_wd
    wd = get_wd(data.get('uid'))
    R_data = pd.read_csv(os.path.join(wd, data.get('filename')))
    R_filtered_df, R_log_dict = fi.filter_protein_ids(data=R_data, protein_column=data.get('column'),
                                                      organism=data.get('organism'), rev_con=data.get('revCon'),
                                                      keep_empty=data.get('keep'), reviewed=data.get('reviewed'),
                                                      res_column=data.get('res_column'))

    R_filtered_df.to_csv(os.path.join(wd, 'df.csv'), index=False)
    R_log_dict['Overview_Log'].to_csv(os.path.join(wd, 'overview_log.txt'))
    R_log_dict['Detailed_Log'].to_csv(os.path.join(wd, 'detailed_log.txt'))

    create_overview_plot(logging=R_log_dict["Overview_Log"], out_dir=wd, file_type="png")

    create_filter_detailed_plot(logging=R_log_dict["Detailed_Log"],
                                organism=data.get('organism'), reviewed=data.get('reviewed'), decoy=data.get('revCon'),
                                out_dir=get_wd(data.get('uid')), file_type="png")

    hook.set_files(files=getFiles(data.get('uid'),skip=[data.get('filename')]), uid=data["uid"])
    hook.set_results()


def run_subnetwork(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    network = None
    if 'network_data' in data:
        network = data['network_data']
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="subnetwork",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None,
                      background_model=data["background_model"], background_network=network,
                      distance=data["distance"], out_dir=data["out"],
                      uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_subnetwork_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    network = None
    if 'network_data' in data:
        network = data['network_data']
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="subnetwork_set",
                      runs=data["runs"],
                      replace=data["replace"], ref=data["reference"], ref_id=data["reference_id"],
                      enriched=data["enriched"],
                      background_model=data["background_model"], background_network=network,
                      distance=data["distance"], out_dir=data["out"],
                      uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_cluster(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="clustering",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None,
                      background_model=data["background_model"],
                      background_network=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_set_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                      ref=data["reference"], mode="set-set", runs=data["runs"],
                      replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],
                      background_network=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_id_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                      ref=data["reference"], mode="id-set", runs=data["runs"],
                      replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],
                      background_network=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])
# def init(self):

# ru.print_current_usage('Load mappings for input into cache ...')
# mapper = FileMapper()
# mapper.load_mappings()
