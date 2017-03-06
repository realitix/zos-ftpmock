# z/OS FTP Emulator

## Why this emulator

You can access z/OS in two ways, the UNIX one and the MVS one. When accessing
z/OS with a FTP client, you will usually see only the UNIX tree folder. But
sometime, you want to access the MVS tree structure, to do so, you have to
use a FTP client that supports z/OS FTP server.

I have done this emulator because I have added z/OS support to NppFTP (a
plugin of Notepad++) but the maintainer couldn't test the patch. With this
emulator, he can test it and improve it.

## How to use it

1. Clone this repository
2. `python3 setup.py install`
3. `cd example`
4. `zosftp`

You have now a FTP server listening on port 2121.

To test it, in your FTP client, use 'TSODIQ1' as base path (with the quote).
