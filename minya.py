import argparse
import os
import yaml
import sys

from shutil import copyfile

from internals.variables import loadVariableContext
from internals.templator import processFile

import time  
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler  

class ListenHandler(PatternMatchingEventHandler):
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True

    def __init__(self, config, variables):
    	self.config = config
    	self.variables = variables

    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print("%s, %s" % (event.src_path, event.event_type)) # print now only for degug

        walkSource(self.config, self.variables)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

def walkSource(config, variables):
	for r, d, f in os.walk(config["input"]):
		for file in f:
			fullPath = os.path.join(r, file)

			if "notemplate" in fullPath:
				continue
			
			relPath = os.path.relpath(fullPath, config["input"])

			destPath = os.path.join(config["output"], relPath)
			destDir = os.path.dirname(destPath)

			if not os.path.exists(destDir):
				os.makedirs(destDir)
			elif not os.path.isdir(destDir):
				print("%s is already a file, cannot create directory" % destDir)
				sys.exit(1)

			if ".jinja" in file:
				print("Checking %s" % fullPath)

				processed = processFile(fullPath, variables)

				with open(destPath.replace(".jinja", ""), 'w') as outfile:
					outfile.write(processed)
			else:
				copyfile(fullPath, destPath)

def main():
	parser = argparse.ArgumentParser(description="Tool templating a website with jinja")
	parser.add_argument("--input", help="Input folder")
	parser.add_argument("--output", help="Output folder")
	parser.add_argument("--config", help="Config file")
	parser.add_argument("--variableContext", help="Folder for extracting variables")
	parser.add_argument("--verbose", default=False, action='store_true', help="More verbose logging")
	parser.add_argument("--listen", default=False, action='store_true', help="More verbose logging")
	args = parser.parse_args()

	config = {}

	if args.config is not None:
		if os.path.exists(args.config):
			if args.verbose:
				print("Config file exists, loading...")
			with open(args.config, 'r') as stream:
				try:
					config = yaml.safe_load(stream)
					if not isinstance(config, dict):
						print("Invalid config file, was not dictionary")
						sys.exit(1)
				except yaml.YAMLError as exc:
					print(exc)

	if args.input:
		config["input"] = args.input

	if args.output:
		config["output"] = args.output

	if args.variableContext:
		config["variableContext"] = args.variableContext

	# Validate config

	requiredArgs = ["input", "output"]

	for argName in requiredArgs:
		if not getattr(args, argName):
			print("Lacks parameter --%s, cannot continue" % argName)
			sys.exit(1)	

	# Save config
	if args.config is not None:
		if not os.path.exists(args.config):
			if args.verbose:
				print("Config file does not exist, saving...")
			with open(args.config, 'w') as outfile:
				yaml.dump(config, outfile, default_flow_style=False)

	context = loadVariableContext(config)

	walkSource(config, context)

	if args.listen:
		observer = Observer()
		observer.schedule(ListenHandler(config, context), path=config["input"])
		observer.start()

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			observer.stop()

		observer.join()

if __name__ == "__main__": 
    main()