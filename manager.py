import argparse
import os
import json

def create_admin(username, password):
    admin_file = 'admin.json'
    
    if os.path.exists(admin_file):
        with open(admin_file, 'r') as file:
            admin_data = json.load(file)
            if admin_data.get('username') == username:
                print("Error: Admin user already exists.")
                return
    
    admin_data = {
        'username': username,
        'password': password
    }
    
    with open(admin_file, 'w') as file:
        json.dump(admin_data, file)
    
    print("Admin user created successfully.")

def purge_data():
    data_files = ['users.json', 'projects.json']
    
    print("Are you sure you want to delete all data? This action cannot be undone. (yes/no)")
    choice = input().strip().lower()
    
    if choice == 'yes':
        for data_file in data_files:
            if os.path.exists(data_file):
                os.remove(data_file)
                print(f"Deleted {data_file}")
            else:
                print(f"{data_file} does not exist.")
        print("All data has been purged.")
    else:
        print("Purge data operation canceled.")

def main():
    parser = argparse.ArgumentParser(description='Manage system admin user and data.')
    
    subparsers = parser.add_subparsers(dest='command')
    
    create_admin_parser = subparsers.add_parser('create-admin', help='Create an admin user')
    create_admin_parser.add_argument('--username', required=True, help='Admin username')
    create_admin_parser.add_argument('--password', required=True, help='Admin password')
    
    purge_data_parser = subparsers.add_parser('purge-data', help='Purge all data')
    
    args = parser.parse_args()
    
    if args.command == 'create-admin':
        create_admin(args.username, args.password)
    elif args.command == 'purge-data':
        purge_data()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()