import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import Grid, ImageGrid


def axesgrid(grid=1, size=3, pad=0, image=False, close=False, **kwargs):
    if np.isscalar(grid):
        grid = grid, 1
    if np.isscalar(size):
        size = np.repeat(size, 2)
    if np.isscalar(pad):
        pad = np.repeat(pad, 2)
    xticks = kwargs.pop('xticks', None)
    yticks = kwargs.pop('yticks', None)
    frameon = kwargs.pop('frameon', None)
    figsize = [size[x] * grid[x] + pad[x] * (grid[x] + 1) for x in range(2)]
    fig = plt.figure(figsize=figsize)
    if close:
        plt.close(fig)
    padr = [pad[x] / figsize[x] for x in range(2)]
    rect = padr[0], padr[1], 1 - padr[0] * 2, 1 - padr[1] * 2
    axs = (ImageGrid if image else Grid)(fig, rect, grid[::-1], axes_pad=pad, **kwargs)
    for ax in axs:
        if xticks is not None:
            ax.set_xticks(xticks)
        if yticks is not None:
            ax.set_yticks(yticks)
        if frameon is not None:
            ax.set_frame_on(frameon)
    return fig, axs


def imagegrid(*args, **kwargs):
    kwargs['image'] = True
    kwargs.setdefault('aspect', False)
    return axesgrid(*args, **kwargs)


def subplots(grid=1, size=3, pad=0, close=False, label_mode='L', **kwargs):
    ravel = np.isscalar(grid)
    if np.isscalar(grid):
        grid = grid, 1
    if np.isscalar(size):
        size = np.repeat(size, 2)
    if np.isscalar(pad):
        pad = np.repeat(pad, 2)
    figsize = [size[x] * grid[x] + pad[x] * (grid[x] + 1) for x in range(2)]
    fig = plt.figure(figsize=figsize)
    if close:
        plt.close(fig)
    axs = np.empty(grid[::-1], dtype=np.object)
    for i in range(grid[0]):
        for j in range(grid[1]):
            offset = [pad[x] + (i,j)[x] * (size[x] + pad[x]) for x in range(2)]
            axs[j,i] = _add_axes_inches(fig, size, offset, origin='top left', **kwargs)
    if label_mode == 'L':
        for ax in axs[:-1,:].ravel():
            ax.set_xticklabels(())
        for ax in axs[:,1:].ravel():
            ax.set_yticklabels(())
    else:
        raise NotImplementedError(label_mode)
    if ravel:
        axs = axs.ravel() if axs.size > 1 else axs[0,0]
    return fig, axs


def _add_axes_inches(fig, size, offset=0, origin='middle center', **kwargs):
    figsize = fig.get_size_inches()
    if np.isscalar(size):
        size = np.repeat(size, 2)
    elif len(size) != 2:
        raise NotImplementedError(size)
    if np.isscalar(offset):
        offset = np.repeat(offset, 2)
    elif len(offset) != 2:
        raise NotImplementedError(offset)
    origin = origin.split()
    if len(origin) != 2:
        raise NotImplementedError(origin)
    if origin[1] == 'left':
        left = offset[0]
    elif origin[1] == 'right':
        left = figsize[0] - size[0] - offset[0]
    elif origin[1] == 'center':
        left = (figsize[0] - size[0]) / 2 + offset[0]
    else:
        raise NotImplementedError(origin[1])
    if origin[0] == 'bottom':
        bottom = offset[1]
    elif origin[0] == 'top':
        bottom = figsize[1] - size[1] - offset[1]
    elif origin[0] == 'middle':
        bottom = (figsize[1] - size[1]) / 2 + offset[1]
    else:
        raise NotImplementedError(origin[0])
    width, height = size
    left /= figsize[0]
    bottom /= figsize[1]
    width /= figsize[0]
    height /= figsize[1]
    return fig.add_axes((left, bottom, width, height), **kwargs)
