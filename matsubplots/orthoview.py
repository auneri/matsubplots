import numpy as np
from matplotlib.backend_bases import MouseButton


def orthoview(axs, image, *args, backend=None, **kwargs):
    orthoview_base(axs, image, *args, **kwargs)
    if backend is None:
        pass
    elif backend.lower() == 'interactive':
        return OrthoViewInteractive(axs, image)
    elif backend.lower() == 'static':
        return OrthoViewStatic(axs, image)
    else:
        raise NotImplementedError(backend)


def orthoview_base(axs, image, spacing=(1,1,1), xyz=None, ijk=None, slab_thickness=None, slab_func=np.mean, **kwargs):
    axs = np.asarray(axs)
    image = np.asarray(image)
    spacing = np.asarray(spacing)
    if not (axs.size == image.ndim == spacing.size == 3):
        raise ValueError('Expected a 3D image, 3 axes, and 3 values for spacing')
    if ijk is not None and xyz is not None:
        raise ValueError('Cannot specify ijk and xyz at the same time')
    left = 0
    for i, ax in enumerate(axs.ravel()):
        if xyz is not None:
            j = round(xyz[::-1][i] / spacing[::-1][i] + (image.shape[i] - 1) / 2)
        elif ijk is not None:
            j = ijk[i]
        else:
            j = image.shape[i] // 2
        thickness = 1 if slab_thickness is None else round(slab_thickness / spacing[i])
        j0 = np.maximum(j - thickness // 2, 0)
        j1 = j - (-thickness // 2)
        slice_ = slab_func(np.rollaxis(image, i)[j0:j1], axis=0)
        aspect = np.divide(*spacing[::-1][np.arange(spacing.size) != i])
        bounds = ax.get_position().bounds
        width = bounds[2] * (slice_.shape[1] / slice_.shape[0]) / aspect
        ax.set_position((bounds[0] - left, bounds[1], width, bounds[3]))
        im = ax.imshow(slice_, aspect=aspect, **kwargs)
        left += bounds[2] - width
        if hasattr(ax, 'cax'):
            if ax is axs.ravel()[-1]:
                bounds = ax.cax.get_position().bounds
                ax.cax.set_position((bounds[0] - left, bounds[1], bounds[2], bounds[3]))
            ax.get_figure().colorbar(im, cax=ax.cax)


class OrthoView:

    alignments = (0, 0), (0, 1), (1, 1)
    colors = '#ff0000', '#00ff00', '#ffff00'
    indices = (1, 2), (0, 2), (0, 1)

    def __init__(self, axs, image):
        self.axs = axs
        self.image = image
        self.crosshairs = [[
            axs[i].axhline(image.shape[x]//2, lw=1, c=self.colors[x]),
            axs[i].axvline(image.shape[y]//2, lw=1, c=self.colors[y])]
            for i, (x,y) in enumerate(self.indices)]
        for x in self.crosshairs:
            for y in x:
                y.set_visible(False)

    def scroll(self, i, j, k):
        for index, value in enumerate((i, j, k)):
            self.scrolli(index, value)

    def scrolli(self, index, value):
        self.axs[index].images[0].set_data(np.rollaxis(self.image, index)[value])
        for i, alignment in zip(self.indices[index], self.alignments[index]):
            getattr(self.crosshairs[i][alignment], 'set_ydata' if alignment == 0 else 'set_xdata')([value, value])


class OrthoViewInteractive(OrthoView):

    def __init__(self, axs, *args, **kwargs):
        super().__init__(axs, *args, **kwargs)
        self.pressed = [None, None]
        self.signals = [
            axs[0].get_figure().canvas.mpl_connect('button_press_event', self.on_press),
            axs[0].get_figure().canvas.mpl_connect('button_release_event', self.on_release),
            axs[0].get_figure().canvas.mpl_connect('motion_notify_event', self.on_motion)]
        axs[0].get_figure().canvas.header_visible = False
        axs[0].get_figure().canvas.footer_visible = False

    def __del__(self):
        for signal in self.signals:
            self.axs[0].get_figure().canvas.mpl_disconnect(signal)

    def _ipython_display_(self):
        self.axs[0].get_figure().show()

    def on_press(self, event):
        if event.inaxes in self.axs:
            if event.dblclick:
                for x in self.crosshairs:
                    for y in x:
                        y.set_visible(not y.get_visible())
            elif event.button == MouseButton.LEFT:
                self.pressed[0] = event
            elif event.button == MouseButton.RIGHT:
                self.pressed[1] = event
        self.on_motion(event)

    def on_release(self, _):
        self.pressed[:] = None, None

    def on_motion(self, event):
        for i, ax in enumerate(self.axs):
            if self.pressed[0] is not None and event.inaxes is ax:
                for j, index in enumerate(self.indices[i]):
                    self.scrolli(index, round(getattr(event, 'ydata' if j == 0 else 'xdata')))
            elif self.pressed[1] is not None and event.inaxes is ax:
                vmin, vmax = self.axs[0].images[0].get_clim()
                win = vmax - vmin
                lvl = vmin + (win / 2)
                win += 0.1 * (event.x - self.pressed[1].x) / self.axs[0].images[0].get_size()[0]
                lvl += 0.1 * (event.y - self.pressed[1].y) / self.axs[0].images[0].get_size()[1]
                vmin = lvl - (win / 2)
                vmax = lvl + (win / 2)
                for ax in self.axs:
                    ax.images[0].set_clim((vmin, vmax))
        if any(x is not None for x in self.pressed) and event.inaxes in self.axs:
            self.axs[0].get_figure().canvas.draw_idle()


class OrthoViewStatic(OrthoView):

    def __init__(self, axs, image, *args, **kwargs):
        try:
            import ipywidgets
            from IPython.display import display
        except ModuleNotFoundError as exception:
            raise RuntimeError('ipywidgets is required to provide interactivity with static matplotlib backends') from exception
        super().__init__(axs, image, *args, **kwargs)
        self.wslices = [ipywidgets.IntSlider(description=x, value=image.shape[i]//2, min=0, max=image.shape[i]-1) for i, x in enumerate('ijk')]
        self.wclim = ipywidgets.FloatRangeSlider(description='clim', value=axs[0].images[0].get_clim(), min=np.min(image), max=np.max(image))
        self.wcrosshairs = ipywidgets.Checkbox(description='crosshairs', value=self.crosshairs[0][0].get_visible())
        self.woutput = ipywidgets.Output()
        with self.woutput:
            display(axs[0].get_figure())

        @self.woutput.capture(clear_output=True, wait=True)
        def update(change):
            if change['owner'] is self.wclim:
                for ax in axs:
                    ax.images[0].set_clim(change['new'])
            elif change['owner'] is self.wcrosshairs:
                for x in self.crosshairs:
                    for y in x:
                        y.set_visible(change['new'])
            elif change['owner'] in self.wslices:
                self.scrolli(self.wslices.index(change['owner']), change['new'])
            display(axs[0].get_figure())

        for widget in self.wslices + [self.wclim, self.wcrosshairs]:
            widget.observe(update, names='value')

    def _ipython_display_(self):
        from IPython.display import display
        display(self.widget())

    def scroll(self, i, j, k):
        for index, value in enumerate((i, j, k)):
            self.wslices[index].value = value

    def widget(self):
        import ipywidgets
        return ipywidgets.VBox((self.woutput, ipywidgets.HBox(self.wslices), ipywidgets.HBox((self.wclim, self.wcrosshairs))))
