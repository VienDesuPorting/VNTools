#!/usr/bin/env python3

from __future__ import print_function

import sys
import os
import codecs
import pickle
import errno
import random
try:
    import pickle5 as pickle
except:
    import pickle
    if sys.version_info < (3, 8):
        print('warning: pickle5 module could not be loaded and Python version is < 3.8,', file=sys.stderr)
        print('         newer Ren\'Py games may fail to unpack!', file=sys.stderr)
        if sys.version_info >= (3, 5):
            print('         if this occurs, fix it by installing pickle5:', file=sys.stderr)
            print('             {} -m pip install pickle5'.format(sys.executable), file=sys.stderr)
        else:
            print('         if this occurs, please upgrade to a newer Python (>= 3.5).', file=sys.stderr)
        print(file=sys.stderr)


if sys.version_info[0] >= 3:
    def _unicode(text):
        return text

    def _printable(text):
        return text

    def _unmangle(data):
        if type(data) == bytes:
            return data
        else:
            return data.encode('latin1')

    def _unpickle(data):
        # Specify latin1 encoding to prevent raw byte values from causing an ASCII decode error.
        return pickle.loads(data, encoding='latin1')
elif sys.version_info[0] == 2:
    def _unicode(text):
        if isinstance(text, unicode):
            return text
        return text.decode('utf-8')

    def _printable(text):
        return text.encode('utf-8')

    def _unmangle(data):
        return data

    def _unpickle(data):
        return pickle.loads(data)

class RenPyArchive:
    file = None
    handle = None

    files = {}
    indexes = {}

    version = None
    padlength = 0
    key = None
    verbose = False

    RPA2_MAGIC = 'RPA-2.0 '
    RPA3_MAGIC = 'RPA-3.0 '
    RPA3_2_MAGIC = 'RPA-3.2 '

    # For backward compatibility, otherwise Python3-packed archives won't be read by Python2
    PICKLE_PROTOCOL = 2

    def __init__(self, file=None, version=3, padlength=0, key=0xDEADBEEF, verbose=False):
        self.padlength = padlength
        self.key = key
        self.verbose = verbose

        if file is not None:
            self.load(file)
        else:
            self.version = version

    def __del__(self):
        if self.handle is not None:
            self.handle.close()

    # Determine archive version.
    def get_version(self):
        self.handle.seek(0)
        magic = self.handle.readline().decode('utf-8')

        if magic.startswith(self.RPA3_2_MAGIC):
            return 3.2
        elif magic.startswith(self.RPA3_MAGIC):
            return 3
        elif magic.startswith(self.RPA2_MAGIC):
            return 2
        elif self.file.endswith('.rpi'):
            return 1

        raise ValueError('the given file is not a valid Ren\'Py archive, or an unsupported version')

    # Extract file indexes from opened archive.
    def extract_indexes(self):
        self.handle.seek(0)
        indexes = None

        if self.version in [2, 3, 3.2]:
            # Fetch metadata.
            metadata = self.handle.readline()
            vals = metadata.split()
            offset = int(vals[1], 16)
            if self.version == 3:
                self.key = 0
                for subkey in vals[2:]:
                    self.key ^= int(subkey, 16)
            elif self.version == 3.2:
                self.key = 0
                for subkey in vals[3:]:
                    self.key ^= int(subkey, 16)

            # Load in indexes.
            self.handle.seek(offset)
            contents = codecs.decode(self.handle.read(), 'zlib')
            indexes = _unpickle(contents)

            # Deobfuscate indexes.
            if self.version in [3, 3.2]:
                obfuscated_indexes = indexes
                indexes = {}
                for i in obfuscated_indexes.keys():
                    if len(obfuscated_indexes[i][0]) == 2:
                        indexes[i] = [ (offset ^ self.key, length ^ self.key) for offset, length in obfuscated_indexes[i] ]
                    else:
                        indexes[i] = [ (offset ^ self.key, length ^ self.key, prefix) for offset, length, prefix in obfuscated_indexes[i] ]
        else:
            indexes = pickle.loads(codecs.decode(self.handle.read(), 'zlib'))

        return indexes

    # Generate pseudorandom padding (for whatever reason).
    def generate_padding(self):
        length = random.randint(1, self.padlength)

        padding = ''
        while length > 0:
            padding += chr(random.randint(1, 255))
            length -= 1

        return bytes(padding, 'utf-8')

    # Converts a filename to archive format.
    def convert_filename(self, filename):
        (drive, filename) = os.path.splitdrive(os.path.normpath(filename).replace(os.sep, '/'))
        return filename

    # Debug (verbose) messages.
    def verbose_print(self, message):
        if self.verbose:
            print(message)


    # List files in archive and current internal storage.
    def list(self):
        return list(self.indexes.keys()) + list(self.files.keys())

    # Check if a file exists in the archive.
    def has_file(self, filename):
        filename = _unicode(filename)
        return filename in self.indexes.keys() or filename in self.files.keys()

    # Read file from archive or internal storage.
    def read(self, filename):
        filename = self.convert_filename(_unicode(filename))

        # Check if the file exists in our indexes.
        if filename not in self.files and filename not in self.indexes:
            raise IOError(errno.ENOENT, 'the requested file {0} does not exist in the given Ren\'Py archive'.format(
                _printable(filename)))

        # If it's in our opened archive index, and our archive handle isn't valid, something is obviously wrong.
        if filename not in self.files and filename in self.indexes and self.handle is None:
            raise IOError(errno.ENOENT, 'the requested file {0} does not exist in the given Ren\'Py archive'.format(
                _printable(filename)))

        # Check our simplified internal indexes first, in case someone wants to read a file they added before without saving.
        if filename in self.files:
            self.verbose_print('Reading file {0} from internal storage...'.format(_printable(filename)))
            return self.files[filename]
        else:
            # Read offset and length, seek to the offset and read the file contents.
            if len(self.indexes[filename][0]) == 3:
                (offset, length, prefix) = self.indexes[filename][0]
            else:
                (offset, length) = self.indexes[filename][0]
                prefix = ''

            self.verbose_print('Reading file {0} from data file {1}... (offset = {2}, length = {3} bytes)'.format(
                _printable(filename), self.file, offset, length))
            self.handle.seek(offset)
            return _unmangle(prefix) + self.handle.read(length - len(prefix))

    # Modify a file in archive or internal storage.
    def change(self, filename, contents):
        filename = _unicode(filename)
        self.remove(filename)
        self.add(filename, contents)

    # Add a file to the internal storage.
    def add(self, filename, contents):
        filename = self.convert_filename(_unicode(filename))
        if filename in self.files or filename in self.indexes:
            raise ValueError('file {0} already exists in archive'.format(_printable(filename)))
        self.verbose_print('Adding file {0} to archive... (length = {1} bytes)'.format(
            _printable(filename), len(contents)))
        self.files[filename] = contents

    # Remove a file from archive or internal storage.
    def remove(self, filename):
        filename = _unicode(filename)
        if filename in self.files:
            self.verbose_print('Removing file {0} from internal storage...'.format(_printable(filename)))
            del self.files[filename]
        elif filename in self.indexes:
            self.verbose_print('Removing file {0} from archive indexes...'.format(_printable(filename)))
            del self.indexes[filename]
        else:
            raise IOError(errno.ENOENT, 'the requested file {0} does not exist in this archive'.format(_printable(filename)))

    # Load archive.
    def load(self, filename):
        filename = _unicode(filename)

        if self.handle is not None:
            self.handle.close()
        self.file = filename
        self.files = {}
        self.handle = open(self.file, 'rb')
        self.version = self.get_version()
        self.indexes = self.extract_indexes()

    # Save current state into a new file, merging archive and internal storage, rebuilding indexes, and optionally saving in another format version.
    def save(self, filename=None):
        filename = _unicode(filename)

        if filename is None:
            filename = self.file
        if filename is None:
            raise ValueError('no target file found for saving archive')
        if self.version != 2 and self.version != 3:
            raise ValueError('saving is only supported for version 2 and 3 archives')

        self.verbose_print('Rebuilding archive index...')
        # Merge files added or changed in this session.
        files = self.files
        # First, read files from the current archive into our files structure.
        for file in list(self.indexes.keys()):
            content = self.read(file)
            del self.indexes[file]
            files[file] = content

        # Predict header length; we will write it last.
        offset = 0
        if self.version == 3:
            offset = 34
        elif self.version == 2:
            offset = 25
        archive = open(filename, 'wb')
        archive.seek(offset)

        # Build new indexes while writing files to the archive.
        indexes = {}
        self.verbose_print('Writing files to archive file...')
        for file, content in files.items():
            # Generate random padding if needed.
            if self.padlength > 0:
                padding = self.generate_padding()
                archive.write(padding)
                offset += len(padding)

            archive.write(content)
            # Update index.
            if self.version == 3:
                indexes[file] = [ (offset ^ self.key, len(content) ^ self.key) ]
            elif self.version == 2:
                indexes[file] = [ (offset, len(content)) ]
            offset += len(content)

        # Write the indexes.
        self.verbose_print('Writing archive index to archive file...')
        archive.write(codecs.encode(pickle.dumps(indexes, self.PICKLE_PROTOCOL), 'zlib'))
        # Now write the header.
        self.verbose_print('Writing header to archive file... (version = RPAv{0})'.format(self.version))
        archive.seek(0)
        if self.version == 3:
            archive.write(codecs.encode('{}{:016x} {:08x}\n'.format(self.RPA3_MAGIC, offset, self.key)))
        else:
            archive.write(codecs.encode('{}{:016x}\n'.format(self.RPA2_MAGIC, offset)))
        archive.close()

        # Reload the file in our internal database.
        self.load(filename)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='A tool for working with Ren\'Py archive files.',
        epilog='The FILE argument can optionally be in ARCHIVE=REAL format, mapping a file in the archive filesystem to a file on your system. For example: rpatool -x test.rpa script.rpyc=/home/foo/test.rpyc',
        add_help=False)

    parser.add_argument('archive', metavar='ARCHIVE', nargs='?', help='The Ren\'Py archive file to operate on.')
    parser.add_argument('files', metavar='FILE', nargs='*', action='append', help='Zero or more files to operate on.')

    parser.add_argument('-l', '--list', action='store_true', help='List files in archive ARCHIVE.')
    parser.add_argument('-x', '--extract', action='store_true', help='Extract FILEs from ARCHIVE.')
    parser.add_argument('-c', '--create', action='store_true', help='Create ARCHIVE from FILEs.')
    parser.add_argument('-d', '--delete', action='store_true', help='Delete FILEs from ARCHIVE.')
    parser.add_argument('-a', '--append', action='store_true', help='Append FILEs to ARCHIVE.')

    parser.add_argument('-2', '--two', action='store_true', help='Use the RPAv2 format for creating/appending archives.')
    parser.add_argument('-3', '--three', action='store_true', help='Use the RPAv3 format for creating/appending archives (default).')

    parser.add_argument('-k', '--key', metavar='KEY', help='The obfuscation key used for creating RPAv3 archives, in hexadecimal (default: 0xDEADBEEF).')
    parser.add_argument('-p', '--padding', metavar='COUNT', help='The maximum number of padding bytes to add between files (default: 0).')
    parser.add_argument('-o', '--outfile', help='An alternative output archive file when appending or deleting from archives, or output directory when extracting.')

    # Add new flag for extracting all archives in the current directory.
    parser.add_argument('--all', action='store_true', help='If specified, extracts all .rpa archives in the current directory.')

    parser.add_argument('-h', '--help', action='help', help='Print this help message and exit.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed messages during operations.')
    parser.add_argument('-V', '--version', action='version', version='rpatool v0.8', help='Show version information.')
    arguments = parser.parse_args()

    # Determine RPA version.
    if arguments.two:
        version = 2
    else:
        version = 3

    # Determine RPAv3 key.
    if hasattr(arguments, 'key') and arguments.key is not None:
        key = int(arguments.key, 16)
    else:
        key = 0xDEADBEEF

    # Determine padding bytes.
    if hasattr(arguments, 'padding') and arguments.padding is not None:
        padding = int(arguments.padding)
    else:
        padding = 0

    # If the --all flag is specified, ignore the ARCHIVE argument and process all .rpa files in the current directory.
    if arguments.all:
        archive_files = [f for f in os.listdir('.') if f.lower().endswith('.rpa')]
        if not archive_files:
            print('No .rpa archives found in the current directory.', file=sys.stderr)
            sys.exit(0)
        for archive_filename in archive_files:
            print("Processing archive: {}".format(archive_filename))
            try:
                current_archive = RenPyArchive(archive_filename, padlength=padding, key=key, version=version, verbose=arguments.verbose)
            except IOError as e:
                print('Failed to open archive {}: {}'.format(archive_filename, e), file=sys.stderr)
                continue

            # Determine the extraction directory.
            # If --outfile is provided, use it; otherwise, extract to the current directory directly.
            if arguments.outfile:
                outfolder = _unicode(arguments.outfile)
            else:
                outfolder = "."

            if not os.path.exists(outfolder):
                os.makedirs(outfolder)

            # Extract all files from the archive.
            for filename in current_archive.list():
                if filename.find('=') != -1:
                    (outfile, filename) = filename.split('=', 2)
                else:
                    outfile = filename
                try:
                    contents = current_archive.read(filename)
                    destination = os.path.join(outfolder, outfile)
                    destdir = os.path.dirname(destination)
                    if destdir and not os.path.exists(destdir):
                        os.makedirs(destdir)
                    with open(destination, 'wb') as file_out:
                        file_out.write(contents)
                except Exception as e:
                    print('Failed to extract file {} from {}: {}'.format(filename, archive_filename, e), file=sys.stderr)
        sys.exit(0)

    # Determine input archive/output file.
    if arguments.create:
        archive = None
        output = _unicode(arguments.archive)
    else:
        archive = _unicode(arguments.archive) if arguments.archive is not None else None
        if hasattr(arguments, 'outfile') and arguments.outfile is not None:
            output = _unicode(arguments.outfile)
        else:
            if arguments.extract:
                output = '.'
            else:
                output = _unicode(arguments.archive) if arguments.archive is not None else ''

    # Normalize file arguments.
    if len(arguments.files) > 0 and isinstance(arguments.files[0], list):
        arguments.files = arguments.files[0]

    try:
        if archive is None:
            raise ValueError("No input archive specified.")
        archive = RenPyArchive(archive, padlength=padding, key=key, version=version, verbose=arguments.verbose)
    except Exception as e:
        print('Failed to open archive {} for reading: {}'.format(archive, e), file=sys.stderr)
        sys.exit(1)

    if arguments.create or arguments.append:
        def add_file(filename):
            if filename.find('=') != -1:
                (outfile, filename) = filename.split('=', 2)
            else:
                outfile = filename

            if os.path.isdir(filename):
                for file in os.listdir(filename):
                    add_file(outfile + os.sep + file + '=' + filename + os.sep + file)
            else:
                try:
                    with open(filename, 'rb') as file_in:
                        archive.add(outfile, file_in.read())
                except Exception as e:
                    print('Failed to add file {} to archive: {}'.format(filename, e), file=sys.stderr)

        for filename in arguments.files:
            add_file(_unicode(filename))

        archive.version = version
        try:
            archive.save(output)
        except Exception as e:
            print('Failed to save archive: {}'.format(e), file=sys.stderr)
    elif arguments.delete:
        for filename in arguments.files:
            try:
                archive.remove(filename)
            except Exception as e:
                print('Failed to delete file {} from archive: {}'.format(filename, e), file=sys.stderr)
        archive.version = version
        try:
            archive.save(output)
        except Exception as e:
            print('Failed to save archive: {}'.format(e), file=sys.stderr)
    elif arguments.extract:
        # If specific files are provided, extract them; otherwise, extract all files.
        if len(arguments.files) > 0:
            files = arguments.files
        else:
            files = archive.list()

        if not os.path.exists(output):
            os.makedirs(output)

        for filename in files:
            if filename.find('=') != -1:
                (outfile, filename) = filename.split('=', 2)
            else:
                outfile = filename
            try:
                contents = archive.read(filename)
                out_path = os.path.join(output, outfile)
                if os.path.dirname(out_path) and not os.path.exists(os.path.dirname(out_path)):
                    os.makedirs(os.path.dirname(out_path))
                with open(out_path, 'wb') as file_out:
                    file_out.write(contents)
            except Exception as e:
                print('Failed to extract file {} from archive: {}'.format(filename, e), file=sys.stderr)
    elif arguments.list:
        file_list = archive.list()
        file_list.sort()
        for file in file_list:
            print(file)
    else:
        print('No operation specified :(')
        print('Use {} --help for usage details.'.format(sys.argv[0]))
