# TeamFlow API Overview

## Core Architecture

This system is a **multi-tenant, role-based team collaboration API** ie a single user can belong to multiple teams, each with their own isolated data and role hierarchy.

The architecture is built around four primary domains that each own their own data and rules. These domains communicate through well-defined relationships, never directly reaching into each other's internal logic.

The domains are user, team, membership and tasks.
