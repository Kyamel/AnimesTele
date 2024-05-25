import argparse
from local import db_sqlite3_acess

def main(mode):
    if mode == 'local_windows_run':
        local_windows_run()
    elif mode == 'local_windows_debug':
        local_windows_debug()
    elif mode == 'server_run':
        server_run()
    elif mode == 'server_debug':
        server_debug()
    elif mode == 'local_linux_run':
        local_linux_run()
    elif mode == 'local_linux_debug':
        local_linux_debug()
    else:
        print(f"Unknown mode: {mode}")

def local_windows_run():
    print("Running in local Windows mode...")
    db_sqlite3_acess.data_collect_and_insert_in_database()

def local_windows_debug():
    print("Debugging in local Windows mode...")
    db_sqlite3_acess.data_collect_and_insert_in_database(print_log=True)
    
def server_run():
    print("Running in server mode...")
                                 
def server_debug():
    print("Debugging in server mode...")

def local_linux_run():
    print("Running in local Linux mode...")

def local_linux_debug():
    print("Debugging in local Linux mode...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the program in different modes.')
    parser.add_argument('mode', choices=[
        'local_windows_run', 'local_windows_debug','server_run', 'server_debug',
        'local_linux_run', 'local_linux_debug'
    ], help='Mode to run the program in.')

    args = parser.parse_args()
    main(args.mode)