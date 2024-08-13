# this script is utter dogshit
import pdb
import sys
import pathlib as pl
import argparse
import re
import psycopg
import pdf2image as pi
from psycopg.rows import dict_row

# for config import
parentdir = pl.PosixPath(__file__).parent.parent
sys.path.append(str(parentdir))

import config

parser = argparse.ArgumentParser(
        prog="notesappcli",
        description="update/add/delete pdf or markdown from notesapp database"
        )

parser.add_argument("-t", type=str, required=True, help="title")
parser.add_argument("-f", type=str, required=True, help="file path")
parser.add_argument("-d", action="store_true", help="delete title")

args = parser.parse_args()

title = args.t
file_path = args.f
delete = args.d

#set extension based on -f file extension
extensionpat = re.compile(r"^.+\.(.+)$")
match = extensionpat.match(file_path)
assert isinstance(match, re.Match)
extension = match.group(1)

if not (title or file_path):
    raise Exception("Must include title idiot")

# absolute path of file to be added, file name of new file
def ingest_file(path, file_name):
    with open(path, 'rb') as old_file:
        file_bytes = old_file.read()
        # write requested pdf to assetsdir
        match extension:
            case "pdf":
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
            case "md":
                with open(config.assetsdir / (file_name + ".md"), 'wb') as new_file:
                    new_file.write(file_bytes)

def delete_asset(title):
    match extension:
        case "pdf":
            pl.Path.unlink(config.assetsdir / (title + ".pdf"))
            pl.Path.unlink(config.assetsdir / (title + ".jpg"))
        case "md":
            pl.Path.unlink(config.assetsdir / (title + ".md"))

with psycopg.connect(conninfo=config._conninfo, row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        match extension:
            case "pdf":
                table = "assets"
            case "md":
                table = "articles"
            case _:
                raise ValueError
        if delete:
            cur.execute("SELECT * FROM notes.%s WHERE title=%s", [table, title])
            recordset = cur.fetchall()
            if recordset == []:
                raise Exception("no such title")
            uuid = str(recordset[0]["id"])
            # delete assets and db entry
            cur.execute("DELETE FROM notes.%s WHERE title=%s", [table, title])
            delete_asset(uuid)
        else:
            # check if title already exists
            cur.execute("SELECT * FROM notes.%s WHERE title=%s", [table, title])
            recordset = cur.fetchall()
            if not recordset == []:
                # update timestamp
                cur.execute("UPDATE notes.%s SET dt=current_timestamp(0) WHERE title=%s", [table, title])
            else:
                # create new db entry
                cur.execute("INSERT INTO notes.%s (title) VALUES (%s)", [table, title])
            # add asset to assetsdir
            cur.execute("SELECT * FROM notes.%s WHERE title=%s", [table, title])
            recordset = cur.fetchall()
            uuid = str(recordset[0]["id"])
            ingest_file(file_path, uuid)
