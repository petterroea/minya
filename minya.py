import argparse
import os
import yaml
import sys

parser = argparse.ArgumentParser(description="Tool templating a website with jinja")
parser.add_argument("--input", help="Input folder")
parser.add_argument("--output", help="Output folder")
parser.add_argument("--config", help="Config file")
parser.add_argument("--verbose", help="More verbose logging")
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

# Validate config

if not args.input:
	print("Lacks parameter --input, cannot continue")
	sys.exit(1)
if not args.output:
	print("Lacks parameter --output, cannot continue")
	sys.exit(1)

# Save config
if args.config is not None:
	if not os.path.exists(args.config):
		if args.verbose:
			print("Config file does not exist, saving...")
		with open(args.config, 'w') as outfile:
			yaml.dump(config, outfile, default_flow_style=False)