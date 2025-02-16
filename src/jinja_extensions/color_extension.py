from jinja2.ext import Extension

class ColorExtension(Extension):
    def __init__(self, environment):
        super(ColorExtension, self).__init__(environment)

        # add the filter to jinja environment
        environment.filters['colorize'] = self.colorize_filter

    def colorize_filter(self, value):
        # list of color classes
        colors = ["bg-blue-100   dark:bg-blue-950   text-blue-800   dark:text-blue-300   ",
                  "bg-green-100  dark:bg-green-950  text-green-800  dark:text-green-300  ",
                  "bg-yellow-100 dark:bg-yellow-950 text-yellow-800 dark:text-yellow-300 ",
                  "bg-red-100    dark:bg-red-950    text-red-800    dark:text-red-300    ",
                  "bg-purple-100 dark:bg-purple-950 text-purple-800 dark:text-purple-300 ",
                  "bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 ",
                  "bg-pink-100   dark:bg-pink-950   text-pink-800   dark:text-pink-300   ",
                  #"bg-zinc-100   dark:bg-zinc-950   text-zinc-800   ",
                  ]

        # choose a color based on the hash of the value
        color_class = colors[hash(value) % len(colors)]
        return color_class
