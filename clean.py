import io, os, sys
import hashlib, binascii
import time
import sqlite3
import signal

import utils

db = 'walk.db'


def find_for_deletion(db):

    """
        Marks files for deletion. Files are not deleted for the moment.

        A file is marked for deletion if:

            - A master file exists
            - Is not in a directory marked as protected ou master

        Args:
            db (text): Name of the file used for storing sqlite3 database

        Returns:
            nb_rec (int): Number of files to delete

    """

    cnx = sqlite3.connect(db)

    # Selecting files having duplicates

    res = cnx.execute("SELECT * FROM filelist WHERE has_duplicate='1' ORDER BY hash, master DESC, original_path;")

    # Some init

    current_hash = None
    to_be_deleted = False
    has_master = False

    # Nb of records to delete

    nb_rec = 0

    # Now fetching the DB

    for row in res:

        nb_rec = nb_rec + 1

        # Get info for the file (record)

        fid, hash, _, path, name, orig_path, _, _, _, _, master, has_dup, _, _ = row

        # In case of a new hash, we reset the flags

        if current_hash != hash:

            # New hash, reset all flags
            current_hash = hash 
            has_master = False
            to_be_deleted = False
            print('-'*50)
        
        # We've found a file in a master directory

        if master:
            has_master = True
            to_be_deleted = False
        
        # If the file (record) has a master, and is not in a protected/master directory, we can delete it

        if has_master and not(master):
            to_be_deleted = True
            cnx.execute("UPDATE filelist SET marked_for_deletion = '1' WHERE fid=?", (fid, ))

        # Commit, sometimes

        if (nb_rec % 100) == 0:
            utils.checkpoint_db(cnx, "mark_for_deletion", current_hash, commit = True)

        print(nb_rec, fid, hash, master, has_dup, to_be_deleted, path, name, orig_path)

    # Final commit
    utils.checkpoint_db(cnx, "mark_for_deletion", "all", commit = True)

    # Ends connection
    cnx.close()

    # Returns number of records to delete
    return nb_rec


                
# -------------------------------------------
#  main call
# -------------------------------------------

if __name__ == '__main__':
    find_for_deletion(db)
    