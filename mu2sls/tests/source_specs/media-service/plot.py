from compiler import decorators

##
## This is a backend service that holds movie plots
##

@decorators.service
class Plot(object):
    def __init__(self):
        self.plots = {} # type: Persistent[dict]

    def write_plot(self, plot_id, plot):
        self.plots.update([(plot_id, plot)])

    def read_plot(self, plot_id):
        return self.plots.get(plot_id)
