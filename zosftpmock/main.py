#!/usr/bin/env python3.5
import os.path
from datetime import date

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.filesystems import AbstractedFS


proto_cmds = {
    'ABOR': dict(
        perm=None, auth=True, arg=False,
        help='Syntax: ABOR (abort transfer).'),
    'ALLO': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: ALLO <SP> bytes (noop; allocate storage).'),
    'APPE': dict(
        perm='a', auth=True, arg=True,
        help='Syntax: APPE <SP> file-name (append data to file).'),
    'CDUP': dict(
        perm='e', auth=True, arg=False,
        help='Syntax: CDUP (go to parent directory).'),
    'CWD': dict(
        perm='e', auth=True, arg=None,
        help='Syntax: CWD [<SP> dir-name] (change working directory).'),
    'DELE': dict(
        perm='d', auth=True, arg=True,
        help='Syntax: DELE <SP> file-name (delete file).'),
    'EPRT': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: EPRT <SP> |proto|ip|port| (extended active mode).'),
    'EPSV': dict(
        perm=None, auth=True, arg=None,
        help='Syntax: EPSV [<SP> proto/"ALL"] (extended passive mode).'),
    'FEAT': dict(
        perm=None, auth=False, arg=False,
        help='Syntax: FEAT (list all new features supported).'),
    'HELP': dict(
        perm=None, auth=False, arg=None,
        help='Syntax: HELP [<SP> cmd] (show help).'),
    'LIST': dict(
        perm='l', auth=True, arg=None,
        help='Syntax: LIST [<SP> path] (list files).'),
    'MODE': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: MODE <SP> mode (noop; set data transfer mode).'),
    'MKD': dict(
        perm='m', auth=True, arg=True,
        help='Syntax: MKD <SP> path (create directory).'),
    'NLST': dict(
        perm='l', auth=True, arg=None,
        help='Syntax: NLST [<SP> path] (list path in a compact form).'),
    'NOOP': dict(
        perm=None, auth=False, arg=False,
        help='Syntax: NOOP (just do nothing).'),
    'OPTS': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: OPTS <SP> cmd [<SP> option] (set option for command).'),
    'PASS': dict(
        perm=None, auth=False, arg=None,
        help='Syntax: PASS [<SP> password] (set user password).'),
    'PASV': dict(
        perm=None, auth=True, arg=False,
        help='Syntax: PASV (open passive data connection).'),
    'PORT': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: PORT <sp> h,h,h,h,p,p (open active data connection).'),
    'PWD': dict(
        perm=None, auth=True, arg=False,
        help='Syntax: PWD (get current working directory).'),
    'QUIT': dict(
        perm=None, auth=False, arg=False,
        help='Syntax: QUIT (quit current session).'),
    'REIN': dict(
        perm=None, auth=True, arg=False,
        help='Syntax: REIN (flush account).'),
    'REST': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: REST <SP> offset (set file offset).'),
    'RETR': dict(
        perm='r', auth=True, arg=True,
        help='Syntax: RETR <SP> file-name (retrieve a file).'),
    'RMD': dict(
        perm='d', auth=True, arg=True,
        help='Syntax: RMD <SP> dir-name (remove directory).'),
    'RNFR': dict(
        perm='f', auth=True, arg=True,
        help='Syntax: RNFR <SP> file-name (rename (source name)).'),
    'RNTO': dict(
        perm='f', auth=True, arg=True,
        help='Syntax: RNTO <SP> file-name (rename (destination name)).'),
    'SITE': dict(
        perm=None, auth=False, arg=True,
        help='Syntax: SITE <SP> site-command (execute SITE command).'),
    'SITE HELP': dict(
        perm=None, auth=False, arg=None,
        help='Syntax: SITE HELP [<SP> cmd] (show SITE command help).'),
    'SITE CHMOD': dict(
        perm='M', auth=True, arg=True,
        help='Syntax: SITE CHMOD <SP> mode path (change file mode).'),
    'SIZE': dict(
        perm='l', auth=True, arg=True,
        help='Syntax: SIZE <SP> file-name (get file size).'),
    'STAT': dict(
        perm='l', auth=False, arg=None,
        help='Syntax: STAT [<SP> path name] (server stats [list files]).'),
    'STOR': dict(
        perm='w', auth=True, arg=True,
        help='Syntax: STOR <SP> file-name (store a file).'),
    'STOU': dict(
        perm='w', auth=True, arg=None,
        help='Syntax: STOU [<SP> name] (store a file with a unique name).'),
    'STRU': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: STRU <SP> type (noop; set file structure).'),
    'SYST': dict(
        perm=None, auth=False, arg=False,
        help='Syntax: SYST (get operating system type).'),
    'TYPE': dict(
        perm=None, auth=True, arg=True,
        help='Syntax: TYPE <SP> [A | I] (set transfer type).'),
    'USER': dict(
        perm=None, auth=False, arg=True,
        help='Syntax: USER <SP> user-name (set username).'),
    'XCUP': dict(
        perm='e', auth=True, arg=False,
        help='Syntax: XCUP (obsolete; go to parent directory).'),
    'XCWD': dict(
        perm='e', auth=True, arg=None,
        help='Syntax: XCWD [<SP> dir-name] (obsolete; change directory).'),
    'XMKD': dict(
        perm='m', auth=True, arg=True,
        help='Syntax: XMKD <SP> dir-name (obsolete; create directory).'),
    'XPWD': dict(
        perm=None, auth=True, arg=False,
        help='Syntax: XPWD (obsolete; get current dir).'),
    'XRMD': dict(
        perm='d', auth=True, arg=True,
        help='Syntax: XRMD <SP> dir-name (obsolete; remove directory).'),
}


class ZOSFS(AbstractedFS):
    def format_list_in_root(self, basedir, listing):
        # Send head
        head = "Volume Unit Referred Ext Used Recfm Lrecl BlkSz Dsorg Dsname\r\n"  # noqa
        yield head.encode('utf8', self.cmd_channel.unicode_errors)

        # Send list
        for basename in listing:
            filepath = os.path.join(basedir, basename)
            isdir = os.path.isdir(filepath)
            st = self.lstat(filepath)

            volume = "APCSPL"
            unit = "3380D"
            referred = date.fromtimestamp(st.st_mtime).strftime('%Y/%m/%d')
            ext = "4"
            used = st.st_nlink if st.st_nlink else 1
            recfm = 'F'
            lrecl = str(st.st_size)
            blksz = lrecl
            sorg = "PO" if isdir else "PS"
            dsname = basename

            line = '{} {} {} {} {} {} {} {} {} {}\r\n'.format(
                volume, unit, referred, ext, used, recfm,
                lrecl, blksz, sorg, dsname)
            yield line.encode('utf8', self.cmd_channel.unicode_errors)

    def format_list_in_pds(self, zroot, pds, listing):
        # Send head
        head = "Name VV.MM Created Changed Size Init Mod Id\r\n"
        head = "Volume Unit Referred Ext Used Recfm Lrecl BlkSz Dsorg Dsname\r\n"  # noqa
        yield head.encode('utf8', self.cmd_channel.unicode_errors)

        # Send list
        for basename in listing:
            filepath = os.path.join(self._root, zroot, pds, basename)
            st = self.lstat(filepath)

            name = basename
            vvmm = '00.00'
            created = date.fromtimestamp(st.st_ctime).strftime('%Y/%m/%d')
            changed = date.fromtimestamp(st.st_mtime).strftime('%Y/%m/%d %H:%M')  # noqa
            size = str(st.st_size)
            init = size
            mod = '0'
            zid = zroot

            line = '{} {} {} {} {} {} {} {}\r\n'.format(
                name, vvmm, created, changed, size, init, mod, zid)

            # GDG 
            volume = "H19761"
            unit = "Tape"
            referred = ""
            ext = ""
            used = ""
            recfm = ''
            lrecl = ''
            blksz = ""
            sorg = ""
            dsname = basename
            line = '{} {} {} {} {} {} {} {} {} {}\r\n'.format(
                volume, unit, referred, ext, used, recfm,
                lrecl, blksz, sorg, dsname)
            yield line.encode('utf8', self.cmd_channel.unicode_errors)

    def format_list(self, basedir, listing, ignore_err=True):
        after_root = basedir[len(self._root) + 1:]
        l = after_root.split('/')
        if len(l) == 1:
            return self.format_list_in_root(basedir, listing)
        else:
            return self.format_list_in_pds(l[0], l[1], listing)


class ZOSHandler(FTPHandler):
    def zos_to_unix(self, path):
        # remove '
        path = path.replace("'", "")

        # if parenthesis, add /
        if '(' in path and ')' in path:
            path = path.replace('(', '/')
            path = path.replace(')', '')

        return path

    def zos_absolute(self, path):
        base = self.fs._root + "/"
        zos_path = path[path.find("'"):]
        unix_path = self.zos_to_unix(zos_path)
        unix_path = unix_path.replace('.', '/', 1)
        path = base + unix_path
        return path

    def ftp_LIST(self, path):
        if "'" in path:
            path = self.zos_absolute(path)
        return super().ftp_LIST(path)

    def ftp_CWD(self, path):
        path = self.zos_absolute(path)
        return super().ftp_CWD(path)

    def ftp_PWD(self, line):
        cwd = self.fs.cwd
        # remove first /
        cwd = cwd[1:]
        # replace / by .
        cwd = cwd.replace("/", ".")
        # add quotes
        cwd = "'" + cwd + "'"
        self.respond('257 "%s" is the current directory.' % cwd)

    def ftp_RETR(self, path):
        #path = self.zos_absolute(path)
        print("RETR "+path)
        return super().ftp_RETR(path)

    def ftp_STOR(self, path, mode='w'):
        path = self.zos_absolute(path)
        return super().ftp_STOR(path, mode)

    def ftp_TYPE(self, line):
        return super().ftp_TYPE(line)


def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user('test', 'test', '.', perm='elradfmwM')

    # Instantiate FTP handler class
    handler = ZOSHandler
    handler.authorizer = authorizer
    handler.banner = "z/OS FTP Emulator by realitix"
    handler.abstracted_fs = ZOSFS
    handler.proto_cmds = proto_cmds

    address = ('', 2121)
    server = FTPServer(address, handler)

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':
    main()
