import io
import os
import logging
import subprocess


def __get_sct_version():
    """Get git commit if in repo and version for the version.txt file

    :return: Tuple (install_type, sct_commit, sct_branch, version_sct)
    """
    sct_commit = __git_commit__
    sct_branch = __git_branch__

    if sct_commit is not 'unknown':
        install_type = 'git'
    else:
        install_type = 'package'

    with io.open(os.path.join(__sct_dir__, 'version.txt'), 'r') as myfile:
        version_sct = myfile.read().replace('\n', '')

    return install_type, sct_commit, sct_branch, version_sct


def __get_branch():
    """
    Fallback if for some reason the value vas no set by sct_launcher
    :return:
    """

    p = subprocess.Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=__sct_dir__)
    output, _ = p.communicate()
    status = p.returncode

    if status == 0:
        return output
    return 'unknown'


def __get_commit():
    """
    Fallback if for some reason the value vas no set by sct_launcher
    :return:
    """
    p = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=__sct_dir__)
    output, _ = p.communicate()
    status = p.returncode
    if status == 0:
        return output
    return 'unknown'


# Basic sct config
__sct_dir__ = os.getenv("SCT_DIR", os.path.dirname(os.path.realpath(__file__)).rstrip("scripts"))
__data_dir__ = os.getenv("SCT_DATA_DIR", "{}/data".format(__sct_dir__))
# Be careful no to change the order commit, branch and then version!
__git_commit__ = os.getenv("SCT_COMMIT", __get_commit())
__git_branch__ = os.getenv("SCT_BRANCH", __get_branch())
__version__ = '-'.join(__get_sct_version())

# statistic report level
__report_log_level__ = logging.ERROR
__report_exception_level__ = Exception
