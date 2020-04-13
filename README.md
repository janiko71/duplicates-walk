# duplicates
Helps removing duplicates files in yuor filesystem.
# How it works?
In a few words: it scans directories, store the file names and information in a ```sqlite3``` database (file), looks for duplicates and put the unwanted files in a "trash".
## First phase
The script ```dup.py``` takes one file in argument (by default ```filelist.txt```, but you can change it in ```utils.py```). This file contains the directories you want to scan for duplicates.

Just run it.

It can be very long to execute, but you can restart anytime without problem, it's **designed to be stopped and restarted** at any step, without loosing information or doing the job twice.
### File list structure
Looks like a ```.csv``` file, but it's only text:
* 1st column is 0 or 1 (1 means the directory is the **master** one)
* 2nd is not used for now, but means **protected** directory.
* 3rd is the directory name (ex: "C:\User\johndoe\DOcuments")
### ```dup.py``` arguments
None. If you add "restart", the database will be wiped.
### ```utils.py``` parameters
You can change a couple of parameters in this file:
- The filename sqlite3 will use to store the database (```db_name```);
- The filename of the scanned directories (```filelist_name```)
- The directory where you will move the duplicate files (```trash_dir```)
- The hash algo used for comparison (```hash_algo```)
You can choose any supported hash, but for deduplication ```md5``` is the best candidate (fast and discriminating enough).

## 2nd phase
A ```clean.py``` script will delete the duplicates file. For now, it doesn't touch the master directories, and remove all files in other directories that have a least one duplicate in a master directory.

To be precise, all files are moved in a trash directory, and not really deleted. When finished, do what you want with the trash (delete, cold storage, etc.).

If an error occurs (ex: bad permissions for deleting), the files won't be trashed but will remain marked "to be deleted" with an error code. You can modify permissions and re-run the clean program, it will retry with those files in error.

### Examples
If you have 4 duplicates, 1 in the master, 3 in other directories, all 3 files in other directories will be deleted (trashed).

If you have 2 files that are duplicates but only in normal directories (not master), they won't be removed.