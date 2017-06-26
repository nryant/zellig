import os
try:
    from setuptools import setup
except ImportError:
    from distutils import setup
from distutils.command.clean import clean as Clean
import shutil
import subprocess

from Cython.Build import cythonize


############################
# Distribution details
############################
DISTNAME = 'zellig'
PACKAGE_NAME = 'zellig'
DESCRIPTION = ''
MAINTAINER = 'Neville Ryant'
MAINTAINER_EMAIL = 'nryant@gmail.com'
URL = ''
LICENSE = 'Apache 2.0'
DOWNLOAD_URL = ''
VERSION = '0.1'


###########################
# Clean command
###########################
REMOVE_EXTENSIONS = set(['.pyc', '.pyd', '.so', '.dll'])
class CleanCommand(Clean):
    def run(self):
        Clean.run(self)
        if os.path.exists('build'):
            shutil.rmtree('build')
        eggf = '%s.egg-info' % PACKAGE_NAME;
        if os.path.exists(eggf):
            shutil.rmtree(eggf)
        for dirpath, dirnames, fns in os.walk(PACKAGE_NAME):
            for fn in fns:
                ext = os.path.splitext(fn)[1]
                if ext in REMOVE_EXTENSIONS:
                    os.remove(os.path.join(dirpath, fn))


############################
# Setup
############################
def get_ext_modules():
    pyx_fns = []
    for dirpath, dirnames, fns in os.walk(PACKAGE_NAME):
        for fn in fns:
            if fn.endswith('.pyx'):
                pyx_fns.append(os.path.join(dirpath, fn))
    ext_modules = cythonize(pyx_fns)
    for e in ext_modules:
        e.extra_compile_args = ['-O3']
    return ext_modules;


def get_packages():
    packages = []
    for dirpath, dirnames, fns in os.walk(PACKAGE_NAME):
        if os.path.basename(dirpath) == 'tests':
            continue
        if os.path.isfile(os.path.join(dirpath, '__init__.py')):
            package = dirpath.replace(os.path.sep, '.')
            packages.append(package)
    return packages


def get_full_version():
    if os.path.exists('.git'):
        git_revision = get_git_revision()
        full_version = VERSION +  '.dev-' + git_revision[:7]
    else:
        full_version = VERSION
    return full_version


def get_git_revision():
    """Return current revision."""
    def _minimal_ext_cmd(cmd):
        # Construct minimal environment.
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
        stdout = p.communicate()[0]
        return stdout

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    return git_revision


def write_version_py(fn, version):
    with open(fn, 'w') as f:
        f.write("version = '%s'\n" % version)


def setup_package():
    version = get_full_version();
    write_version_py(os.path.join(PACKAGE_NAME, 'version.py'), version)
    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=version,
          download_url=DOWNLOAD_URL,
          packages = get_packages(),
          ext_modules = get_ext_modules(),
          cmdclass={'clean': CleanCommand},
          )


if __name__ == '__main__':
    setup_package()
