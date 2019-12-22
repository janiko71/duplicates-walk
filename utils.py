import time


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


# -------------------------------
#
#  Some other useful functions
#
# -------------------------------

def check_arguments(args):

    return args



#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
