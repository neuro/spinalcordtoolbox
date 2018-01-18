import io
import os
import logging
import subprocess



def _get_sct_version():
    """Get git commit if in repo and version for the version.txt file

    :return: Tuple (install_type, sct_commit, sct_branch, version_sct)
    """
    sct_commit = 'unknown'
    sct_branch = 'unknown'

    if os.path.isdir(os.path.join(__sct_dir__, '.git')):
        install_type = 'git'
        p = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         cwd=__sct_dir__)
        output, _ = p.communicate()
        status = p.returncode
        if status == 0:
            sct_commit = output
        p = subprocess.Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, cwd=__sct_dir__)
        output, _ = p.communicate()
        status = p.returncode

        if status == 0:
            sct_branch = output
    else:
        install_type = 'package'

    with io.open(os.path.join(__sct_dir__, 'version.txt'), 'r') as myfile:
        version_sct = myfile.read().replace('\n', '')

    return install_type, sct_commit, sct_branch, version_sct


# Basic sct config
__sct_dir__ = os.getenv("SCT_DIR", os.path.dirname(os.path.realpath(__file__)).rstrip("scripts"))
__data_dir__ = os.getenv("SCT_DATA_DIR", "{}/data".format(__sct_dir__))
__version__ = '-'.join(_get_sct_version())


# statistic report level
__report_log_level__ = logging.ERROR
__report_exception_level__ = Exception
