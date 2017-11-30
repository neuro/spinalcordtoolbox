import commands
import os
import logging


def _get_sct_version():
    """Get git commit if in repo and version for the version.txt file

    :return: Tuple (install_type, sct_commit, sct_branch, version_sct)
    """
    sct_commit = ''
    sct_branch = ''
    # fetch true commit number and branch
    # first, make sure there is a .git folder
    if os.path.isdir(os.path.join(__sct_dir__, '.git')):
        install_type = 'git'
        sct_commit = commands.getoutput('git rev-parse HEAD')
        sct_branch = commands.getoutput('git branch | grep \*').strip('* ')
        if not (sct_commit.isalnum()):
            sct_commit = 'unknown'
            sct_branch = 'unknown'
    else:
        install_type = 'package'
    # fetch version
    with open(os.path.join(__sct_dir__, 'version.txt'), 'r') as myfile:
        version_sct = myfile.read().replace('\n', '')

    return install_type, sct_commit, sct_branch, version_sct


# Basic sct config
__sct_dir__ = os.getenv("SCT_DIR", os.path.dirname(os.path.realpath(__file__)).rstrip("scripts"))
__data_dir__ = os.getenv("SCT_DATA_DIR", "{}/data".format(__sct_dir__))
__version__ = '-'.join(_get_sct_version())


# statistic report level
__report_log_level__ = logging.ERROR
__report_exception_level__ = Exception
