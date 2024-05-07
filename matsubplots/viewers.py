import numpy as np
from matplotlib.backend_bases import MouseButton


def orthoview(*args, backend=None, **kwargs):
    if backend is None:
        return OrthoView(*args, **kwargs)
    elif backend.lower() == 'interactive':
        return OrthoViewInteractive(*args, **kwargs)
    elif backend.lower() == 'static':
        return OrthoViewStatic(*args, **kwargs)


class OrthoView:

    alignments = (0, 0), (0, 1), (1, 1)
    colors = '#ff0000', '#00ff00', '#ffff00'
    indices = (1, 2), (0, 2), (0, 1)

    def __init__(self, axs, image, spacing=(1,1,1), slab_thickness=None, slab_func=np.mean, reposition=True, **kwargs):
        axs = np.asarray(axs)
        image = np.asarray(image)
        spacing = np.asarray(spacing)
        if not (axs.size == image.ndim == spacing.size == 3):
            raise ValueError('Expected a 3D image, 3 axes, and 3 values for spacing')
        bounds = []
        for i, ax in enumerate(axs.ravel()):
            j = image.shape[i] // 2
            thickness = 1 if slab_thickness is None else round(slab_thickness / spacing[i])
            j0 = np.maximum(j - thickness // 2, 0)
            j1 = j - (-thickness // 2)
            slice_ = slab_func(np.rollaxis(image, i)[j0:j1], axis=0)
            aspect = np.divide(*spacing[::-1][np.arange(spacing.size) != i])
            bounds.append([])
            bounds[-1].append(ax.get_position().bounds)
            im = ax.imshow(slice_, aspect=aspect, **kwargs)
            bounds[-1].append(ax.get_position().bounds)
            if hasattr(ax, 'cax'):
                ax.get_figure().colorbar(im, cax=ax.cax)
        crosshairs = [[
            axs[i].axhline(image.shape[x]//2, lw=1, c=self.colors[x], visible=False),
            axs[i].axvline(image.shape[y]//2, lw=1, c=self.colors[y], visible=False)]
            for i, (x,y) in enumerate(self.indices)]
        self.axs = axs
        self.image = image
        self.spacing = spacing
        self._crosshairs = crosshairs
        if reposition:
            self._reposition(axs, bounds)

    def crosshairs(self, toggle=None):
        if toggle is None:
            toggle = not self._crosshairs[0][0].get_visible()
        default_color = self.axs[0].get_xaxis().get_label().get_color()
        for i, crosshairs in enumerate(self._crosshairs):
            for line in crosshairs:
                line.set_visible(toggle)
            for spine in self.axs[i].spines.values():
                spine.set_edgecolor(self.colors[i] if toggle else default_color)

    def ijk(self, i, j, k, crosshairs=None):
        for index, value in enumerate((i, j, k)):
            self._scroll(index, value)
        if crosshairs is not None:
            self.crosshairs(crosshairs)

    def xyz(self, x, y, z, crosshairs=None):
        xyz = x, y, z
        ijk = [round(xyz[::-1][i] / self.spacing[::-1][i] + (self.image.shape[i] - 1) / 2) for i in range(3)]
        self.ijk(*ijk, crosshairs=crosshairs)

    def _scroll(self, index, value):
        self.axs[index].images[0].set_data(np.rollaxis(self.image, index)[value])
        for i, alignment in zip(self.indices[index], self.alignments[index]):
            getattr(self._crosshairs[i][alignment], 'set_ydata' if alignment == 0 else 'set_xdata')([value, value])

    @staticmethod
    def _reposition(axs, bounds):
        _, _, w00, _ = bounds[0][0]
        l01, b01, w01, h01 = bounds[0][1]
        l0, b0, w0, h0 = l01, b01, w01, h01
        _, _, w10, _ = bounds[1][0]
        l11, b11, w11, h11 = bounds[1][1]
        l1, b1, w1, h1 = l11, b11, w11, h11
        _, _, w20, _ = bounds[2][0]
        l21, b21, w21, h21 = bounds[2][1]
        l2, b2, w2, h2 = l21, b21, w21, h21
        lshift = (w00 - w01) / 2
        lshift += (w10 - w11) / 2
        if w1 < w0:
            w0 = w1
            h0 *= w0 / w01
            b0 += (h01 - h0) / 2
            lshift += w01 - w0
            axs[0].set_position((l0, b0, w0, h0))
            axs[1].set_position((l1 - lshift, b1, w1, h1))
        else:
            w1 = w0
            h1 *= w1 / w11
            b1 += (h11 - h1) / 2
            axs[1].set_position((l1 - lshift, b1, w1, h1))
            lshift += w11 - w1
        lshift += (w10 - w11) / 2
        w2 *= h1 / h2
        h2 = h1
        b2 = b1
        lshift += (w20 - w21) / 2
        axs[2].set_position((l2 - lshift, b2, w2, h2))
        lshift += (w20 - w21) / 2
        lshift += w21 - w2
        if hasattr(axs[-1], 'cax'):
            cl, cb, cw, ch = axs[-1].cax.get_position().bounds
            ch2 = max(h0, h1, h2)
            cb2 = cb + (ch - ch2) / 2
            axs[-1].cax.set_position((cl - lshift, cb2, cw, ch2))


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
                self.crosshairs()
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
                    self._scroll(index, round(getattr(event, 'ydata' if j == 0 else 'xdata')))
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
        self.wcrosshairs = ipywidgets.Checkbox(description='crosshairs', value=self._crosshairs[0][0].get_visible())
        self.woutput = ipywidgets.Output()
        with self.woutput:
            display(axs[0].get_figure())

        @self.woutput.capture(clear_output=True, wait=True)
        def update(change):
            if change['owner'] is self.wclim:
                for ax in axs:
                    ax.images[0].set_clim(change['new'])
            elif change['owner'] is self.wcrosshairs:
                self.crosshairs(change['new'])
            elif change['owner'] in self.wslices:
                self._scroll(self.wslices.index(change['owner']), change['new'])
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
