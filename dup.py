import io, os, sys
import hashlib, binascii
import time
import sqlite3
import signal

import utils

#
# 1. Discovering files
# 2. Calculating quick hash (on the first 8192 bytes only)
# 3. Calculating complete hash for duplicate candidates
#
# REMEMBER : Trust No-One. Filter and sanitize all fields and entries
#

restart = False
last_step = None
last_id = None


def exit_handler(signum, frame):

    print()
    print("Normal exit from KeyboardInterrupt (CTRL+C)")
    checkpoint_db(cnx, last_step, last_id, commit = True)
    exit(0)

#
#    ====================================================================
#     File hash calculation (single file)
#    ====================================================================
#

def file_hash_calc(filename, algo_name, pre_hash=True):

    """

        Returns the hash of a file. You can choose any hash function that your Phython environment supports.

        It can be used for a full hash computation, or only a pre-hash (much quicker with large files). Pre-hash
        computes the hash only on the first bytes. As we are looking for duplicates, two files with a different
        pre-hash are... different! No need to compute the full hash.

        On the contrary, if the pre-hash is the same for some files, we calculate the full hash (with the entire
        file content) and then we could decide if files are duplicates or not.

        Args:

            filename (text): Absolute path for the file
            algo_name(text): Name of the hash algo we use ("md5", "sha1", and even "crc32")
            pre_hash (boolean): Indicates if we compute a pre-hash or not

        Returns:

            h (text): The hash value (hexa text)
            t (int): execution time (in seconds)

        .. Example:: file_hash_calc("test.txt", "md5")

    """

    # Start time

    chrono = utils.Chrono()
    chrono.start()

    #
    #  ---> Depending on the selected algo, let's calculate the hash
    #

    if (algo_name != "crc32"):

        # Here we have the 'hashlib' hashes
        # ---

        hl = getattr(hashlib, algo_name)()

        #
        # We calculate here only the first bytes for the pre_hash (to speed up the calculation and alors to avoid MemoryError with big files)
        #
        # For complete hash, we need to split the reading.
        # 

        with open(filename,'rb') as f:

            if (pre_hash):

                #
                # Pre-hash => Only on the first bytes
                #

                hl.update(f.read(io.DEFAULT_BUFFER_SIZE))

            else:

                #
                # Complete hash => split the file
                #

                while True:

                    #
                    # We use the read only the size of the block to avoid
                    # heavy ram usage. The file content is buffered.
                    #

                    data = f.read(io.DEFAULT_BUFFER_SIZE)

                    if not data:

                        # if we don't have any more data to read, stop.
                        break

                    # we partially calculate the hash
                    hl.update(data)

        # 
        # We have exceptions: the 'shake' hashes need one argument
        # Else, for all other hashes, we don't need any argument adnd we 
        # can calculate the hash with the hexdigest() method.
        # 

        if (algo_name == "shake_128"):
            h = hl.hexdigest(128)
        elif (algo_name == "shake_256"):
            h = hl.hexdigest(256)
        else:
            h = hl.hexdigest()

    else:

        # 
        # Here we have the 'binascii' hashes (CRC32). Included in an other library.
        # 

        with open(filename,'rb') as f:
            h = binascii.crc32(f.read(8192))

    # End time

    chrono.stop()

    # 
    # ---> We return both hash and execution time (for info)
    #

    return h, chrono.elapsed()



#
#    ====================================================================
#     Database connexion
#    ====================================================================
#
def db_connect(db, restart = False):

    """

        Connects to the file which will be used for the sqlite3 database. If needed (= if you start a new search or if you've asked for a restart manually),
        a new database will be created, else you just get the pointer to the file.

        If the database exists, we look into to get the state of the last call of the script, to manage the restart option, else we create a new database.

        Args:
            db (text): Name of the file used for storing sqlite3 database
            restart (boolean): (Optional) Indicates if your restart the process from the beginning or not
        
        Returns:
            cnx (sqlite3.Connection): Connection object (bound to the file _filename_)

    """

    cnx = sqlite3.connect(db)

    #
    # ---> Did we ask for a restart or not?
    #

    if not restart:

        # We didn't, so we continue the process. Does the table 'params' exist?

        res = cnx.execute("SELECT count(*) FROM sqlite_master WHERE type ='table' AND name ='params';").fetchone()

        if (res[0] == 1):

            # Yes, so we look for the status. If the status is empty, no step has been executed
            # so we have to recreate the database to start on clean basis.

            step = get_status(cnx)

            if (step == None):

                # No step in the database => Let's recreate the DB
                cnx.close()        
                cnx = db_create(db)

            else:

                # The script is in progress
                pass

        else:

            # No, there's no existing database, so we create one

            cnx = db_create(db)

    else:

        #
        #  'restart' is passed in args. So we drop & recreate the database
        #

        cnx = db_create(db)

    return cnx



#
#    ====================================================================
#     Database creation
#    ====================================================================
#

def db_create(db):

    """

        Creates the database tables (unconditionnally).

        Args:
            db (text): Name of the file used for storing sqlite3 database

        Returns:
            cnx (sqlite3.Connection): Connection object (bound to the file _filename_)
    """

    cnx = sqlite3.connect(db)
    #cnx = sqlite3.connect(':memory:') ==> in-memory for sqlite3 is not really faster 
    print("Creating database...")

    #
    # ---> Dropping old tables
    #

    try:

        # Drop all tables

        cnx.execute("DROP TABLE filelist")
        cnx.execute("DROP TABLE params")
        print("Old database deleted.")

    except sqlite3.OperationalError:

        # Exception means no old database

        print("No old database.")

    #
    # ---> Let's create the table used for storing files information
    #
    
    cnx.execute("CREATE TABLE filelist (\
                    fid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                    hash CHAR(256), \
                    pre_hash CHAR(256), \
                    path VARCHAR(4096), \
                    name TINYTEXT, \
                    original_path VARCHAR(4096), \
                    size BIGINT, \
                    marked_for_deletion BOOL, \
                    protected BOOL, \
                    access_denied BOOL, \
                    master BOOL, \
                    has_duplicate BOOL, \
                    os_errno TINYINT, \
                    os_strerror TEXT) \
                ")

    # ---> Some useful indexes to speed up the processing

    cnx.execute("CREATE INDEX index_filepath ON filelist (path, name)")
    cnx.execute("CREATE INDEX index_hash ON filelist (hash)")
    cnx.execute("CREATE INDEX index_pre_hash ON filelist (pre_hash)")

    #
    # ---> Params table used to store infomation about the process and restart steps.
    #
    
    cnx.execute("CREATE TABLE params(\
                    key TINYTEXT,\
                    value TEXT)\
                ")

    # --- > Default values

    cnx.execute("INSERT INTO params VALUES ('last_step','')")
    cnx.execute("INSERT INTO params VALUES ('last_id','')")
    cnx.execute("INSERT INTO params VALUES ('last_path','')")
    cnx.execute("INSERT INTO params VALUES ('last_file','')")

    cnx.commit()

    return cnx


#
#    ====================================================================
#     Get state of last call in the params table
#    ====================================================================
#

def get_status(cnx):

    """

        Gets the status of the last process, if it has beend stored, to handle a restart if needed.

        Args:
            cnx (sqlite3.Connection): Connection object

        Returns:
            value (text): Name of the last executed process

    """

    res = cnx.execute("SELECT value FROM params WHERE key='last_step'").fetchone()

    #
    # ---> Get last step
    #

    if (res != None):
        if (res[0] == ''):
            res= None
        else:
            res = res[0]

    #
    # ---> Get last ID (fid or hash)
    # 

    lid = cnx.execute("SELECT value FROM params WHERE key='last_id'").fetchone()

    if (lid != None):
        if (lid[0] == ''):
            lid= None
        else:
            lid = lid[0]

    return res, lid


#
#    ====================================================================
#     Set state of last (=current) step executed in the params table
#    ====================================================================
#

def checkpoint_db(cnx, last_step, last_id = None, commit = False):

    """

        Sets the status of the current process by storing the name of the last well-executed step.

        Args:
            cnx (sqlite3.Connection): Connection object
            last_step (text): Name of the last well-executed step

        Returns:
            nothing

    """

    cnx.execute("UPDATE params SET value=? WHERE key='last_step'", (last_step,))
    cnx.execute("UPDATE params SET value=? WHERE key='last_id'", (last_id,))

    if (commit):
        cnx.commit()

    return 



#
#    ====================================================================
#     Directory calculation (for all files in many directories)
#    ====================================================================
#

def directories_lookup(cnx, basepath_list):

    t_elaps = 0.0
    nb_files = 0

    # As there's no restart point here (we restart the loop), we need to reset the filelist table

    cnx.execute("DELETE FROM filelist")
    cnx.commit()

    for basepath in basepath_list:

        line        = basepath.rstrip("\n").split(";")

        if line[0] != '':

            p_master    = line[0]
            p_protected = line[1]
            path        = line[2]

            print("Considering {}, master:{} protected:{}...".format(path, p_master, p_protected))
            t, nb = directory_lookup(cnx, path, p_master, p_protected)
            
            t_elaps += t
            nb_files += nb

    return t_elaps, nb_files


#
#    ====================================================================
#     Directory calculation (for all files in one directory)
#    ====================================================================
#

def directory_lookup(cnx, basepath, master, protected):

    """

        Looks (hierarchically) for all files within the folder structure, and stores the path and the 
        name of each file. No file access is made (to save time).

        Args:
            cnx (sqlite3.Connection): Connection object
            basepath (text): Array of file paths we will look into.

        Returns:
            t (time): The execution time of this function
            nb_to_process (int): The number of files we have to process        

    """

    global last_step, last_id

    # Start time
    chrono = utils.Chrono()
    chrono.start()

    # Nb of files init
    nb = 0

    # Filepath init

    if (basepath == ""):
        basepath = "."

    #
    # ---> Files discovering. Thanks to Python, we just need to call an existing function...
    #

    for root, _, files in os.walk(basepath, topdown=True):

        #
        #  We just look for files, we don't process the directories
        #

        for name in files:

            # Hey, we got one (file)!

            nb = nb + 1
            cnx.execute("INSERT INTO filelist(path, name, access_denied, original_path, master, protected)\
                            VALUES (?, ?, ?, ?, ?, ?)",(root, name, False, basepath, master, protected))

            # Checkpoint

            last_step = "directory_lookup"
            last_id = "in progress"

            # Displaying progression and commit (occasionnaly)

            if ((nb % 100) == 0):
                print("Discovering #{} files ({:.2f} sec)".format(nb, chrono.elapsed()), end="\r", flush=True)
                if ((nb % 1000) == 0):
                    checkpoint_db(cnx, "directory_lookup", commit = True)

            """
            except PermissionError:

                cnx.execute("INSERT INTO filelist(pre_hash, path, name, access_denied)\
                                VALUES (?, ?, ?, ?)",("?", root, name, True))

            except OSError as ose:

                cnx.execute("INSERT INTO filelist(pre_hash, path, name, os_errno, os_strerror)\
                                VALUES (?, ?, ?, ?, ?)",("?", root, name, ose.errno, ose.strerror))
            """

    #
    # ---> Last commit
    #

    checkpoint_db(cnx, "directory_lookup", "all", commit = True)

    # End time
    chrono.stop()

    # Returning nb of files to process in the table. Should be the same as nb...

    r = cnx.execute("SELECT COUNT(*) FROM filelist")
    nb_to_process = r.fetchone()[0]
        
    return chrono.elapsed(), nb_to_process



#
#    ====================================================================
#     File list pre hash calculation (for all files)
#    ====================================================================
#

def filelist_pre_hash(cnx, algo):

    """

        Calculates a "pre-hash" that is a hash calculated on the first bytes of the file. 

        Listen to me well: hash calculation can be long for... long files. Here we make a first *selection*
        where we eliminate files without duplicates. As a matter of fact, if the hash of the first
        bytes are not equals, it means that the files are... not equals for sure!

        On the other hand, files with the same pre-hash need further investigation and we'll 
        calculate in the next step the complete hash, but only for duplicate candidates. Then
        we avoid unnecessary long calculation, especially for big files.

        Though you can use any system-known hash function, we suggest to use only **md5** for 
        pre-hashing, because it has enough entropy for our usage, and it's quicker in most situations.
        Better algos will have better result, but here we only want some file duplicate candidate selection.

        Args:
            cnx (sqlite3.Connection): Connection object
            algo (text): Name of the hash algo to use. 

        Returns:
            t (time): The execution time of this function

    """

    global last_step, last_id

    # Start time
    chrono = utils.Chrono()
    chrono.start()

    #
    # ---> Main loop (on all files)
    #
    
    nb = 0
    
    if (last_step != "filelist_pre_hash"):
        r = cnx.execute("SELECT * FROM filelist ORDER BY fid")
    else:
        r = cnx.execute("SELECT * FROM filelist WHERE fid >? ORDER BY fid", (last_id,))
        print("Restart from fid {}".format(last_id))

    for row in r:

        # Let's get the filepath of this element

        fid = row[0]
        filepath = os.path.join(row[3], row[4])

        try:

            file_stats = os.stat(filepath)
            file_size = file_stats.st_size 
            h, _ = file_hash_calc(filepath, algo)
            cnx.execute("UPDATE filelist SET size = ?, pre_hash = ? WHERE fid = (?)", (file_size, h, fid))

            # Checkpoint

            last_step = "filelist_pre_hash"
            last_id = fid

        except PermissionError as pe:

            #
            # Here we have an existing file but we have no right permission on it. Bad strike!
            # 

            cnx.execute("UPDATE filelist SET size = ?, access_denied = ? WHERE fid = (?)", (file_size, True, fid))

        except OSError as ose:

            #
            # Worst: we have an OS Error while retrieving file information or during hash calculation
            #
            # Example: We'll get an #22 error with an OneDrive file stored only in the cloud and not present on disk
            #
            
            cnx.execute("UPDATE filelist SET os_errno = ?, os_strerror=? WHERE fid = (?)", (ose.errno, ose.strerror, fid))


        nb = nb + 1

        # Displaying progression and commit (occasionnaly)

        if ((nb % 100) == 0):
            print("Quick hash computing #{} files ({:.2f} sec)".format(nb, chrono.elapsed()), end="\r", flush=True)
            if ((nb % 1000) == 0):
                checkpoint_db(cnx, "filelist_pre_hash", fid, commit = True)

    #
    #  ---> Last commit
    #

    checkpoint_db(cnx, "filelist_pre_hash", "all", commit = True)

    # End time
    chrono.stop()

    return chrono.elapsed()



#
#    ====================================================================
#     Finding pre-duplicates (files with the same pre_hash). We need to calculate the full hash for all of them
#    ====================================================================
#

def pre_duplicates_rehash(cnx):

    """
        Recalculates full hash for duplicate candidates (files having the same pre-hash). You can use here
        the hash function you want but consider "md5" as the best ratio entropy/execution time. The updates
        are made directly in the database.

        Args:
            cnx (sqlite3.Connection): Connection object

        Returns:
            t (time): The execution time of this function
    """

    global last_step, last_id

    # Start time
    chrono = utils.Chrono()
    chrono.start()

    #
    # ---> Selection of pre_hashes present more than once 
    #
    
    nb = 0

    if (last_step != "pre_duplicates_rehash"):

        # Here we start from the beginning and read all the files in DB
        res = cnx.execute("SELECT pre_hash FROM filelist GROUP BY pre_hash HAVING COUNT(pre_hash) > 1 ORDER BY fid")

    else:

        # Checkpoint/restart : we restart from last updated record (fid)
        res = cnx.execute("SELECT pre_hash FROM filelist WHERE fid >? GROUP BY pre_hash HAVING COUNT(pre_hash) > 1 ORDER BY fid", (last_id,))
        print("Restart from fid {}".format(last_id))

    for h in res:

        #
        # We look for all files that have the selected pre_hash
        # 

        hash = h[0]
        r = cnx.execute("SELECT * FROM filelist WHERE pre_hash = ?", (hash, ))

        for row in r:

            # Here we need to go a bit further: having the same pre_hash
            # does not mean that files are identical; we need to calculate the complete hash

            fid = row[0]
            filepath = os.path.join(row[3], row[4])
            full_hash, _ = file_hash_calc(filepath, "md5", False)

            cnx.execute("UPDATE filelist set hash = ? WHERE fid = (?)", (full_hash, fid))

            # Checkpoint
            
            last_step = "pre_duplicates_rehash"
            last_id = fid

            nb = nb + 1

            # Displaying progression and commit (occasionnaly)

            if ((nb % 100) == 0):
                print("Rehashing duplicate candidates #{} ({:.2f} sec)".format(nb, chrono.elapsed()), end="\r", flush=True)
                if ((nb % 1000) == 0):
                    checkpoint_db(cnx, "pre_duplicates_rehash", fid, commit = True)
        
    #
    #  ---> Last commit
    #
    
    checkpoint_db(cnx, "pre_duplicates_rehash", "all", commit = True)

    # End time
    chrono.stop()

    return chrono.elapsed(), nb


#
#    ====================================================================
#     Selecting "true" duplicates (= having the same hash ;)
#    ====================================================================
#

def duplicates_update(cnx):

    """
        Selects the *real* duplicates (= files having the same *full* hash), and marks them into the DB.

        Args:
            cnx (sqlite3.Connection): Connection object

        Returns:
            t (time): The execution time of this function        
            nb (int): The number of files having duplicates
            size (int): The size of all files that have duplicates
    """

    global last_step, last_id

    # Start time

    chrono = utils.Chrono()
    chrono.start()

    #
    # ---> All-in-one SQL query (updating the files in the selection of duplicates)
    #
    # The query has 2 parts:
    #   . The UPDATE that marks the 'has_duplicate' of all files whose hash is in the selected ones;
    #   . The SELECT used in the 'IN' clause where we select (complete) hashes present more than once.
    #

    cnx.execute("UPDATE filelist SET has_duplicate = True WHERE hash IN \
        (SELECT hash FROM filelist WHERE hash NOT NULL GROUP BY hash HAVING COUNT(hash) > 1 ORDER BY hash)")
        
    #
    #  ---> Last commit
    #

    # Checkpoint
    
    last_step = "pre_duplicates_rehash"
    last_id = "all"

    checkpoint_db(cnx, "duplicates_update", "all", commit = True)

    # Results...

    nb , size = duplicates_select(cnx)

    # End time
    chrono.stop()

    return chrono.elapsed(), nb, size


#
#    ====================================================================
#     Selecting "true" duplicates (= having the same hash ;)
#    ====================================================================
#

def duplicates_select(cnx):

    """

        Returns infos about files having duplicates in the database.

        Args:
            cnx (sqlite3.Connection): Connection object

        Returns:
            nb (int): The number of files having duplicates
            size (int): The size of all files that have duplicates
    """

    # Nb of files that have duplicates
    # ---
    r = cnx.execute("SELECT COUNT(*) FROM filelist WHERE has_duplicate = True")
    nb = r.fetchone()[0]

    # Size of all files that are duplicated
    # ---
    r = cnx.execute("SELECT SUM(size) FROM filelist WHERE has_duplicate = True")
    size = r.fetchone()[0] 

    return nb, size


#
#    ====================================================================
#
#     Main part
#
#    ====================================================================
#

# 
# ---> Check for 'restart' argument
#

arguments = utils.check_arguments(sys.argv)

if ("restart" in arguments):
    restart = True
else:
    restart = False

#
# ---> Catch the exit signal to commit the database with last checkpoint
#

signal.signal(signal.SIGINT, exit_handler)

#
# ---> Some inits
#

db = 'walk.db'
algo = 'md5'

with open("filelist.txt","r") as f:
    basepath = f.readlines()

#print(basepath)
print("Default blocksize for this system is {} bytes.".format(io.DEFAULT_BUFFER_SIZE))

#
# ---> DB connection
#

cnx = db_connect(db, restart)

last_step, last_id = get_status(cnx)
print("Last step: {}, last ID: {}".format(last_step, last_id))
next_step = False

# Looking for files
# ---

if (last_step == None) | ((last_step == "directory_lookup") & (last_id == "in progress")):

    t, nb = directories_lookup(cnx, basepath)
    print("Files lookup duration: {:.2f} sec for {} files.".format(t, nb))
    next_step = True

else:

    print("Files lookup already done.")


# Calculating pre hash (quick hash on first bytes)
# ---

if (next_step | 
    ((last_step == "directory_lookup") & (last_id == "all"))|
    ((last_step == "filelist_pre_hash") & (last_id != "all"))):

    t = filelist_pre_hash(cnx, 'md5')
    print("Pre-hash calculation duration: {:.2f} sec.          ".format(t))
    next_step = True

else:

    print("Pre-hash calculation already done.")


# Calculate size of all files
# ---

res = cnx.execute("select sum(size) FROM filelist")
size = res.fetchone()[0]

print("Size of all files: {}".format(utils.humanbytes(size)))

# Recomputing hashes for duplicates candidates
# ---

if (next_step | 
    ((last_step == "filelist_pre_hash") & (last_id == "all")) |
    ((last_step == "pre_duplicates_rehash") & (last_id != "all"))):

    t, nb = pre_duplicates_rehash(cnx)
    print("Pre-duplicates rehashing duration: {:.2f} sec. for {} records.".format(t, nb))
    next_step = True

else:

    print("Pre-duplicates rehashing already done.")

# Dealing with duplicates
# ---

if (next_step | (last_step == "pre_duplicates_rehash")):
    
    t, nb_dup, size_dup = duplicates_update(cnx)

else:

    nb_dup, size_dup = duplicates_select(cnx)

# Result summary
# ---
print("{} files have duplicates, total size of duplicate files is {}.".format(nb_dup, utils.humanbytes(size_dup)))


# Closing database
# ---

cnx.close()
