import os
import shutil
from collections import ChainMap

# TODO (b0nd0, 2016-05-11): clear all prints(). Add normal logging.

class InitException(Exception):
    pass


class Dotfiles(object):
    """Dotfiles manager class. """

    def __init__(self, src=None, dst=None, bkp=None):
        """ Init base variables. Find available configs and backups.
        :src: - iterable of dirs with dotfiles.
        :dst: - directory to install files to.
        :bkp: - directory where existing dotfiles whill be placed.
        """
        self.prefix = '.'
        self.src = src
        self.dst = dst
        self.bkp = bkp
        self.init_options()
        self.init_files()


    def init_options(self):
        """ Initialize base parameters. Normalize and validate directories.

        :returns: None
        """

        for dr in (self.src, self.dst, self.bkp):
            if dr is None:
                raise InitException('Some of input parameters absent. Need: \
                        source_dir, destination_dir, backup_dir')

            if not (os.path.isdir(dr)
                        and os.access(dr, os.R_OK|os.W_OK)):
                raise InitException('Have no permissions for %s.' % dr)


    def init_files(self):
        """Read configs from :self.src: and :self.bkp: directory.


        :returns: None
        """
        configs = {}
        backups = {}
        for root, dirs, files in os.walk(self.src):
            for f in files:
                if f.startswith(self.prefix):
                    continue
                configs[f] = os.path.join(root, f)

        for root, dirs, files in os.walk(self.bkp):
            for f in files:
                if f.startswith(self.prefix):
                    continue
                backups[f] = os.path.join(root, f)

        self.files = configs
        self.backups = backups


    def install(self):
        """ install dotfiles to destination dir
        :returns: None
        """
        #print('install running')
        for f in self.files:
            #print('\t for %s:' % f)
            dst_f = os.path.join(self.dst, self.prefix + f)
            backup_f = os.path.join(self.bkp, f)
            #print('\t\th: %s, b: %s' % (dst_f, backup_f))
            if os.path.isfile(dst_f):
                if os.path.isfile(backup_f):
                    print('Error: Backup found %s. Ignoring %s.' % (backup_f, f))
                    continue
                #print('move %s to %s' % (dst_f, backup_f))
                shutil.move(dst_f, backup_f)
            #print('symlink %s to %s' % (self.files[f], dst_f))
            os.symlink(self.files[f], dst_f)


    def remove(self):
        """ restore original configs from backup

        :returns: None
        """
        # remove files for which we have backups.
        for fname, fpath in self.backups.items():
            home_f = os.path.join(self.dst, self.prefix + fname)
            backup_f = os.path.join(self.bkp, fname)
            if os.path.lexists(home_f):
                if os.path.islink(home_f):
                    os.unlink(home_f)
                else:
                    print('Error: %s is not part of this installation. Ignoring %s.' % (home_f, fname))
            shutil.move(backup_f, home_f)

        # remove symlinks to our :src:, even if there are no backup.
        no_backups = set(self.files.keys()) - set(self.backups.keys())
        for fname in no_backups:
            home_f = os.path.join(self.dst, self.prefix + fname)

            if os.path.islink(home_f):
                os.unlink(home_f)
