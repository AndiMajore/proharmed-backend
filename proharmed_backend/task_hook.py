class TaskHook:

    def __init__(self, parameters, set_status,set_result, set_files, set_progress):
        self.__parameters = parameters
        self.__set_result = set_result
        self.__set_status = set_status
        self.__set_files = set_files
        self.__set_progress = set_progress


    @property
    def parameters(self):
        """
        Returns parameters selected for the algorithm.

        :return: Parameters as dictionary (e.g. {"proteins": [...], "paramA": 123, "paramB": True, ...})
        """
        return self.__parameters


    def set_progress(self, progress,status):
        self.__set_progress(progress,status)
    def set_status(self, status):
        """
        To be called to indicate computation progress.

        :param progress: A float between 0.0 and 1.0 (e.g. 0.5 for 50% progress)
        :param status: A string indicating the status (e.g. 'Parsing file')
        :return:
        """
        self.__set_status(status)

    def set_files(self, files, uid):
        self.__set_files(files, uid)

    def set_results(self, filename):
        """
        To be called when the computation is finished.

        :param results: A dictionary containing a networks entry, each network having nodes and edges.
        (e.g. {"network": {"nodes": ["P61970", "Q9H4P4"], "edges": [{"from": "P61970", "to": "Q9H4P4"}]}})
        """
        self.__set_result(filename)
