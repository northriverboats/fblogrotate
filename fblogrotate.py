#!/usr/bin/env python3

import click
from datetime import date,  datetime, timedelta
from dotenv import load_dotenv
# from emailer import mail_results as mail_results_original
import os
import sys
import traceback
import shutil

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_dirs(path):
    """ generator for list of directorise """
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            yield file

def build_dates(today,days_to_keep):
    """ build a liste of dates like '2023.05.28' to keep files from
        based on the last day of the month before inventory, plus 12 more days
        for 2 inventory periods plus the last 12 days
    """
    period = int((today.month  -1)/3)
    base = (
        (-1, 6, 30),
        (-1, 9, 30),
        (-1, 12, 31),
        (0, 3, 31),
        (0, 6, 30),
        (0, 9, 30),
    )

    date_groups = []
    for i in range(period, period+3):
        date_groups.append(datetime(
            year=today.year+base[i][0],
            month=base[i][1],
            day=base[i][2]))

    date_groups.append(today-timedelta(days=days_to_keep-1))

    all_dates = set()
    for day in date_groups:
        for j in range(0,days_to_keep):
            all_dates.add( (day + timedelta(days=j)).strftime("%Y.%m.%d") )

    return all_dates


def dry_run(path, dates):
    """ perform a dry run """
    print("Folders to keep ============================")
    for dir in get_dirs(path):
        if dir[:10] in dates:
            click.echo( os.path.join(path, dir) )

    click.echo()

    print("Folders to delete ============================")
    for dir in get_dirs(path):
        if not dir[:10] in dates:
            print( os.path.join(path, dir) )

def delete_folders(path, dates):
    """ delete folders and contents"""
    for dir in get_dirs(path):
        if not dir[:10] in dates:
            # shutil.rmtree( os.path.join(path, dir) )
            click.echo(os.path.join(path, dir))

@click.command()
@click.option('--force', '-f', is_flag=True,
              help="force files to be deleted")
def main(force):
    """
    Fish Bowl Log Rotate Utility

    If run with no parameters will print a list of files to keep and files
    to be deleted.

    To actually delete files this utility must be run with the --force option
    """
    # load environmental variables
    load_dotenv(dotenv_path=resource_path(".env"))
    path = os.environ.get('FOLDER', '/tmp')
    interval = int(os.environ.get('INTERVAL', 15))
    dates = sorted(build_dates( date.today(), interval))
    if force:
        delete_folders(path, dates)
    else:
        dry_run(path, dates)

if __name__ == "__main__":
   main()
