import yaml
import os

allowedVariableFiles = ["yml", "yaml"]

def loadVariables(filename):
	print("Loading %s" % filename)
	with open(filename, 'r') as stream:
		try:
			return yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print(exc)


def loadVariableContext(config):
	if not "variableContext" in config:
		print("WARN: There is no variable context defined")
		return {}

	context = {}

	for r, d, f in os.walk(config["variableContext"]):
		#print("r: %s, d: %s, f: %s" % (r, d, f))
		for file in f:
			for extension in allowedVariableFiles:
				if ".%s" % extension in file:
					name = file.replace(".%s" % extension, "")
					context[name] = loadVariables(os.path.join(r, file))
					break

	return context