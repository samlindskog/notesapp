# i dislike this script strongly
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

parser.add_argument("-u", type=str, help="uuid", dest="uuid")
parser.add_argument("-t", type=str, help="title", dest="title")
parser.add_argument("-f", type=str, help="file path", dest="file_path")
parser.add_argument("-d", action="store_true", help="delete uuid", dest="delete")

args = parser.parse_args()

# including uuid without -d updates stored file and dt only
if not args.delete:
    if not args.uuid and not (args.title and args.file_path):
       raise Exception("adding a new asset requires title and file")
else:
    if not args.uuid:
        raise Exception("deleting an asset requires uuid")

# set extension based on -f file extension
extensionpat = re.compile(r"^.+\.(.+)$")
match = extensionpat.match(args.file_path)
assert isinstance(match, re.Match)
# used in match statements instead of typ for readability
extension = match.group(1)
# set extension typ integer for database
match extension:
    case "pdf":
        typ = 0
    case "md":
        typ = 1
    case _:
        raise ValueError("-f file extension not supported")

# absolute path of file to be added, file name of new file
def ingest_file(path, uuid):
    with open(path, 'rb') as old_file:
        file_bytes = old_file.read()
        # write requested pdf to assetsdir
        match extension:
            case "pdf":
                with open(config.assetsdir / (uuid + ".pdf"), 'wb') as new_file:
                    new_file.write(file_bytes)
                # add new thumbnail
                pi.convert_from_bytes(
                        file_bytes,
                        fmt="jpeg",
                        output_folder=config.assetsdir,
                        output_file=uuid,
                        single_file=True
                        )
            case "md":
                with open(config.assetsdir / (uuid + ".md"), 'wb') as new_file:
                    new_file.write(file_bytes)
                # add new thumbnail

def delete_asset(uuid):
    match extension:
        case "pdf":
            pl.Path.unlink(config.assetsdir / (uuid + ".pdf"))
            pl.Path.unlink(config.assetsdir / (uuid + ".jpg"))
        case "md":
            pl.Path.unlink(config.assetsdir / (uuid + ".md"))

# psycopg will abort transaction if exception is raised in cursor context
with psycopg.connect(conninfo=config._conninfo, row_factory=dict_row) as conn: # type: ignore
    with conn.cursor() as cur:
        if args.delete:
            cur.execute("SELECT * FROM notes.assets WHERE id=%s", [args.uuid])
            recordset = cur.fetchall()
            if recordset == []:
                raise Exception("no such id")
            # delete assets and db entry
            cur.execute("DELETE FROM notes.assets WHERE id=%s", [args.uuid])
            delete_asset(args.uuid)
        else:
            # check if uuid already exists
            cur.execute("SELECT * FROM notes.assets WHERE id=%s", [args.uuid])
            recordset = cur.fetchall()
            if not recordset == []:
                # update timestamp
                cur.execute("UPDATE notes.assets SET dt=current_timestamp(0) WHERE id=%s", [args.uuid])
                # update title
                if args.title:
                    cur.execute("UPDATE notes.assets SET title=%s WHERE id=%s", [args.title, args.uuid])
            else:
                # create new db entry
                cur.execute("INSERT INTO notes.assets (title, typ) VALUES (%s, %s)", [args.title, typ])
            # add asset to assetsdir
            cur.execute("SELECT * FROM notes.assets WHERE title=%s", [args.title])
            recordset = cur.fetchall()
            uuid = str(recordset[0]["id"])
            ingest_file(args.file_path, uuid)
