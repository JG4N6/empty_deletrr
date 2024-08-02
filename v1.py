import os 
import sys

def split_path(path):
    parts = []
    while True:
        path, tail = os.path.split(path)
        if tail:
            parts.insert(0, tail)
        else:
            if path:
                parts.insert(0, path)
            break
    return parts


def now(tz_string="Pacific/Auckland", trailing_newline=False):
	
	if 'datetime' not in sys.modules:
		from datetime import datetime
	else:
		datetime = sys.modules['datetime'].datetime

	if 'pytz' not in sys.modules:
		import pytz
	else:
		pytz = sys.modules['pytz']

	if tz_string:
		tz = pytz.timezone(tz_string)
	else:
		tz = pytz.utc

	utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
	tz_now = utc_now.astimezone(tz)
	
	if not trailing_newline:
		return tz_now.strftime('%Y-%m-%d %H:%M:%S %Z%z')
	else:
		return tz_now.strftime('%Y-%m-%d %H:%M:%S %Z%z')+"\n"


def get_all_files_in_folder_recursive(folder, verbose=False):
	my_items = []
	for root, subs, files in os.walk(folder):
		for f in files:
			my_items.append(os.path.join(root, f))
	if verbose:
		print(f"Found {len(my_items)} file(s) in {folder}")
	return my_items


def get_all_folders_in_folder_recursive(folder, verbose=False):
	my_items = []
	for root, subs, files in os.walk(folder):
		for s in subs:
			my_items.append(os.path.join(root, s))
	if verbose:
		print(f"Found {len(my_items)} folders(s) in '{folder}'")
	return my_items


def count_subfolders(path):
    try:
        # List all entries in the directory
        entries = os.listdir(path)
        
        # Filter out only directories
        subfolders = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
        
        # Count the subfolders
        return len(split_path(path))
    except FileNotFoundError:
        print(f"The path {path} does not exist.")
        return 0
    except PermissionError:
        print(f"Permission denied to access the path {path}.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


def delete_folder_if_empty(folder_path):
    try:
        # Attempt to remove the directory
        os.rmdir(folder_path)
        return 1

    except OSError as e:
        return 0


def run(log_deletes=False):
	log_lines = []
	folder_delete_counter = 0
	files_delete_counter = 0
	error_count = 0


	print(f"\n{now()}\nStarting on {root_folder}\n")
	my_files = get_all_files_in_folder_recursive(root_folder)
	my_folders = get_all_folders_in_folder_recursive(root_folder)

	print (f"{now()}\nCollected file system extents\n\tLocated {len(my_files)} files\n\tLocated {len(my_folders)} folders\n\nCalculating subfolders max depth\n") 

	folders_by_sub_folder_depth = {}
	for folder in my_folders:
		subs_len = count_subfolders(folder)
		if subs_len not in folders_by_sub_folder_depth:
			folders_by_sub_folder_depth[subs_len] = []
		folders_by_sub_folder_depth[subs_len].append(folder)

	max_key = max(list(folders_by_sub_folder_depth.keys()))
	print (f"{now()} - Done - max depth is {max_key}\n\nExample max depth folder:\n{folders_by_sub_folder_depth[max_key][0]}\n\nRemoving empty content\n")
	printed_values = []
	for f in my_files:
		try:
			if os.path.getsize(f) == 0:
				os.remove(f)
				log_lines.append(f)
				files_delete_counter += 1
				if all([files_delete_counter % 500 == 0, files_delete_counter not in printed_values, verbose, True]):
					print (f"Removed {files_delete_counter} empty files")
					printed_values.append(files_delete_counter)
		except PermissionError:
			error_count += 1
		except FileNotFoundError:
			error_count += 1

	folder_keys = list(folders_by_sub_folder_depth.keys())
	folder_keys.sort(reverse=True)


	last_tally = 0
	while last_tally != 0:
		last_tally = 0
		printed_values = []
		for i in folder_keys:
			print (f"Folder depth: {i} - ({len(folders_by_sub_folder_depth[i])})")
			for folder in folders_by_sub_folder_depth[i]:
				try:
					folder_delete_counter += delete_folder_if_empty(folder)
					log_lines.append(folder)
					if all([files_delete_counter % 500 == 0, files_delete_counter not in printed_values, verbose, True]):
						print (f"Removed {folder_delete_counter} empty folders")
						printed_values.append(folder_delete_counter)
						last_tally += 1
				except:
					pass
		print ("Looping back over folders until complete")

	print (f"{now()} - Finished\n\tDealt with {files_delete_counter} empty files\n\tDealt with {folder_delete_counter} empty folders\n") 

	if log_deletes and len(lines) != 0:
		if not os.path.exists(os.path.dirname(log_file_path)):
			os.makedirs(os.path.dirname(log_file_path))

		with open(log_file_path, "w", encoding="utf8") as data:
			for l in lines:
				data.write(l+"\n")
		print(f"Cleans logged to {log_file_path}")

verbose = False
root_folder = r"my/files/dump"
log_file_path = r"my/log/files/empty_delete_log.txt"

run(log_deletes=True)
