from jinja2 import Environment, FileSystemLoader


def processFile(filename, config, variables):
	with open(filename, 'r') as stream:
		data = stream.read()
		t = Environment(loader=FileSystemLoader(config["input"])).from_string(data)
		return t.render(variables)