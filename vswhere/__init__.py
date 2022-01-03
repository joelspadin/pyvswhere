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

__version__ = '1.3.0'
__author__ = 'Joel Spadin'
__license__ = 'MIT'

LATEST_RELEASE_ENDPOINT = 'https://api.github.com/repos/Microsoft/vswhere/releases/latest'
DOWNLOAD_PATH = os.path.join(os.path.dirname(__file__), 'vswhere.exe')

if 'ProgramFiles(x86)' in os.environ:
    DEFAULT_PATH = os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
else:
    DEFAULT_PATH = None

alternate_path = None
download_mirror_url = None


def execute(args):
    """
    Call vswhere with the given arguments and return an array of results.

    `args` is a list of command line arguments to pass to vswhere.

    If the argument list contains '-property', this returns an array with the
    property value for each result. Otherwise, this returns an array of
    dictionaries containing the results.
    """
    is_property = '-property' in args

    args = [get_vswhere_path(), '-utf8'] + args

    if not is_property:
        args.extend(['-format', 'json'])

    output = subprocess.check_output(args).decode('utf-8')

    if is_property:
        return output.splitlines()
    else:
        return json.loads(output)


def find(
    find=None,
    find_all=False,
    latest=False,
    legacy=False,
    path=None,
    prerelease=False,
    products=None,
    prop=None,
    requires=None,
    requires_any=False,
    sort=False,
    version=None,
):
    """
    Call vswhere and return an array of the results.

    Selection Options:
        find_all: If True, finds all instances even if they are incomplete and
            may not launch.
        prerelease: If True, also searches prereleases. By default, only
            releases are searched.
        products: a product ID or list of one or more product IDs to find.
            Defaults to Community, Professional, and Enterprise if not specified.
            Specify '*' by itself to search all product instances installed.
            See https://aka.ms/vs/workloads for a list of product IDs.
        requires: a workload component ID or list of one or more IDs required
            when finding instances. All specified IDs must be installed unless
            `requires_any` is True. See https://aka.ms/vs/workloads for a list
            of workload and component IDs.
        requires_any: If True, find instances with any one or more workload or
            component IDs passed to `requires`.
        version: A version range for instances to find. Example: '[15.0,16.0)'
            will find versions 15.*.
        latest: If True, returns only the newest version and last installed.
        legacy: If True, also searches Visual Studio 2015 and older products.
            Information is limited. This option cannot be used with either
            `products` or `requires`.
        path: Gets the instance for the given file path. Not compatible with any
            other selection option.

    Output Options:
        sort: If True, sorts the instances from newest version and last installed
            to oldest. When used with `find`, first instances are sorted, then
            files are sorted lexigraphically.
        prop: The name of a property to return instead of the full installation
            details. Use delimiters '.', '/', or '_' to separate object and
            property names. Example: 'properties.nickname' will return the
            'nickname' property under 'properties'.
        find: Returns the file paths matching this glob pattern under the
            installation path. The following patterns are supported:
            ?  Matches any one character except "\\"
            *  Matches zero or more characters except "\\"
            ** Searches the current directory and subdirectories for the
               remaining search pattern.
    """
    args = []

    if find:
        args.append('-find')
        args.append(find)

    if find_all:
        args.append('-all')

    if latest:
        args.append('-latest')

    if legacy:
        args.append('-legacy')

    if path:
        args.append('-path')
        args.append(path)

    if prerelease:
        args.append('-prerelease')

    if products:
        args.append('-products')
        _extend_or_append(args, products)

    if prop:
        args.append('-property')
        args.append(prop)

    if requires:
        args.append('-requires')
        _extend_or_append(args, requires)

    if requires_any:
        args.append('-requiresAny')

    if sort:
        args.append('-sort')

    if version:
        args.append('-version')
        args.append(version)

    return execute(args)


def find_first(**kwargs):
    """
    Call vswhere and returns only the first result, or None if there are no results.

    See find() for keyword arguments.
    """
    return next(iter(find(**kwargs)), None)


def get_latest(legacy=None, **kwargs):
    """
    Get the information for the latest installed version of Visual Studio.

    Also supports the same selection options as find(), for example to select
    different products. If the `legacy` argument is not set, it defaults to
    `True` unless either `products` or `requires` arguments are set.
    """
    legacy = _get_legacy_arg(legacy, **kwargs)
    return find_first(latest=True, legacy=legacy, **kwargs)


def get_latest_path(legacy=None, **kwargs):
    """
    Get the file path to the latest installed version of Visual Studio.

    Returns None if no installations could be found.

    Also supports the same selection options as find(), for example to select
    different products. If the `legacy` argument is not set, it defaults to
    `True` unless either `products` or `requires` arguments are set.
    """
    legacy = _get_legacy_arg(legacy, **kwargs)
    return find_first(latest=True, legacy=legacy, prop='installationPath', **kwargs)


def get_latest_version(legacy=None, **kwargs):
    """
    Get the version string of the latest installed version of Visual Studio.

    For Visual Studio 2017 and newer, this is the full version number, for
    example: '15.8.28010.2003'.

    For Visual Studio 2015 and older, this only contains the major version, with
    the minor version set to 0, for example: '14.0'.

    Returns None if no installations could be found.

    Also supports the same selection options as find(), for example to select
    different products. If the `legacy` argument is not set, it defaults to
    `True` unless either `products` or `requires` arguments are set.
    """
    legacy = _get_legacy_arg(legacy, **kwargs)
    return find_first(latest=True, legacy=legacy, prop='installationVersion', **kwargs)

def get_latest_major_version(**kwargs):
    """
    Get the major version of the latest installed version of Visual Studio as an int.

    Returns 0 if no installations could be found.

    Also supports the same selection options as find(), for example to select
    different products. If the `legacy` argument is not set, it defaults to
    `True` unless either `products` or `requires` arguments are set.
    """
    return int(next(iter(get_latest_version(**kwargs).split('.')), '0'))


def get_vswhere_path():
    """
    Get the path to vshwere.exe.

    If vswhere is not already installed as part of Visual Studio, and no
    alternate path is given using `set_vswhere_path()`, the latest release will
    be downloaded and stored alongside this script.
    """
    if alternate_path and os.path.exists(alternate_path):
        return alternate_path

    if DEFAULT_PATH and os.path.exists(DEFAULT_PATH):
        return DEFAULT_PATH

    if os.path.exists(DOWNLOAD_PATH):
        return DOWNLOAD_PATH

    _download_vswhere()
    return DOWNLOAD_PATH


def set_vswhere_path(path):
    """
    Set the path to vswhere.exe.

    If this is set, it overrides any version installed as part of Visual Studio.
    """
    global alternate_path
    alternate_path = path


def set_download_mirror(url):
    """
    Set a URL from which vswhere.exe should be downloaded if it is not already
    installed as part of Visual Studio and no alternate path is given using
    `set_vswhere_path()`.
    """
    global download_mirror_url
    download_mirror_url = url


def _extend_or_append(lst, value):
    if isinstance(value, str):
        lst.append(value)
    else:
        lst.extend(value)


def _get_legacy_arg(legacy, **kwargs):
    if legacy is None:
        return 'products' not in kwargs and 'requires' not in kwargs
    else:
        return legacy


def _download_vswhere():
    """
    Download vswhere to DOWNLOAD_PATH.
    """
    print('downloading from', _get_latest_release_url())
    try:
        from urllib.request import urlopen
        with urlopen(_get_latest_release_url()) as response, open(DOWNLOAD_PATH, 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
    except ImportError:
        # Python 2
        import urllib
        urllib.urlretrieve(_get_latest_release_url(), DOWNLOAD_PATH)


def _get_latest_release_url():
    """
    The the URL of the latest release of vswhere.
    """
    if download_mirror_url:
        return download_mirror_url

    try:
        from urllib.request import urlopen
        with urlopen(LATEST_RELEASE_ENDPOINT) as response:
            release = json.loads(response.read())
    except ImportError:
        # Python 2
        import urllib2
        response = urllib2.urlopen(LATEST_RELEASE_ENDPOINT)
        release = json.loads(response.read(), encoding=response.headers.getparam('charset') or 'utf-8')

    for asset in release['assets']:
        if asset['name'] == 'vswhere.exe':
            return asset['browser_download_url']

    raise Exception('Could not locate the latest release of vswhere.')