import pdb
import sys
import pathlib as pl
import argparse
import psycopg
import pdf2image as pi
from psycopg.rows import dict_row

# for config import
parentdir = pl.PosixPath(__file__).parent.parent
sys.path.append(str(parentdir))

import config

parser = argparse.ArgumentParser(
        prog="notesappcli",
        description="update or add pdf to notesapp database"
        )

parser.add_argument("-t", type=str, required=True, help="title")
parser.add_argument("-f", type=str, required=True, help="file path")
parser.add_argument("-d", action="store_true", help="delete title")

args = parser.parse_args()

title = args.t
file_path = args.f
delete = args.d

if not (title or file_path):
    raise Exception("Must include title idiot")

# absolute path of file to be added, file name of new file
def ingest_file(path, file_name):
    with open(path, 'rb') as old_file:
        file_bytes = old_file.read()
        # write requested pdf to assetsdir
        with open(config.assetsdir / (file_name + ".pdf"), 'wb') as new_file:
            new_file.write(file_bytes)
        # add new thumbnail
        pi.convert_from_bytes(
                file_bytes,
                fmt="jpeg",
                output_folder=config.assetsdir,
                output_file=file_name,
                single_file=True
                )

def delete_assets(title):
    pl.Path.unlink(config.assetsdir / (title + ".pdf"))
    pl.Path.unlink(config.assetsdir / (title + ".jpg"))

with psycopg.connect(conninfo=config._conninfo, row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        if delete:
            cur.execute("SELECT * FROM notes.assets WHERE title=%s", [title])
            recordset = cur.fetchall()
            if recordset == []:
                raise Exception("no such title")
            uuid = str(recordset[0]["id"])
            # delete assets and db entry
            delete_assets(uuid)
            cur.execute("DELETE FROM notes.assets WHERE title=%s", [title])
        else:
            # check if title already exists
            cur.execute("SELECT * FROM notes.assets WHERE title=%s", [title])
            recordset = cur.fetchall()
            if not recordset == []:
                # update timestamp
                cur.execute("UPDATE notes.assets SET dt=current_timestamp(0) WHERE title=%s", [title])
            else:
                # create new db entry
                cur.execute("INSERT INTO notes.assets (title) VALUES (%s)", [title])
            # add assets to assetsdir
            cur.execute("SELECT * FROM notes.assets WHERE title=%s", [title])
            recordset = cur.fetchall()
            uuid = str(recordset[0]["id"])
            ingest_file(file_path, uuid)
