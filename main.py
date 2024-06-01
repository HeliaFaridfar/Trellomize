import email
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
import logging
import re

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    else:
        return False

# Configure logging
logging.basicConfig(filename='project_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"Duty '{title}' added to project '{self._Title}'.")
        return new_duty

    def add_member(self, user: User):
        if user not in self._Members:
            self._Members.append(user)
            logging.info(f"User '{user.get_username()}' added to project '{self._Title}'.")

    def remove_member(self, user: User):
        if user in self._Members:
            self._Members.remove(user)
        logging.info(f"User '{user.get_username()}' removed from project '{self._Title}'.")

    def delete_project(self):
        logging.info(f"Project '{self._Title}' deleted.")
        pass

    def assign_duty(self, duty_id, username):
        for duty in self._Duties:
            if duty.get_ID() == duty_id:
                assignee = next((member for member in self._Members if member.get_username() == username), None)
                if assignee:
                    duty.set_assigned_to(assignee)
                    logging.info(f"Duty '{duty.get_title()}' assigned to '{username}' in project '{self._Title}'.")
                    print(f"[green]Duty '{duty.get_title()}' assigned to '{username}' successfully.[/green]")
                else:
                    logging.error(f"Error! User '{username}' is not a member of the project '{self._Title}'.")
                    print(f"[red]Error! User '{username}' is not a member of this project.[/red]")
                return
            logging.error(f"Error! Duty with ID '{duty_id}' not found in project '{self._Title}'.")
        print(f"[red]Error! Duty with ID '{duty_id}' not found.[/red]")

    def unassign_duty(self, duty_id):
        for duty in self._Duties:
            if duty.get_ID() == duty_id:
                duty.set_assigned_to(None)
                logging.info(f"Duty '{duty.get_title()}' unassigned in project '{self._Title}'.")
                print(f"[green]Duty '{duty.get_title()}' unassigned successfully.[/green]")
                return
            logging.error(f"Error! Duty with ID '{duty_id}' not found in project '{self._Title}'.")
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
    logging.info(f"Account created for user '{username}'.")

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
    users = LoadUsers()
    for user in users:
        if user['username'] == username:
            leader = User(user['username'], user['password'], user['emailaddress'])
            new_project = {'ID': ID, 'Title': Title, 'Leader': username, 'Members': [username], 'Duties': []}
            projects.append(new_project)
            SaveProjects(projects)
            print("[green]Project created successfully![/green]")
            return

    print("[red]Error! Leader not found.[/red]")

def create_a_new_project(title, leader):
    projects = LoadProjects()
    users = LoadUsers()

    project_id = str(len(projects) + 1)
    leader_obj = next((user for user in users if user['username'] == leader), None)
    if not leader_obj:
        print("[red]Error! Leader username not found.[/red]")
        logging.error(f"Error! Leader username '{leader}' not found.")
        return

    new_project = {
        'ID': project_id,
        'Title': title,
        'Leader': leader,
        'Members': [],
        'Duties': []
    }
    projects.append(new_project)
    SaveProjects(projects)
    print("[green]Project created successfully![/green]")
    logging.info(f"Project '{title}' created with leader '{leader}'.")

def print_projects():
    projects = LoadProjects()
    console = Console()
    table = Table(title="Projects")

    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Leader", style="green")
    table.add_column("Members", style="yellow")

    for project in projects:
        member_names = ", ".join([member['username'] for member in project['Members']])
        table.add_row(
            project['ID'],
            project['Title'],
            project['Leader']['username'],
            member_names
        )

    console.print(table)

def create_duty(project_id, duty_id, title, detail, assignees_usernames):
    projects = LoadProjects()
    users = LoadUsers()

    project = next((proj for proj in projects if proj['ID'] == project_id), None)
    if not project:
        print(f"[red]Error! Project with ID '{project_id}' not found.[/red]")
        return

    assignees = [User(user['username'], user['password'], user['emailaddress']) for user in users if user['username'] in assignees_usernames]

    if len(assignees) != len(assignees_usernames):
        print("[red]Error! One or more assignees not found.[/red]")
        return

    if any(duty['ID'] == duty_id for duty in project['Duties']):
        print(f"[red]Error! Duty with ID '{duty_id}' already exists in project '{project_id}'.[/red]")
        return

    new_duty = Duty(duty_id, title, detail, assignees)
    project['Duties'].append({
        'ID': new_duty.get_ID(),
        'Title': new_duty.get_title(),
        'Detail': new_duty.get_detail(),
        'StartTime': new_duty.get_st().strftime("%Y-%m-%d %H:%M:%S"),
        'FinishTime': new_duty.get_ft().strftime("%Y-%m-%d %H:%M:%S"),
        'Priority': new_duty.get_priority().value,
        'Status': new_duty.get_status().value,
        'Assignees': [assignee.to_dict() for assignee in new_duty.get_assignees()],
        'AssignedTo': new_duty.get_assigned_to().to_dict() if new_duty.get_assigned_to() else None
    })
    SaveProjects(projects)
    print("[green]Duty created successfully![/green]")

def list_projects():
    projects = LoadProjects()
    console = Console()
    table = Table(title="Projects List")

    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Leader", style="green")

    for project in projects:
        table.add_row(project['ID'], project['Title'], project['Leader'])

    console.print(table)

def list_users():
    users = LoadUsers()
    console = Console()
    table = Table(title="Users List")

    table.add_column("Username", style="cyan")
    table.add_column("Email Address", style="magenta")
    table.add_column("Role", style="green")

    for user in users:
        table.add_row(user['username'], user['emailaddress'], user['role'])

    console.print(table)

#To add a member to a project
def add_member_to_project(project_id, username):
    projects = LoadProjects()
    users = LoadUsers()
   
    for project in projects:
        if project['ID'] == project_id:
            user_to_add = next((u for u in users if u['username'] == username), None)
            if not user_to_add:
                print(f"Error User '{username}' not found.")
                return
            if username in [member['username'] for member in project['Members']]:
                print("[red]Error User is already a member of this project.[/red]")
                return
            project['Members'].append(username)
            SaveProjects(projects)
            print(f"Member {username} added to project {project_id}.")
            return
    print(f"Error Project with ID '{project_id}' not found.")
    user_to_add = next((u for u in users if u['username'] == username), None)
    if not project:
        print("[red]Error! Project ID not found.[/red]")
        logging.error(f"Error! Project ID '{project_id}' not found.")
        return
    
    if not user_to_add:
        print(f"Error! User '{username}' not found.")
        logging.error(f"Error! Username '{username}' not found.")
        return
    if username in project['Members']:
        print("[red]Error! User is already a member of this project.[/red]")
        logging.error(f"Error! User '{username}' is already a member of project '{project['Title']}'.")
        return

    project['members'].append(username)
    print(f"Member {username} added to project {project_id}.")
    SaveProjects(projects)
    print("[green]Member added to project successfully![/green]")
    logging.info(f"User '{username}' added to project '{project['Title']}'.")

    for project in projects:
        if project['ID'] == project_id:
            if any(member['username'] == username for member in project['Members']):
                print(f"[bold white]Error! User '{username}' is already a member of the project![/bold white]")
                return
            project['Members'].append(user_to_add)
            SaveProjects(projects)
            print(f"User '{username}' added to project '{project['Title']}' successfully.")
            return

    print(f"Error! Project with ID '{project_id}' not found.")

#To remove a member from a project
def remove_member_from_project(project_id, username):
    projects = LoadProjects()
    project = next((proj for proj in projects if proj['ID'] == project_id), None)

    if not project:
        print("[red]Error! Project ID not found.[/red]")
        logging.error(f"Error! Project ID '{project_id}' not found.")
        return

    if username not in project['Members']:
        print("[red]Error! User is not a member of this project.[/red]")
        logging.error(f"Error! User '{username}' is not a member of project '{project['Title']}'.")
        return

    project['Members'].remove(username)
    SaveProjects(projects)
    print("[green]Member removed from project successfully![/green]")
    logging.info(f"User '{username}' removed from project '{project['Title']}'.")

def add_duty_to_project(project_id, duty_id, title, detail, assignees):
    projects = LoadProjects()
    users = LoadUsers()
    project = next((proj for proj in projects if proj['ID'] == project_id), None)

    if not project:
        print("[red]Error! Project ID not found.[/red]")
        logging.error(f"Error! Project ID '{project_id}' not found.")
        return

    for assignee in assignees:
        if assignee not in project['Members']:
            print(f"[red]Error! User '{assignee}' is not a member of this project.[/red]")
            logging.error(f"Error! User '{assignee}' is not a member of project '{project['Title']}'.")
            return

    new_duty = {
        'ID': duty_id,
        'Title': title,
        'Detail': detail,
        'Start Time': datetime.now().isoformat(),
        'End Time': (datetime.now() + timedelta(hours=24)).isoformat(),
        'Priority': 'LOW',
        'Status': 'BACKLOG',
        'Assignees': assignees,
        'Assigned To': None
    }
    project['Duties'].append(new_duty)
    SaveProjects(projects)
    print("[green]Duty added to project successfully![/green]")
    logging.info(f"Duty '{title}' added to project '{project['Title']}'.")

#To delete a project
def delete_project(project_id, username):
    projects = LoadProjects()

    for project in projects:
        if project['ID'] == project_id:
            if project['Leader'] !=username:
                print(f"[red]Error! Only the leader can delete the project.[/red]")
                return
            projects.remove(project)
            SaveProjects(projects)
            print(f"[green]Project with ID '{project_id}' deleted successfully.[/green]")
            return
    print(f"[red]Error! Project with ID '{project_id}' not found.[/red]")

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
            for duty in project['Duties']:
                if duty['ID'] == duty_id:
                    duty['AssignedTo'] = None
                    SaveProjects(projects)
                    print(f"[green]Duty '{duty_id}' unassigned successfully.[/green]")
                    return
    print(f"[red]Error! Project with ID '{project_id}' or duty with ID '{duty_id}' not found.[/red]")

#New function to list duties of a project for a member
def list_project_duties(project_id):
    projects = LoadProjects()
    project = next((proj for proj in projects if proj['ID'] == project_id), None)

    if not project:
        print("[red]Error! Project ID not found.[/red]")
        logging.error(f"Error! Project ID '{project_id}' not found.")
        return

    console = Console()
    table = Table(title=f"Project Duties - {project['Title']}")

    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Detail", style="green")
    table.add_column("Start Time", justify="center", style="yellow")
    table.add_column("End Time", justify="center", style="yellow")
    table.add_column("Status", justify="center", style="red")
    table.add_column("Priority", justify="center", style="red")

    for duty in project['Duties']:
        table.add_row(
            duty['ID'],
            duty['Title'],
            duty['Detail'],
            duty['Start Time'],
            duty['End Time'],
            duty['Status'],
            duty['Priority']
        )

    console.print(table)

def assign_duty_to_user(project_id, duty_id, username):
    projects = LoadProjects()
    users = LoadUsers()
    project = next((proj for proj in projects if proj['ID'] == project_id), None)
    user = next((usr for usr in users if usr['username'] == username), None)

    if not project:
        print("[red]Error! Project ID not found.[/red]")
        logging.error(f"Error! Project ID '{project_id}' not found.")
        return

    if not user:
        print("[red]Error! Username not found.[/red]")
        logging.error(f"Error! Username '{username}' not found.")
        return

    duty = next((dty for dty in project['Duties'] if dty['ID'] == duty_id), None)

    if not duty:
        print("[red]Error! Duty ID not found.[/red]")
        logging.error(f"Error! Duty ID '{duty_id}' not found in project '{project['Title']}'.")
        return

    if username not in project['Members']:
        print(f"[red]Error! User '{username}' is not a member of this project.[/red]")
        logging.error(f"Error! User '{username}' is not a member of project '{project['Title']}'.")
        return

    duty['Assigned To'] = username
    SaveProjects(projects)
    print("[green]Duty assigned to user successfully![/green]")
    logging.info(f"Duty '{duty['Title']}' assigned to user '{username}' in project '{project['Title']}'.")

def unassign_duty_from_user(project_id, duty_id):
    projects = LoadProjects()
    project = next((proj for proj in projects if proj['ID'] == project_id), None)

    if not project:
        print("[red]Error! Project ID not found.[/red]")
        logging.error(f"Error! Project ID '{project_id}' not found.")
        return

    duty = next((dty for dty in project['Duties'] if dty['ID'] == duty_id), None)

    if not duty:
        print("[red]Error! Duty ID not found.[/red]")
        logging.error(f"Error! Duty ID '{duty_id}' not found in project '{project['Title']}'.")
        return

    duty['Assigned To'] = None
    SaveProjects(projects)
    print("[green]Duty unassigned successfully![/green]")
    logging.info(f"Duty '{duty['Title']}' unassigned in project '{project['Title']}'.")

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

# To create Duty
def create_duty_in_project(project_id, duty_id, title, detail, assignees_usernames):
    projects = LoadProjects()
    users = LoadUsers()

    project = next((proj for proj in projects if proj['ID'] == project_id), None)
    if not project:
        print(f"[red]Error! Project with ID '{project_id}' not found.[/red]")
        return

    assignees = [User(user['username'], user['password'], user['emailaddress']) for user in users if user['username'] in assignees_usernames]

    if len(assignees) != len(assignees_usernames):
        print("[red]Error! One or more assignees not found.[/red]")
        return

    if any(duty['ID'] == duty_id for duty in project['Duties']):
        print(f"[red]Error! Duty with ID '{duty_id}' already exists in project '{project_id}'.[/red]")
        return

    new_duty = Duty(duty_id, title, detail, assignees)
    project['Duties'].append({
        'ID': new_duty.get_ID(),
        'Title': new_duty.get_title(),
        'Detail': new_duty.get_detail(),
        'StartTime': new_duty.get_st().strftime("%Y-%m-%d %H:%M:%S"),
        'FinishTime': new_duty.get_ft().strftime("%Y-%m-%d %H:%M:%S"),
        'Priority': new_duty.get_priority().value,
        'Status': new_duty.get_status().value,
        'Assignees': [assignee.to_dict() for assignee in new_duty.get_assignees()],
        'AssignedTo': new_duty.get_assigned_to().to_dict() if new_duty.get_assigned_to() else None
    })
    SaveProjects(projects)
    print("[green]Duty created successfully![/green]")

def user_menu():
    console = Console()
    console.print("[bold white]Welcome to the Project Management System![/bold white]")
    console.print("[bold magenta]--- Menu ---[/bold magenta]")
    console.print("1. Create an account")
    console.print("2. Log in")
    console.print("3. Exit")

    name = Prompt.ask("[bold yellow]Enter your choice[/bold yellow]")
    return name

def project_menu():
    console = Console()
    console.print("[bold magenta]--- Project Menu ---[/bold magenta]")
    console.print("1. Create project")
    console.print("2. List my projects")
    console.print("3. Exit")

    name = Prompt.ask("[bold yellow]Enter your choice[/bold yellow]")
    return name

def project_information():
    console = Console()
    console.print("[bold magenta]--- Project Information ---[/bold magenta]")
    console.print("1. Add member")
    console.print("2. Delete member")
    console.print("3. Create duty")
    console.print("4. Assignment of duties")
    console.print("5. Unassignment of duties")
    console.print("6. Update duty details")
    console.print("7. Delete Project")
    console.print("8. Exit")

    name = Prompt.ask("[bold yellow]Enter your choice[/bold yellow]")
    return name

def main():
    while True:
        name = user_menu()
        if name == '1':
            username = Prompt.ask("Enter username: ")
            while True:
                email = input("Enter email: ")
                if validate_email(email):
                    print("[bold green]Email is valid.[/bold green]")
                    break
                else:
                    print("[red]Email is not valid.[/red]")
            password = input("Enter password: ")
            create_an_account(username, email, password)
        elif name == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            logged_in_user = login_user(username, password)
            if logged_in_user:
                print(f"[green]Welcome, {logged_in_user.get_username()}![/green]")

                while True:
                    choice2 = project_menu()
                    if choice2 == '1':
                        ID = input("Enter the project ID: ")
                        Title = input("Enter the title of the project: ")
                        create_project(ID, Title, username.get_username())
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
                                title = input("Enter the title of the duty: ")
                                detail = input("Enter the detail of the duty: ")
                                assignees_usernames = input("Enter the usernames of assignees : ").split(',')
                                create_duty_in_project(project_id, duty_id, title, detail, assignees_usernames)
                            elif choice3 == '4':
                                project_id = input("Enter the project ID: ")
                                duty_id = input("Enter the duty ID: ")
                                assignee_username = input("Enter username: ")
                                assign_duty_to_member(project_id, duty_id, assignee_username)
                            elif choice3 == '5':
                                project_id = input("Enter the project ID: ")
                                duty_id = input("Enter the duty ID: ")
                                unassign_duty_from_member(project_id, duty_id)
                            elif choice3 == '6':
                                project_id = input("Enter the project ID: ")
                                duty_id = input("Enter the duty ID: ")

                                update_fields = {}
                                update_title = input("Enter new title (or leave blank to keep current): ")
                                if update_title:
                                    update_fields['title'] = update_title

                                update_detail = input("Enter new detail (or leave blank to keep current): ")
                                if update_detail:
                                    update_fields['detail'] = update_detail

                                update_st = input("Enter new start time (YYYY-MM-DD , HH:MM:SS) (or leave blank to keep current): ")
                                if update_st:
                                    update_fields['st'] = datetime.fromisoformat(update_st)

                                update_ft = input("Enter new finish time (YYYY-MM-DD , HH:MM:SS) (or leave blank to keep current): ")
                                if update_ft:
                                    update_fields['ft'] = datetime.fromisoformat(update_ft)

                                update_priority = input("Enter new priority (CRITICAL/HIGH/MEDIUM/LOW) (or leave blank to keep current): ")
                                if update_priority:
                                    update_fields['priority'] = Priority[update_priority.upper()]

                                update_status = input("Enter new status (BACKLOG/TODO/DOING/DONE/ARCHIVED) (or leave blank to keep current): ")
                                if update_status:
                                    update_fields['status'] = Status[update_status.upper()]

                                update_duty_details(logged_in_user, project_id, duty_id, **update_fields)
                            elif choice3 == '7':
                                project_id = input("Enter the project ID: ")
                                delete_project(project_id, logged_in_user.get_username())
                            elif choice3 == '8':
                                print("[bold red]Exiting the program...[/bold red]")
                                break
                            else:
                                print("Please try between 1 to 8.")
                    elif choice2 == '3':
                        print("Exiting the project menu :)")
                        break
                    else:
                        print("Invalid choice! Please try again.")
        elif name == '3':
            print("[red]Exiting the program...   Goodbye[/red]")
            break
        else:
            print("[bold red]Please choose between 1 to 3![/bold red]")

def convert_to_isoformat(date_str):
    try:
        date_str = date_str.replace(' , ', 'T')  # Replace comma with 'T'
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"Invalid isoformat string: '{date_str}'")

if __name__ == "__main__":
    main()
