from jinja2 import Template


def processFile(filename, variables):
	with open(filename, 'r') as stream:
		data = stream.read()
		t = Template(data)
		return t.render(variables)