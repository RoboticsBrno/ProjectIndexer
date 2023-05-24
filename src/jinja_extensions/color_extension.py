from jinja2.ext import Extension

class ColorExtension(Extension):
    def __init__(self, environment):
        super(ColorExtension, self).__init__(environment)

        # add the filter to jinja environment
        environment.filters['colorize'] = self.colorize_filter

    def colorize_filter(self, value):
        # list of color classes
        colors = ["bg-blue-100 text-blue-800",
                  "bg-green-100 text-green-800",
                  "bg-yellow-100 text-yellow-800",
                  "bg-red-100 text-red-800",
                  "bg-purple-100 text-purple-800",
                  "bg-indigo-100 text-indigo-800",
                  "bg-pink-100 text-pink-800",
                  "bg-gray-100 text-gray-800"]

        # choose a color based on the hash of the value
        color_class = colors[hash(value) % len(colors)]
        return color_class
