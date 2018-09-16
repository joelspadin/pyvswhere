# Python vswhere

This module provides an interface to Microsoft's Visual Studio locator tool,
[vswhere](https://github.com/Microsoft/vswhere).

If Visual Studio 15.2 or later has been installed, this will use the vswhere
binary installed with Visual Studio. Otherwise, it will download the latest
release of vswhere the first time a function is called.

# Usage

`find` and `find_first` are the most generic functions. They support most of the
[command line options](https://github.com/Microsoft/vswhere/blob/master/src/vswhere.lib/vswhere.lib.rc#L72)
to vswhere. `find` returns a list of installed copies of Visual Studio matching
the given options, and `find_first` returns only the first result.

If you are only interested in the latest version of Visual Studio, use
`get_latest`. To get just the installation path, use `get_latest_path`. To get
just the version number, use `get_latest_version` or `get_latest_major_version`.

If you want to use your own version of vswhere.exe instead of the one installed
with Visual Studio, use `set_vswhere_path` to provide its location.

If you want to use a mirror instead of GitHub to download vswhere.exe, for
example when on an intranet that does not have access to GitHub, use
`set_download_mirror` and provide the URL of the mirror.

## Examples

```Python
>>> import pprint, vswhere
>>> vswhere.get_latest_path()
'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community'
>>> vswhere.get_latest_version()
'15.8.28010.2003'
>>> vswhere.get_latest_major_version()
15
>>> vswhere.find(legacy=True, prop='installationPath')
['C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community', 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\']
>>> pp = pprint.PrettyPrinter(indent=4, width=200)
>>> pp.pprint(vswhere.find(legacy=True))
[   {   ...
        'description': 'Free, fully-featured IDE for students, open-source and individual developers',
        'displayName': 'Visual Studio Community 2017',
        'enginePath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\resources\\app\\ServiceHub\\Services\\Microsoft.VisualStudio.Setup.Service',
        'installDate': '2018-04-26T04:49:29Z',
        'installationName': 'VisualStudio/15.8.1+28010.2003',
        'installationPath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community',
        'installationVersion': '15.8.28010.2003',
        'instanceId': 'ee7ea828',
        'isPrerelease': False,
        'productId': 'Microsoft.VisualStudio.Product.Community',
        'productPath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community\\Common7\\IDE\\devenv.exe',
        'properties': ...,
        'releaseNotes': 'https://go.microsoft.com/fwlink/?LinkId=660692#15.8.1',
        'thirdPartyNotices': 'https://go.microsoft.com/fwlink/?LinkId=660708',
        'updateDate': '2018-08-19T20:49:30.0058548Z'},
    {'installationPath': 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\', 'installationVersion': '14.0', 'instanceId': 'VisualStudio.14.0'}]
```