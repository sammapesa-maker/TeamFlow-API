# TeamFlow API Overview

## Core Architecture

This system is a **multi-tenant, role-based team collaboration API** ie a single user can belong to multiple teams, each with their own isolated data and role hierarchy.

The architecture is built around four primary domains that each own their own data and rules. These domains communicate through well-defined relationships, never directly reaching into each other's internal logic.

The domains are user, team, membership and tasks.

## Core System Idea - Simplified

A backend system where:

- Users authenticate
- Users join teams
- Teams manage tasks
- System enforces permissions

---

## Core End to End flows

### USER AUTHENTICATION — FULL LIFECYCLE

---

### 1. **Register User** (COMPLETE)

- Receive email and password from the user
- Check if the email already exists in the system
- If the email exists:
  - Stop the process
  - Return an error: user already exists

- If the email does not exist:
  - Securely hash the password
  - Create a new user record with email and hashed password
  - Save the user in the database

- Return success confirming account creation

---

### 2. **Login User** (COMPLETE)

- Receive email and password
- Find a user with the given email
- If no user is found:
  - Stop the process
  - Return error: invalid credentials

- If user is found:
  - Compare the given password with the stored hashed password

- If the password is incorrect:
  - Stop the process
  - Return error: invalid credentials

- If the password is correct:
  - Generate an access token (short-lived)
  - Generate a refresh token (long-lived)
  - Return both tokens to the user

---

### 3. **Access Protected Route**

- Receive request with an access token
- Check if the token is present
- If no token:
  - Stop the process
  - Return error: unauthorized

- If token is present:
  - Decode the token

- If token is invalid or corrupted:
  - Stop the process
  - Return error: unauthorized

- If token is expired:
  - Stop the process
  - Return error: token expired

- If token is valid:
  - Extract user identity from the token
  - Allow the request to continue

---

### 4. **Get Current User (From Token)**

- Receive access token
- Decode the token
- Extract user ID
- Find user in database using the ID
- If user does not exist:
  - Stop the process
  - Return error: user not found

- If user exists:
  - Return user information

---

### 5. **Refresh Access Token** (COMPLETE)

- Receive refresh token
- Check if token is present
- If not present:
  - Stop the process
  - Return error

- Decode the refresh token
- If invalid or expired:
  - Stop the process
  - Return error

- If valid:
  - Extract user identity
  - Generate a new access and refresh tokens
  - Return new tokens

---

### 6. **Reject Unauthorized Access (Global Rule)**

This applies to every protected action:

- If no token is provided → reject
- If token is invalid → reject
- If token is expired → reject
- If user from token does not exist → reject

Only allow the request if all checks pass

---

### USER AUTHENTICATION LOGIC SUMMARY

- Register → create user if not exists
- Login → verify credentials and issue tokens
- Token → proves identity
- Protected routes → require valid token
- Refresh → issue new access token without login
- Logout → revoke access

> TASK: how to also disable access tokens in logout.

---

## Team Lifecycle — Full Algorithms (Plain English)

---

### 1. **Create Team**

- Receive request to create a team (team name + user)
- Check if the user is authenticated
- If not authenticated:
  - Stop the process
  - Return error

- If authenticated:
  - Create a new team record with the given name
  - Save the team in the database
  - Add the creator as a member of the team
  - Assign the creator the role of **admin**

- Return success with team details

---

### 2. **Add Member to Team**

- Receive request (admin user, team, target user to add)
- Check if the requesting user is authenticated
- If not:
  - Stop and return error

- Check if the team exists
- If not:
  - Stop and return error

- Check if the requesting user belongs to the team
- If not:
  - Stop and return error

- Check if the requesting user is an **admin** in that team
- If not:
  - Stop and return error (not allowed)

- Check if the target user exists
- If not:
  - Stop and return error

- Check if the target user is already in the team
- If yes:
  - Stop and return error (already a member)

- If all checks pass:
  - Add the target user to the team
  - Assign default role (**member**)

- Return success

---

### 3. **Get User's Teams**

- Receive request (user)
- Check if the user is authenticated
- If not:
  - Stop and return error

- Fetch all teams where the user is a member
- Return the list of teams

---

### 4. **Check Membership (Internal Rule Used Everywhere)**

- Receive user and team
- Check if a membership record exists linking the user to the team
- If it exists:
  - Return true

- If not:
  - Return false

---

### 5. **Check Admin Role (Internal Rule)**

- Receive user and team
- Find the membership record
- Check the role field
- If role is **admin**:
  - Return true

- Otherwise:
  - Return false

---

### 6. **Restrict Actions Based on Role**

Used in actions like adding members or assigning tasks:

- If user is not part of the team → reject
- If action requires admin and user is not admin → reject
- If all checks pass → allow action

---

### 7. **Leave Team (Optional but Logical)**

- Receive request (user, team)
- Check if user is authenticated
- If not:
  - Stop and return error

- Check if user is a member of the team
- If not:
  - Stop and return error

- Remove the user from the team
- Return success

---

### 8. **Prevent Invalid Team States (System Rules)**

- A user cannot be added twice to the same team
- Only admins can add new members
- Every team must have at least one admin
- Actions must always verify membership before proceeding

---

### TEAM LIFECYCLE LOGIC SUMMARY

- Teams are controlled spaces
- Membership defines access
- Roles define power
- Admins control team structure
- Every action checks:
  - Is user authenticated?
  - Is user in the team?
  - Is user allowed to do this?

---

## Task Lifecycle — Full Algorithms (Plain English)

---

### 1. **Create Task**

- Receive request (user, team, task details)
- Check if user is authenticated
- If not:
  - Stop and return error

- Check if the team exists
- If not:
  - Stop and return error

- Check if the user is a member of the team
- If not:
  - Stop and return error (not allowed)

- If all checks pass:
  - Create a new task linked to the team
  - Set initial status (e.g., **Pending**)
  - Save the task in the database

- Return success with task details

---

### 2. **Assign Task to User**

- Receive request (admin user, task, target user)
- Check if requesting user is authenticated
- If not:
  - Stop and return error

- Check if the task exists
- If not:
  - Stop and return error

- Check if the requesting user belongs to the task’s team
- If not:
  - Stop and return error

- Check if the requesting user is an **admin**
- If not:
  - Stop and return error (not allowed)

- Check if the target user exists
- If not:
  - Stop and return error

- Check if the target user is a member of the same team
- If not:
  - Stop and return error

- If all checks pass:
  - Assign the task to the target user
  - Save/update the task

- Return success

---

### 3. **Update Task Status**

- Receive request (user, task, new status)
- Check if user is authenticated
- If not:
  - Stop and return error

- Check if the task exists
- If not:
  - Stop and return error

- Check if the user belongs to the task’s team
- If not:
  - Stop and return error

- (Optional rule depending on system design)
  - If only assigned user or admin can update:
    - Check if user is assigned OR is admin
    - If not → stop and return error

- Validate the new status (e.g., Pending, In Progress, Done)
- If invalid:
  - Stop and return error

- If all checks pass:
  - Update the task status
  - Save the task

- Return success

---

### 4. **Get Tasks (Basic Fetch)**

- Receive request (user, team)
- Check if user is authenticated
- If not:
  - Stop and return error

- Check if the team exists
- If not:
  - Stop and return error

- Check if user is a member of the team
- If not:
  - Stop and return error

- Fetch all tasks linked to the team
- Return tasks

---

### 5. **Get Tasks with Pagination**

- Receive request (user, team, page, limit)
- Perform all checks (authentication + membership)
- If any fail:
  - Stop and return error

- Calculate how many tasks to skip based on page and limit
- Fetch only a limited number of tasks
- Return the subset of tasks

---

### 6. **Filter Tasks**

- Receive request (user, team, filters like status or assigned user)
- Perform all checks (authentication + membership)
- If any fail:
  - Stop and return error

- Apply filters:
  - If status filter exists → return only tasks with that status
  - If assigned user filter exists → return only tasks for that user

- Return filtered tasks

---

### 7. **Validate Task Actions (Core Rule Used Everywhere)**

Before any task operation:

- Check authentication
- Check team existence
- Check task existence
- Check user membership in team
- Check role if required (admin or assigned user)

If any check fails → stop immediately

---

### 8. **Prevent Invalid Task States (System Rules)**

- A task must always belong to a team
- A task can only be assigned to a user in that team
- Only authorized users can assign tasks
- Status must follow allowed values
- Unauthorized users cannot modify tasks

---

### TASK LIFECYCLE LOGIC SUMMARY

- Tasks live inside teams
- Only team members can interact with tasks
- Admins control assignment
- Status tracks progress
- Every action enforces:
  - Authentication
  - Membership
  - Permission

---

## System Complete (Logic View)

You now have:

- Authentication lifecycle
- Team lifecycle
- Task lifecycle

All expressed as:

- Step-by-step logic
- Clear decision flow
- Implementation-ready thinking
