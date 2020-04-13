import time

#
#  Global constants
#

db_name       = "walk.db"
filelist_name = "filelist.txt"
hash_algo     = "md5"
trash_dir     = "C:\\Users\\Janiko\\OneDrive\\trash"


#    -------------------------------
#
#     Chrono Class
#
#    -------------------------------

class Chrono:

    """
        A simple class to help mesuring execution time of a function. Can be cumulative with several start/stop.
    """

    def __init__(self):

        #
        # Init function.
        #

        # t0 is the start time
        self.t0  = None

        # t1 is the end time
        self.t1  = None

        # t is execution time
        self.t   = None

        # sum is the sum of execution time in case of several start/stop
        self.sum = 0.0

        # running is the state of measurement
        self.running = False


    def start(self):

        # Start function. t0 is set, and the running status is set to True.

        self.t0 =  time.time()
        self.t1  = None
        self.t   = None
        self.running = True


    def stop(self):

        # Stop function. t is calculated bu subtracting the stop time t1 to the start time.
        # And sum adds this execution time to itself, to cumulate all start/stop. 
        # Note: to reset, just create a new Chrono() object...

        self.t1 =  time.time()
        self.t  = self.t1 - self.t0
        self.sum = self.sum + self.t
        self.running = False


    def elapsed(self, total=False):

        # Displays elapsed time. If total is True, it display the elapsed time + sum of stored execution time
        # If the chrono is running, it doesn't stop it but only return the current execution time
        # If the chrono never started, it returns nothing

        try:
            if (not total):
                if (self.running == True):
                    t_int = time.time()
                    return t_int - self.t0
                else:
                    return self.t
            else:
                if (self.running == True):
                    t_int = time.time()
                    return self.sum + t_int - self.t0
                else:
                    return self.sum
        except:
            return None

    def __str__(self):

        # Customized str function

        return "({}, {}, {}, {}, {})".format(self.t0, self.t1, self.t, self.sum, self.running)

    def __repr__(self):

        # CUstomized representation (for testing purpose)

        return str(self)



#    -------------------------------
#
#     Useful functions for the database
#
#    -------------------------------

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


    # We update the params table with the last well completed step

    cnx.execute("UPDATE params SET value=? WHERE key='last_step'", (last_step,))
    cnx.execute("UPDATE params SET value=? WHERE key='last_id'", (last_id,))

    if last_step == "directory_lookup" and last_id != "in progress":

        # Here we are in the 1st step (file lookup). Here we store the completed directories
        cnx.execute("INSERT INTO params VALUES (?, ?)", ("completed_dir", last_id))

    if (commit):
        cnx.commit()

    return 



#    -------------------------------
#
#     Some other useful functions
#
#    -------------------------------

def check_arguments(args):

    return args



def humanbytes(B):
    
    # https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/52379087
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B/TB)



#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
