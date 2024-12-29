# PostgreSQL Migration Deployment Guide

## Pre-Migration Checklist

1. **Backup**
   - [ ] Take a backup of the production SQLite database (`instance/books.db`)
   - [ ] Store backup in a secure location

2. **PostgreSQL Setup**
   - [ ] Install PostgreSQL on the production server
   - [ ] Create a database user with appropriate permissions
   - [ ] Create the database
   - [ ] Test connection to the database

3. **Environment Configuration**
   - [ ] Update production `.env` file with PostgreSQL credentials:
     ```
     DATABASE_URL=postgresql://username:password@hostname:port/dbname
     ```
   - [ ] Remove or comment out the old `SQLITE_URL`
   - [ ] Ensure all other environment variables are correctly set

4. **Dependencies**
   - [ ] Install required packages:
     ```bash
     pip install psycopg2-binary SQLAlchemy Flask-SQLAlchemy
     ```

## Migration Steps

1. **Preparation**
   - [ ] Schedule downtime if needed
   - [ ] Notify users of maintenance window
   - [ ] Stop the production application

2. **Migration**
   - [ ] Copy the migration script to production server
   - [ ] Run the migration script:
     ```bash
     python migrate_to_postgres.py
     ```
   - [ ] Verify the migration output shows success
   - [ ] Check record counts match the source database

3. **Verification**
   - [ ] Start the application
   - [ ] Test core functionality:
     - [ ] User login
     - [ ] Book listing
     - [ ] Book search
     - [ ] Adding new books
     - [ ] Admin functionality
   - [ ] Monitor application logs for errors

## Rollback Plan

If issues are encountered:

1. **Stop the Application**
   - [ ] Stop the Flask application
   - [ ] Document any errors encountered

2. **Restore SQLite**
   - [ ] Restore the SQLite database from backup
   - [ ] Update `.env` to use SQLite
   - [ ] Restart the application

3. **Post-Rollback**
   - [ ] Notify team of rollback
   - [ ] Investigate migration issues
   - [ ] Plan new migration attempt

## Post-Migration

1. **Cleanup**
   - [ ] Archive SQLite database backup
   - [ ] Remove SQLite database file (after confirming successful migration)
   - [ ] Update application documentation

2. **Monitoring**
   - [ ] Monitor application performance
   - [ ] Watch for any database-related errors
   - [ ] Check database connection pool usage

3. **Documentation**
   - [ ] Update deployment documentation
   - [ ] Document any issues encountered and solutions
   - [ ] Update database backup procedures for PostgreSQL