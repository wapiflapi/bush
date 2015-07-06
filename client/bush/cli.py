import os
import sys
import argparse
import datetime
import contextlib

from distutils import util

import arrow
import progressbar

import bush.api
import bush.config

class ShowProgress():

    def __init__(self, total):

        widgets = [
            progressbar.Percentage(),
            ' ', progressbar.Bar(),
            ' ', progressbar.ETA(),
            ' ', progressbar.AdaptiveETA(),
            ' ', progressbar.AdaptiveTransferSpeed(),
            ]

        self.bar = progressbar.ProgressBar(widgets=widgets, maxval=total)
        self.bar.start()

    def __call__(self, update):
        self.bar.update(update)

    def __del__(self):
        self.bar.finish()


class UIAPI(bush.api.BushAPI):

    def confirmation(self, msg, level):
        print(msg, file=sys.stderr)

        try:
            status = util.strtobool(input("Do you want to proceed? (y/N) "))
        except ValueError:
            status = False

        return status

@contextlib.contextmanager
def user_friendly_errors(exceptions=Exception, debug=False):
    try:
        yield
    except KeyboardInterrupt:
        print('interrupted', file=sys.stderr)
    except () if debug else exceptions as e:
        exit(e)


def do_list(api, args):
    files = api.list()
    maxlen = max(len(f.tag) for f in files) if files else 0
    for f in files:
        f.output(align=maxlen, extended=args.exact)


def do_wait(api, args):

    latest = None
    update = arrow.now() - datetime.timedelta(seconds=args.age)

    knowntags = None

    while not latest:
        tags = set()
        for f in api.list():
            if f.date > update and not (latest and latest.date > f.date):
                latest = f
            elif knowntags is not None and f.tag not in knowntags:
                latest = f
            tags.add(f.tag)
        knowntags = tags

    latest.output(extended=args.exact)
    api.download(latest.tag, args.dest, callback=ShowProgress)


def do_upload(api, args):

    if args.tag is not None:
        tag = args.tag
    elif len(args.file) > 1:
        tag = args.file.pop()
        if ((os.path.isfile(tag) or os.path.isdir(tag)) and
            not api.confirmation("Tag is also an existing file: %r." % tag,
                                 level=bush.api.LOW)):
            exit(1)
    else:
        tag = None

    api.upload(args.file, tag=tag, callback=ShowProgress)


def do_download(api, args):
    api.download(args.tag, args.dest, callback=ShowProgress)


def do_delete(api, args):
    api.delete(args.tag)


def do_reset(api, args):
    api.reset()


def do_serve(api, args):
    from bush.server import app
    app.run(host=api.base.hostname, port=api.base.port, debug=args.debug)


def main():

    parser = argparse.ArgumentParser(description="Simplistic file sharing. ",
                                     epilog="Configuration file is searched "
                                     "for in the following locations: %s" %
                                     ", ".join(bush.config.get_configpaths()))
    subs = parser.add_subparsers(dest='action')
    subs.required = True

    sub = subs.add_parser('ls', help="list information about available files")
    sub.set_defaults(callback=do_list)
    sub.add_argument('-x', '--exact', action='store_true',
                     help="show exact dates instead of ages")

    sub = subs.add_parser('wait', help="wait for a new file and download it")
    sub.set_defaults(callback=do_wait)
    sub.add_argument('dest', nargs='?', default='./',
                     help="path where the file should be downloaded")
    sub.add_argument('-a', '--age', default=0, type=int,
                     help="this many seconds old is new")
    sub.add_argument('-x', '--exact', action='store_true',
                     help="show exact dates instead of ages")

    sub = subs.add_parser('up', help="upload new file(s)")
    sub.set_defaults(callback=do_upload)
    sub.add_argument('file', nargs='+', help='path of the file(s) to upload')
    sub.add_argument('tag', nargs="?", default=None,
                     help='the name associated with the file(s) to upload')

    sub = subs.add_parser('dl', help="download a file")
    sub.set_defaults(callback=do_download)
    sub.add_argument('tag',
                     help='the name associated with the file to download')
    sub.add_argument('dest', nargs='?', default='./',
                     help="path where the file should be downloaded")

    sub = subs.add_parser('rm', help="remove an uploaded file")
    sub.set_defaults(callback=do_delete)
    sub.add_argument('tag', help='the name associated with the file to delete')

    sub = subs.add_parser('reset', help="delete all files")
    sub.set_defaults(callback=do_reset)

    sub = subs.add_parser('serve', help="act as a bush server")
    sub.set_defaults(callback=do_serve)

    parser.add_argument('-u', '--url', help="API endpoint")
    parser.add_argument('-U', '--username', help="API username")
    parser.add_argument('-P', '--password', help="API password")
    parser.add_argument("-c", "--config", type=argparse.FileType("r"),
                        help="path overwriting the default configuration file")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="full traceback for exceptions")

    args = parser.parse_args()

    config = bush.config.load_config(args.config)

    if args.callback is do_serve and args.url is None:
        args.url = 'local'

    servers = config.get('servers') or [{}]

    for server in servers:
        if args.url in (server.get('url'), server.get('alias')):
            break
    else:
        server = servers[0] if args.url is None else {}

    url = server.get('url', args.url)

    if url is None:
        exit("No URL specified, check your configuration or specify --url.")

    if not url.endswith('/'):
        print("""\
The API URL doesn't end with a '/', I'll go on and assume you know what
you are doing. But if something fails you might want to try to add one.""",
              file=sys.stderr)

    username = args.username or server.get('username')
    password = args.password or server.get('password')
    api = UIAPI(url, username=username, password=password)

    with user_friendly_errors(debug=args.debug):
        args.callback(api, args)
