import setuptools
import vswhere

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='vswhere',
    version=vswhere.__version__,
    description='Interface to Microsoft\'s Visual Studio locator tool, vswhere',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ChaosinaCan/pyvswhere',
    author='Joel Spadin',
    author_email='joelspadin@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)',
    ],
    zip_safe=False)