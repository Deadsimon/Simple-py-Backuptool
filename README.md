#Simple-py-Backuptool


This is a simple python application for backing up your important files

current features:
application Watchdog
Quickrun backup
Scheduled - time stamped backups.
SQLlite database for tracking and recording backup results.
installer for easy use.


Future features:
database location definition moved to config.yml
small GUI application for reading database results.
Multi-instance(maybe)
automated backup sorter(organises backups,set deletion periods,maybe even add cloud options)


#build instructions
simply clone the github repo and open with pycharm.


#Readme = installer


Please goto the install directory and find Config.yml
to configure the backup tool.

install location: C:\Program Files\Deadsimon - Github\Simple-py-backer-upper

config location: C:\Program Files\Deadsimon - Github\Simple-py-backer-upper\config.yml

Config opitions:


output_folder: 			# This is the backup output location

folder_path: 			# This is the source location.

schedule_length_unit: minute #options - minute - hour - day

schedule_length_amount: 1 # whole numbers only
