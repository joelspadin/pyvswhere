r"""
Interface to Microsoft's Visual Studio locator tool, vswhere.

If Visual Studio 15.2 or later has been installed, this will use the vswhere
binary installed with Visual Studio. Otherwise, it will download the latest
release of vswhere from https://github.com/Microsoft/vswhere the first time a
function is called.
"""
import json
import os
import shutil
import subprocess

__version__ = '1.0'
__author__ = 'Joel Spadin'

DEFAULT_LOCATION = os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
DOWNLOAD_LOCATION = os.path.join(os.path.dirname(__file__), 'vswhere.exe')

LATEST_RELEASE_ENDPOINT = 'https://api.github.com/repos/Microsoft/vswhere/releases/latest'

def execute(args):
    """
    Call vswhere with the given arguments and return an array of results.

    `args` is a list of command line arguments to pass to vswhere.

    If the argument list contains '-property', this returns an array with the
    property value for each result. Otherwise, this returns an array of
    dictionaries containing the results.
    """
    is_property = '-property' in args

    args = [get_vswhere(), '-utf8'] + args

    if not is_property:
        args.extend(['-format', 'json'])

    output = subprocess.check_output(args)

    if is_property:
        return output.decode('utf-8').splitlines()
    else:
        return json.loads(output, encoding='utf-8')


def find(find_all=False, latest=False, legacy=False, prerelease=False, products=None, prop=None, requires=None, requires_any=False, version=None):
    """
    Call vswhere and return an array of the results.

    If `find_all` is true, finds all instances even if they are incomplete and may not launch.

    If `latest` is true, returns only the newest version and last installed.

    If `legacy` is true, also searches Visual Studio 2015 and older products.
    Information is limited. This option cannot be used with either products or requires.

    If `prerelease` is true, also searches prereleases. By default, only releases are searched.

    `products` is a list of one or more product IDs to find.
    Defaults to Community, Professional, and Enterprise if not specified.
    Specify ['*'] by itself to search all product instances installed.
    See https://aka.ms/vs/workloads for a list of product IDs.

    `prop` is the name of a property to return instead of the full installation details.
    Use delimiters '.', '/', or '_' to separate object and property names.
    Example: 'properties.nickname' will return the 'nickname' property under 'properties'.

    `requires` is a list of one or more workload component IDs required when finding instances.
    All specified IDs must be installed unless `requires_any` is True.
    See https://aka.ms/vs/workloads for a list of workload and component IDs.

    `version` is a version range for instances to find. Example: '[15.0,16.0)' will find versions 15.*.
    """
    args = []

    if find_all:
        args.append('-all')

    if latest:
        args.append('-latest')

    if legacy:
        args.append('-legacy')

    if prerelease:
        args.append('-prerelease')

    if products:
        args.append('-products')
        args.extend(products)

    if prop:
        args.append('-property')
        args.append(prop)

    if requires:
        args.append('-requires')
        args.extend(requires)

    if requires_any:
        args.append('-requiresAny')

    if version:
        args.append('-version')
        args.append(version)

    return execute(args)


def find_first(**kwargs):
    """
    Call vswhere and returns only the first result, or None if there are no results.

    See find() for parameters.
    """
    return next(iter(find(**kwargs)), None)


def get_latest():
    """
    Get the information for the latest installed version of Visual Studio.
    """
    return find_first(latest=True, legacy=True)


def get_latest_path():
    """
    Get the file path to the latest installed version of Visual Studio.

    Returns None if no installations could be found.
    """
    return find_first(latest=True, legacy=True, prop='installationPath')


def get_latest_version():
    """
    Get the version string of the latest installed version of Visual Studio.

    For Visual Studio 2017 and newer, this is the full version number, for
    example: '15.8.28010.2003'.

    For Visual Studio 2015 and older, this only contains the major version, with
    the minor version set to 0, for example: '14.0'.

    Returns None if no installations could be found.
    """
    return find_first(latest=True, legacy=True, prop='installationVersion')

def get_latest_major_version():
    """
    Get the major version of the latest installed version of Visual Studio as an integer.

    Returns 0 if no installations could be found.
    """
    return int(next(iter(get_latest_version().split('.')), '0'))


def get_vswhere():
    """
    Get the location of the vswhere executable.

    If vswhere is not already installed as part of Visual Studio, the latest
    release will be downloaded and stored alongside this script.
    """
    if os.path.exists(DEFAULT_LOCATION):
        return DEFAULT_LOCATION

    if os.path.exists(DOWNLOAD_LOCATION):
        return DOWNLOAD_LOCATION

    _download_vswhere()
    return DOWNLOAD_LOCATION


def _download_vswhere():
    """
    Download vswhere to DOWNLOAD_LOCATION.
    """
    try:
        from urllib.request import urlopen
        with urlopen(_get_latest_release_url()) as response, open(DOWNLOAD_LOCATION, 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
    except ImportError:
        # Python 2
        import urllib
        urllib.urlretrieve(_get_latest_release_url(), DOWNLOAD_LOCATION)


def _get_latest_release_url():
    """
    The the URL of the latest release of vswhere.
    """
    try:
        from urllib.request import urlopen
        with urlopen(LATEST_RELEASE_ENDPOINT) as response:
            release = json.loads(response.read(), encoding=response.headers.get_content_charset() or 'utf-8')
    except ImportError:
        # Python 2
        import urllib2
        response = urllib2.urlopen(LATEST_RELEASE_ENDPOINT)
        release = json.loads(response.read(), encoding=response.headers.getparam('charset') or 'utf-8')

    for asset in release['assets']:
        if asset['name'] == 'vswhere.exe':
            return asset['browser_download_url']

    raise Exception('Could not locate the latest release of vswhere.')