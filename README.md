# Python vswhere

This module provides an interface to Microsoft's Visual Studio locator tool,
[vswhere](https://github.com/Microsoft/vswhere).

If Visual Studio 15.2 or later has been installed, this will use the vswhere
binary installed with Visual Studio. Otherwise, it will download the latest
release of vswhere the first time a function is called.

# Usage

`find()` and `find_first()` are the most generic functions. They support most of
the [command line options](https://github.com/Microsoft/vswhere/blob/master/src/vswhere.lib/vswhere.lib.rc#L72)
to vswhere. `find()` returns a list of installed copies of Visual Studio matching
the given options, and `find_first()` returns only the first result.

If you are only interested in the latest version of Visual Studio, use
`get_latest()`. To get just the installation path, use `get_latest_path()`.
To get just the version number, use `get_latest_version()` or `get_latest_major_version()`.
These functions also support the same arguments as `find()`, so you can find
pre-releases or different products such as build tools.

If you want to use your own version of vswhere.exe instead of the one installed
with Visual Studio, use `set_vswhere_path()` to provide its location.

If you want to use a mirror instead of GitHub to download vswhere.exe, for
example when on an intranet that does not have access to GitHub, use
`set_download_mirror()` and provide the URL of the mirror.

## Examples

```Python
>>> import pprint, vswhere
>>> vswhere.get_latest_path()
'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community'
>>> vswhere.get_latest_path(products='Microsoft.VisualStudio.Product.BuildTools')
'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools'
>>> vswhere.get_latest_version()
'16.5.30011.22'
>>> vswhere.get_latest_major_version()
16
>>> vswhere.find(legacy=True, prop='installationPath')
['C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community', 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\']
>>> pp = pprint.PrettyPrinter(indent=4, width=200)
>>> pp.pprint(vswhere.find(legacy=True))
[   {   'catalog': {   'buildBranch': 'd16.5',
                       'buildVersion': '16.5.30011.22',
                       'id': 'VisualStudio/16.5.4+30011.22',
                       'localBuild': 'build-lab',
                       'manifestName': 'VisualStudio',
                       'manifestType': 'installer',
                       'productDisplayVersion': '16.5.4',
                       'productLine': 'Dev16',
                       'productLineVersion': '2019',
                       'productMilestone': 'RTW',
                       'productMilestoneIsPreRelease': 'False',
                       'productName': 'Visual Studio',
                       'productPatchVersion': '4',
                       'productPreReleaseMilestoneSuffix': '1.0',
                       'productSemanticVersion': '16.5.4+30011.22',
                       'requiredEngineVersion': '2.5.2141.57745'},
        'channelId': 'VisualStudio.16.Release',
        'channelUri': 'https://aka.ms/vs/16/release/channel',
        'description': 'Powerful IDE, free for students, open-source contributors, and individuals',
        'displayName': 'Visual Studio Community 2019',
        'enginePath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\resources\\app\\ServiceHub\\Services\\Microsoft.VisualStudio.Setup.Service',
        'installDate': '2019-06-24T05:30:57Z',
        'installationName': 'VisualStudio/16.5.4+30011.22',
        'installationPath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community',
        'installationVersion': '16.5.30011.22',
        'instanceId': '0a09d80d',
        'isComplete': True,
        'isLaunchable': True,
        'isPrerelease': False,
        'isRebootRequired': False,
        'productId': 'Microsoft.VisualStudio.Product.Community',
        'productPath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\Common7\\IDE\\devenv.exe',
        'properties': {   'campaignId': '1263684068.1543796472',
                          'channelManifestId': 'VisualStudio.16.Release/16.5.4+30011.22',
                          'nickname': '',
                          'setupEngineFilePath': 'C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\vs_installershell.exe'},
        'releaseNotes': 'https://go.microsoft.com/fwlink/?LinkId=660893#16.5.4',
        'state': 4294967295,
        'thirdPartyNotices': 'https://go.microsoft.com/fwlink/?LinkId=660909',
        'updateDate': '2020-05-10T17:04:46.9919584Z'},
    {'installationPath': 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\', 'installationVersion': '14.0', 'instanceId': 'VisualStudio.14.0'}]
```