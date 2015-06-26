import os
import uuid
import sqlite3
import os.path

import arrow

from flask import Flask, request, redirect, send_file
from flask_restful import Resource, Api, abort
from flask.ext import shelve

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.realpath('./data/')
app.config['SHELVE_FILENAME'] = os.path.realpath('./data/files.db')

api = Api(app)
shelve.init_app(app)

class FileList(Resource):

    def get(self):
        db = shelve.get_shelve('c')
        return {k: {'name': v['name'],
                    'date': v['date'].isoformat(),
                    'url': api.url_for(File, tag=k, _external=True)}
                for k, v in db.items()}

    def delete(self):
        db = shelve.get_shelve('c')
        for f in db.values():
            try:
                os.remove(f['path'])
            except FileNotFoundError:
                pass
        db.clear()
        return {}


class File(Resource):

    def get(self, tag):
        db = shelve.get_shelve('c')

        try:
            f = db[tag]
        except KeyError:
            abort(404)

        return send_file(f['path'], as_attachment=True, attachment_filename=f['name'])

    def put(self, tag):
        path = "%s/%s" % (app.config['UPLOAD_FOLDER'], uuid.uuid4())

        f = request.files['file']
        f.save(path)

        db = shelve.get_shelve('c')
        db[tag] = {
            'name': f.filename,
            'path': path,
            'date': arrow.now()
            }

        return {}, 201

    def delete(self, tag):
        db = shelve.get_shelve('c')

        try:
            f = db.pop(tag)
        except KeyError:
            abort(404)

        try:
            os.remove(f['path'])
        except FileNotFoundError:
            pass

        return {}, 200

        # TODO: also delete file on FS.

api.add_resource(FileList, '/files/')
api.add_resource(File, '/files/<string:tag>')
