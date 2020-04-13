import io, os, sys
import hashlib, binascii
import time
import sqlite3
import signal
import shutil

import utils

from colorama import Fore, Back, Style 

#
# Some constants
#

FMT_HIGH = Fore.LIGHTWHITE_EX + Style.DIM
FMT_RESET =  Fore.RESET + Style.RESET_ALL
FMT_STR_MARKED_FILES = FMT_HIGH + "{}" + FMT_RESET \
                        + " files marked for deletion, total size is " + FMT_HIGH + "{}"  + FMT_RESET + "."

FMT_STR_TRASH_PROCESSING = FMT_HIGH + "  {}"+ FMT_RESET + " files trashed, " \
                        + FMT_HIGH + "{}"+ FMT_RESET + " files in error, progression " \
                        + FMT_HIGH + "{:.2f}"+ FMT_RESET + "%, elapsed " \
                        + FMT_HIGH + "{:.2f}" + FMT_RESET + " sec"

FMT_STR_TRASHED_FILES = FMT_HIGH + "{}" + FMT_RESET \
                        + " files put in trash directory (" + FMT_HIGH + "{}" + FMT_RESET \
                        + "), total size is " + FMT_HIGH + "{}"  + FMT_RESET + "." + " "*30
#
# Some init
#

db = utils.db_name
trash = utils.trash_dir

#
# Exit handler (CTRL+C)
#

def exit_handler(signum, frame):

    print()
    print("Normal exit from KeyboardInterrupt (CTRL+C)")
    
    exit(0)


#
# ---
#

def restart_clean(db):

    cnx = sqlite3.connect(db)
    cnx.execute("UPDATE filelist SET trashed=NULL, marked_for_deletion=NULL")
    cnx.commit()
    cnx.close()

#
# ---
#

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
            size(int): Size of files to delete

    """

    cnx = sqlite3.connect(db)

    # Selecting files having duplicates

    res = cnx.execute("SELECT * FROM filelist WHERE has_duplicate='1' ORDER BY hash, master DESC, original_path;")

    # Some init

    current_hash = None
    to_be_deleted = False
    has_master = False

    # Nb of records read
    nb_rec = 0

    # Now fetching the DB

    for row in res:

        nb_rec = nb_rec + 1

        # Get info for the file (record)

        fid, hash, _, path, name, orig_path, _, _, _, _, master, has_dup, _, _, _, _ = row

        # In case of a new hash, we reset the flags

        if current_hash != hash:

            # New hash, reset all flags
            current_hash = hash 
            has_master = False
            to_be_deleted = False
            #print('-'*50)
        
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

        #print(nb_rec, fid, hash, master, has_dup, to_be_deleted, path, name, orig_path)

    # Final commit
    utils.checkpoint_db(cnx, "mark_for_deletion", "all", commit = True)

    # Nb of marked files
    res = cnx.execute("SELECT count(fid) FROM filelist WHERE marked_for_deletion = '1'")
    nb = res.fetchone()[0]

    # Size of marked files
    res = cnx.execute("SELECT SUM(size) FROM filelist WHERE marked_for_deletion = '1'")
    size = res.fetchone()[0]

    # Ends connection
    cnx.close()

    # Returns number of records to delete
    return nb, size


#
# ---
#

def move_files(db):

    """
        Move files marked for deletion in a "trash" directory. 

        Args:
            db (text): Name of the file used for storing sqlite3 database

        Returns:
            nb (int): Number of files moved
            size(int): Size of deleted (trashed) files

    """

    cnx = sqlite3.connect(db)

    # Nb of marked files

    res = cnx.execute("SELECT count(fid) FROM filelist WHERE marked_for_deletion = '1'")
    nb_to_delete = res.fetchone()[0]
    str_fmt = FMT_HIGH + "{}" + FMT_RESET + " files to delete/trash (total)."
    print(str_fmt.format(nb_to_delete))

    # Remaining files to delete

    res = cnx.execute("SELECT count(fid) FROM filelist WHERE (marked_for_deletion = '1') AND (trashed IS NULL);")
    nb_remaining = res.fetchone()[0]
    str_fmt = FMT_HIGH + "{}" + FMT_RESET + " remaining files to delete/trash."
    print(str_fmt.format(nb_remaining))

    # Selecting files to delete

    res = cnx.execute("SELECT * FROM filelist WHERE (marked_for_deletion = '1') AND (trashed IS NULL)")

    # Start time
    chrono = utils.Chrono()
    chrono.start()

    # Big loop

    nb_trash = 0
    nb_fail = 0
    nb = 0
    size_deleted = 0

    for row in res:

        nb = nb + 1

        fid, hash, _, path, name, orig_path, size, _, _, _, master, has_dup, _, _, _, _ = row

        original_file = os.path.join(path, name)
        rel_path = os.path.relpath(path, orig_path)
        copy_file = trash + os.sep + os.path.join(rel_path, name)
        trash_file_path = os.path.dirname(copy_file)

        try:
            if not(os.path.exists(trash_file_path)):
                os.makedirs(trash_file_path)
            # --- shutil.copy2(original_file, copy_file)
            shutil.move(original_file, copy_file)
            nb_trash = nb_trash + 1
            size_deleted = size_deleted + size
            cnx.execute("UPDATE filelist SET trashed='1', delete_error=NULL WHERE fid = ?", (fid, ))

        except OSError as ose:

            nb_fail = nb_fail + 1
            err_num = ose.errno
            cnx.execute("UPDATE filelist SET delete_error=? WHERE fid = ?", (err_num, fid, ))
            #print("({}) {} --> {}".format(err_num, original_file, copy_file))
        
        # Where am I?

        if ((nb % 10) == 0):

            perc = ((nb_trash + nb_fail) / nb_remaining) * 100
            print(FMT_STR_TRASH_PROCESSING.format(nb_trash, nb_fail, perc, chrono.elapsed()), end="\r", flush=True)
            cnx.commit()
            if ((nb % 1000) == 0):
                utils.checkpoint_db(cnx, "filelist_pre_hash", fid, commit = True)

    # Ends connection
    cnx.commit()
    cnx.close()

    return nb_trash, nb_fail, size_deleted





#
# main "procedure"
#
               
def main():

    # 
    # ---> Check for 'restart' argument
    #

    arguments = utils.check_arguments(sys.argv)

    if ("restart" in arguments):
        restart_clean(db)

    #
    # ---> Catch the exit signal to commit the database with last checkpoint
    #

    signal.signal(signal.SIGINT, exit_handler)

    #
    # --> Marking files for deletion
    #

    nb, size = find_for_deletion(db)

    print(FMT_STR_MARKED_FILES.format(nb, utils.humanbytes(size)))

    #
    # --> Deleting/Trashing files
    #

    nb_trash, nb_fail, size = move_files(db)

    print(FMT_STR_TRASHED_FILES.format(nb_trash, trash, utils.humanbytes(size)))

    return



# -------------------------------------------
#  main call
# -------------------------------------------

if __name__ == '__main__':

    main()