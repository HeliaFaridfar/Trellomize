import json
import os
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import List
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich import print

# enum for Priority
class Priority(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

# enum for Status
class Status(Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"

class User:
    def __init__(self, U, P, E):
        self._username = U
        self._password = P
        self._emailaddress = E
        self._active = True

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    def get_emailaddress(self):
        return self._emailaddress

    def is_active(self):
        return self._active

    def set_username(self, U):
        self._username = U

    def set_password(self, P):
        self._password = P

    def set_emailaddress(self, E):
        self._emailaddress = E

    def set_active(self, A):
        self._active = A

    def login(self, U, P):
        return self._username == U and self._password == hashed_password(P)

    def disable(self):
        self._active = False

    def to_dict(self):
        return {
            "username": self._username,
            "password": self._password,
            "emailaddress": self._emailaddress,
            "active": self._active
        }

class Duty:
    def __init__(self, Id, title: str, detail: str, assignees: List[User], assigned_to: User = None):
        self._ID = Id
        self._Title = title
        self._Detail = detail
        self._ST = datetime.now()
        self._FT = self._ST + timedelta(hours=24)
        self._Priority = Priority.LOW
        self._Status = Status.BACKLOG
        self._Assignees = assignees
        self._AssignedTo = assigned_to

    def get_ID(self):
        return self._ID

    def get_title(self):
        return self._Title

    def get_detail(self):
        return self._Detail

    def get_st(self):
        return self._ST

    def get_ft(self):
        return self._FT

    def get_priority(self):
        return self._Priority

    def get_status(self):
        return self._Status

    def get_assignees(self):
        return self._Assignees

    def get_assigned_to(self):
        return self._AssignedTo

    def set_ID(self, Id):
        self._ID = Id

    def set_title(self, title):
        self._Title = title

    def set_detail(self, detail):
        self._Detail = detail

    def set_st(self, value):
        self._ST = value

    def set_ft(self, value):
        self._FT = value

    def set_priority(self, value: Priority):
        self._Priority = value

    def set_status(self, value: Status):
        self._Status = value

    def set_assignees(self, value: List[User]):
        self._Assignees = value

    def set_assigned_to(self, user: User):
        self._AssignedTo = user

    def add_assignee(self, user: User):
        if user not in self._Assignees:
            self._Assignees.append(user)

    def delete_assignee(self, user: User):
        if user in self._Assignees:
            self._Assignees.remove(user)

class Project:
    def __init__(self, Id, T, leader, members: List[User] = [], duties: List[Duty] = []):
        self._ID = Id
        self._Title = T
        self._Leader = leader
        self._Members = members
        self._Duties = duties

    def get_id(self):
        return self._ID

    def get_T(self):
        return self._Title

    def get_leader(self):
        return self._Leader

    def get_members(self):
        return self._Members

    def get_duties(self):
        return self._Duties

    def set_ID(self, Id):
        self._ID = Id

    def set_Title(self, T):
        self._Title = T

    def set_Leader(self, leader):
        self._Leader = leader

    def set_Members(self, members: List[User]):
        self._Members = members

    def set_duties(self, duties: List[Duty]):
        self._Duties = duties

    def add_duty(self, Id, title: str, detail: str, assignees: List[User]):
        new_duty = Duty(Id, title, detail, assignees)
        self._Duties.append(new_duty)
        return new_duty

    def add_member(self, user: User):
        if user not in self._Members:
            self._Members.append(user)

    def remove_member(self, user: User):
        if user in self._Members:
            self._Members.remove(user)

    def delete_project(self):
        pass

    def assign_duty(self, duty_id, username):
        for duty in self._Duties:
            if duty.get_ID() == duty_id:
                assignee = next((member for member in self._Members if member.get_username() == username), None)
                if assignee:
                    duty.set_assigned_to(assignee)
                    print(f"[green]Duty '{duty.get_title()}' assigned to '{username}' successfully.[/green]")
                else:
                    print(f"[red]Error! User '{username}' is not a member of this project.[/red]")
                return
        print(f"[red]Error! Duty with ID '{duty_id}' not found.[/red]")

    def unassign_duty(self, duty_id):
        for duty in self._Duties:
            if duty.get_ID() == duty_id:
                duty.set_assigned_to(None)
                print(f"[green]Duty '{duty.get_title()}' unassigned successfully.[/green]")
                return
        print(f"[red]Error! Duty with ID '{duty_id}' not found.[/red]")

    def print_duties(self):
        console = Console()
        table = Table(title="Project Duties")

        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Detail", style="green")
        table.add_column("Start Time", justify="center", style="yellow")
        table.add_column("Status", justify="center", style="red")

        for duty in self._Duties:
            table.add_row(
                duty.get_ID(),
                duty.get_title(),
                duty.get_detail(),
                duty.get_st().strftime("%Y-%m-%d %H:%M:%S"),
                duty.get_status().value
            )

        console.print(table)

def LoadUsers(file_path='users.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            users = json.load(file)
            for user in users:
                if 'role' not in user:
                    user['role'] = ''
            return users
    return []

def SaveUsers(users, file_path='users.json'):
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

def LoadProjects(file_path='projects.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def SaveProjects(projects, file_path='projects.json'):
    with open(file_path, 'w') as file:
        json.dump(projects, file, indent=4)

def hashed_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_an_account(username, emailaddress, password):
    users = LoadUsers()
    for user in users:
        if user['username'] == username or user['emailaddress'] == emailaddress:
            print("[red]Error! Username or email already exists.[/red]")
            return

    new_user = {'username': username, 'emailaddress': emailaddress, 'password': hashed_password(password)}
    users.append(new_user)
    SaveUsers(users)
    print("[green]Account created successfully![/green]")

def login_user(username, password):
    users = LoadUsers()
    for user in users:
        if user['username'] == username:
            if hashed_password(password) == user['password']:
                print("[green]Login successful[/green]")
                return User(user['username'], user['password'], user['emailaddress'])
            else:
                print("[red]Error! Invalid password[/red]")
                return None
    print("[red]Error! Invalid username or password.[/red]")
    return None

def create_project(ID, Title,username):
    projects = LoadProjects()
    for project in projects:
        if project['ID'] == ID:
            print("[red]Error! Project ID already exists.[/red]")
            return

    new_project = Project(ID, Title,username)
    projects.append({
        'ID': new_project.get_id(),
        'Title': new_project.get_T(),
        'Leader': username,
        'Members': [member.to_dict() for member in new_project.get_members()],
        'Duties': []
    })
    SaveProjects(projects)
    print("[green]Project created successfully![/green]")

#To add a member to a project
def add_member_to_project(project_id, username):
    projects = LoadProjects()
    users = LoadUsers()
    user_to_add = next((u for u in users if u['username'] == username), None)

    if not user_to_add:
        print(f"Error! User '{username}' not found.")
        return

    for project in projects:
        if project['ID'] == project_id:
            if any(member['username'] == username for member in project['Members']):
                print(f"Error! User '{username}' is already a member of the project.")
                return
            project['Members'].append(user_to_add)
            SaveProjects(projects)
            print(f"User '{username}' added to project '{project['Title']}' successfully.")
            return

    print(f"Error! Project with ID '{project_id}' not found.")

#To remove a member from a project
def remove_member_from_project(project_id, username):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            project['Members'] = [m for m in project['Members'] if m['username'] != username]
            SaveProjects(projects)
            print(f"User '{username}' removed from project '{project['Title']}' successfully.")
            return

    print(f"Error! Project with ID '{project_id}' not found.")

#To delete a project
def delete_project(project_id, leader: User):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            if project['Leader'] != leader.get_username():
                print(f"Error! Only the leader can delete the project.")
                return
            projects.remove(project)
            SaveProjects(projects)
            print(f"Project with ID '{project_id}' deleted successfully.")
            return

    print(f"Error! Project with ID '{project_id}' not found.")

# To assign a duty to a member
def assign_duty_to_member(project_id, duty_id, username):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            leader = User(project['Leader'], '', '')  # Assuming leader does not need a role

            # Create Project instance with proper User and Duty objects
            members = [User(m['username'], '', '') for m in project['Members']]
            duties = [
                Duty(
                    d['ID'],
                    d['Title'],
                    d['Detail'],
                    [User(a['username'], '', '') for a in d['Assignees']],
                    User(d['AssignedTo']['username'], '', '') if d['AssignedTo'] else None
                ) for d in project['Duties']
            ]

            project_instance = Project(project['ID'], project['Title'], leader, members, duties)

            # Assign the duty to the user
            project_instance.assign_duty(duty_id, username)
            
            # Update the project duties in the original data structure
            project['Duties'] = [
                {
                    'ID': duty.get_ID(),
                    'Title': duty.get_title(),
                    'Detail': duty.get_detail(),
                    'ST': duty.get_st().isoformat(),
                    'FT': duty.get_ft().isoformat(),
                    'Priority': duty.get_priority().value,
                    'Status': duty.get_status().value,
                    'Assignees': [{'username': user.get_username(), 'password': user.get_password(), 'emailaddress': user.get_emailaddress(), 'active': user.is_active()} for user in duty.get_assignees()],
                    'AssignedTo': {'username': duty.get_assigned_to().get_username(), 'password': duty.get_assigned_to().get_password(), 'emailaddress': duty.get_assigned_to().get_emailaddress(), 'active': duty.get_assigned_to().is_active()} if duty.get_assigned_to() else None
                } for duty in project_instance.get_duties()
            ]
            
            SaveProjects(projects)
            return
    print(f"Error! Project with ID '{project_id}' not found.")

#To unassign a duty from a member
def unassign_duty_from_member(project_id, duty_id):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            project_instance = Project(
                project['ID'],
                project['Title'],
                User(project['Leader'], '', ''),
                [Duty(d['ID'], d['Title'], d['Detail'], d['Assignees'], d['AssignedTo']) for d in project['Duties']],
                [User(m['username'], m['password'], m['role']) for m in project['Members']]
            )
            project_instance.unassign_duty(duty_id)
            project['Duties'] = [duty.__dict__ for duty in project_instance.get_duties()]
            SaveProjects(projects)
            return

    print(f"Error! Project with ID '{project_id}' not found.")

#New function to list duties of a project for a member
def list_project_duties(user: User, project_id):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            project_instance = Project(
                project['ID'],
                project['Title'],
                User(project['Leader'], '', ''),
                [Duty(d['ID'], d['Title'], d['Detail'], d['Assignees'], d['AssignedTo']) for d in project['Duties']],
                [User(m['username'], m['password'], m['role']) for m in project['Members']]
            )
            if user.get_username() in [m.get_username() for m in project_instance.get_members()]:
                project_instance.print_duties()
                return
            else:
                print(f"Error! User '{user.get_username()}' is not a member of this project.")
                return

    print(f"Error! Project with ID '{project_id}' not found.")

#New function to update duty details by a member
def update_duty_details(user: User, project_id, duty_id, **kwargs):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            # Create a proper Project instance
            leader = User(project['Leader'], '', '')  # Assuming leader does not need a role
            members = [User(m['username'], m['password'], m.get('emailaddress', '')) for m in project['Members']]
            duties = [
                Duty(
                    d['ID'],
                    d['Title'],
                    d['Detail'],
                    [User(a['username'], a['password'], a.get('emailaddress', '')) for a in d['Assignees']],
                    User(d['AssignedTo']['username'], '', '') if d['AssignedTo'] else None
                ) for d in project['Duties']
            ]
            
            project_instance = Project(project['ID'], project['Title'], leader, members, duties)
            
            for duty in project_instance.get_duties():
                if duty.get_ID() == duty_id:
                    if duty.get_assigned_to() and duty.get_assigned_to().get_username() == user.get_username():
                        if 'title' in kwargs:
                            duty.set_title(kwargs['title'])
                        if 'detail' in kwargs:
                            duty.set_detail(kwargs['detail'])
                        if 'st' in kwargs:
                            duty.set_st(kwargs['st'])
                        if 'ft' in kwargs:
                            duty.set_ft(kwargs['ft'])
                        if 'priority' in kwargs:
                            duty.set_priority(kwargs['priority'])
                        if 'status' in kwargs:
                            duty.set_status(kwargs['status'])
                        
                        # Update the project duties in the original data structure
                        project['Duties'] = [
                            {
                                'ID': duty.get_ID(),
                                'Title': duty.get_title(),
                                'Detail': duty.get_detail(),
                                'ST': duty.get_st().isoformat(),
                                'FT': duty.get_ft().isoformat(),
                                'Priority': duty.get_priority().value,
                                'Status': duty.get_status().value,
                                'Assignees': [{'username': user.get_username(), 'password': user.get_password(), 'emailaddress': user.get_emailaddress(), 'active': user.is_active()} for user in duty.get_assignees()],
                                'AssignedTo': {'username': duty.get_assigned_to().get_username(), 'password': duty.get_assigned_to().get_password(), 'emailaddress': duty.get_assigned_to().get_emailaddress(), 'active': duty.get_assigned_to().is_active()} if duty.get_assigned_to() else None
                            } for duty in project_instance.get_duties()
                        ]
                        SaveProjects(projects)
                        print(f"Duty '{duty_id}' updated successfully.")
                        return
                    else:
                        print(f"Error! User '{user.get_username()}' is not assigned to this duty.")
                        return

    print(f"Error! Project with ID '{project_id}' not found.")

#To view the list of projects
def list_user_projects(user: User):
    projects = LoadProjects()
    leader_projects = []
    member_projects = []

    for project_data in projects:
        leader = project_data['Leader']
        if leader == user.get_username():
            leader_projects.append(project_data['Title'])
        else:
            for duty in project_data['Duties']:
                for assignee in duty['Assignees']:
                    if assignee['username'] == user.get_username():
                        member_projects.append(project_data['Title'])
                        break

    print(f"Projects led by {user.get_username()}: {leader_projects}")

def user_menu():
    console = Console()
    console.print("[bold magenta]--- Menu ---[/bold magenta]")
    console.print("1. Create an account")
    console.print("2. Log in")
    console.print("3. Exit")

    choice = input("Enter your choice: ")
    return choice

def project_menu():
    console = Console()
    console.print("[bold magenta]--- Project Menu ---[/bold magenta]")
    console.print("1. Create project")
    console.print("2. List my projects")
    console.print("3. Exit")

    choice = input("Enter your choice: ")
    return choice

def project_information():
    console = Console()
    console.print("[bold magenta]--- Project Information ---[/bold magenta]")
    console.print("1. Add member")
    console.print("2. Delete member")
    console.print("3. Assignment of duties")
    console.print("4. Unassignment of duties")
    console.print("5. Update duty details")
    console.print("6. Delete Project")
    console.print("7. Exit")

    choice = input("Enter your choice: ")
    return choice

def main():
    while True:
        choice = user_menu()
        if choice == '1':
            username = Prompt.ask("Enter [bold yellow]username[/bold yellow]: ")
            email = input("Enter email: ")
            password = input("Enter password: ")
            create_an_account(username, email, password)
        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            logged_in_user = login_user(username, password)
            if logged_in_user:
                print(f"Welcome, {logged_in_user.get_username()}!")

                while True:
                    choice2 = project_menu()
                    if choice2 == '1':
                        ID = input("Enter the project ID: ")
                        Title = input("Enter the title of the project: ")
                        create_project(ID, Title, username)
                    elif choice2 == '2':
                        while True:
                            choice3 = project_information()
                            if choice3 == '1':
                                project_id = input("Enter the project ID: ")
                                member_username = input("Enter username: ")
                                add_member_to_project(project_id, member_username)
                            elif choice3 == '2':
                                project_id = input("Enter the project ID: ")
                                member_username = input("Enter username: ")
                                remove_member_from_project(project_id, member_username)
                            elif choice3 == '3':
                                project_id = input("Enter the project ID: ")
                                duty_id = input("Enter the duty ID: ")
                                assignee_username = input("Enter username: ")
                                assign_duty_to_member(project_id, duty_id, assignee_username)
                            elif choice3 == '4':
                                project_id = input("Enter the project ID: ")
                                duty_id = input("Enter the duty ID: ")
                                unassign_duty_from_member(project_id, duty_id)
                            elif choice3 == '5':
                                project_id = input("Enter the project ID: ")
                                duty_id = input("Enter the duty ID: ")

                                update_fields = {}
                                update_title = input("Enter new title (or leave blank to keep current): ")
                                if update_title:
                                    update_fields['title'] = update_title

                                update_detail = input("Enter new detail (or leave blank to keep current): ")
                                if update_detail:
                                    update_fields['detail'] = update_detail

                                update_st = input("Enter new start time (YYYY-MM-DD HH:MM:SS) (or leave blank to keep current): ")
                                if update_st:
                                    update_fields['st'] = datetime.fromisoformat(update_st)

                                update_ft = input("Enter new finish time (YYYY-MM-DD HH:MM:SS) (or leave blank to keep current): ")
                                if update_ft:
                                    update_fields['ft'] = datetime.fromisoformat(update_ft)

                                update_priority = input("Enter new priority (CRITICAL/HIGH/MEDIUM/LOW) (or leave blank to keep current): ")
                                if update_priority:
                                    update_fields['priority'] = Priority[update_priority.upper()]

                                update_status = input("Enter new status (BACKLOG/TODO/DOING/DONE/ARCHIVED) (or leave blank to keep current): ")
                                if update_status:
                                    update_fields['status'] = Status[update_status.upper()]

                                update_duty_details(logged_in_user, project_id, duty_id, **update_fields)
                            elif choice3 == '6':
                                project_id = input("Enter the project ID: ")
                                delete_project(project_id, logged_in_user)
                            elif choice3 == '7':
                                print("[green]Exiting the program...[/green]")
                                break
                            else:
                                print("Invalid choice. Please try again.")
                    elif choice2 == '3':
                        print("Exiting the project menu.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()