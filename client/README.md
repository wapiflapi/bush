
This is a little tool that tries to solve the problem of sharing files with
people. This has been attempted many times but we don't like synchronization
folders (dropbox & co) or having to connect to a service (ftp, email, gdrive...)

The ones we like most are pastebin like services. You share a link and people
can download when and where they want. But we don't like URLs. You don't want to
be shouting "pastebin.com/raw.php?i= sierra romeo capital alpha foxtrot papa
sierra three capital uniform" through the office. And not everyone is always on
IRC, or is it Slack? or Jabber? Also you can't share stuff other than text.

**The spirit is shouting through the office: "Dude, bush dl stuff."**, then the
other guy types `bush dl stuff` and he'll get whatever file(s) you uploaded by
typing `bush up some_complicated_file_name stuff`. (You don't mind typing all
this because auto-completion.)

More information, in particular about how to setup a server, can be
[here](https://github.com/BestPig/bush/).

## get started

```sh
cd client
python setup.py install
```

Then edit the configuration file (use `bush --help` to get its location) to
setup the URL of your server. Or use `bush --url` to try it without configuring
anything.

Here are some of the commands you can try out when your client is running:

  - **`bush ls`** list all files and tags that are present on the server.
  - **`bush reset`** removes everything from the server. This is important, it
  really does remove everything. The spirit of bush is to share stuff with
  people, **not to store it indefinitely**.

  - **`bush up file1 [file2, ...] some_tag`** uploads files to bush. The tag is
  optional and will be auto-generated if you're uploading a single file.
  - **`bush dl some_tag [destination]`** gets the file(s) associated with a
  tag. Optionally you can specify the destination where the file(s) should be
  saved.

  - **`bush rm some_tag`** removes a tag and the associated file(s) from the server.

  - **`bush wait`** this is a nice helper, it waits until someone uploads a file and
    gets it. This avoids shouting the tag through the office if you know someone
    is going to share something.
