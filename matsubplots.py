import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import Grid, ImageGrid


def grid(shape=1, size=3, pad=0, close=False, image_grid=False, return_grid=False, **kwargs):
    """Extend mpl_toolkits.axes_grid1.Grid."""
    if np.isscalar(shape):
        shape = shape, 1
    if np.isscalar(size):
        size = np.repeat(size, 2)
    if np.isscalar(pad):
        pad = np.repeat(pad, 2)
    xticks = kwargs.pop('xticks', None)
    yticks = kwargs.pop('yticks', None)
    frameon = kwargs.pop('frameon', None)
    if image_grid:
        kwargs.setdefault('cbar_pad', pad[0])
        kwargs.setdefault('cbar_size', size[0] * 0.1)
        if kwargs.get('cbar_mode') == 'each':
            size = size[0] + kwargs.get('cbar_pad') + kwargs.get('cbar_size'), size[1]
    figsize = [size[x] * shape[x] + pad[x] * (shape[x] + 1) for x in range(2)]
    if image_grid:
        if kwargs.get('cbar_mode') in ('edge', 'single'):
            figsize = figsize[0] + kwargs.get('cbar_pad') + kwargs.get('cbar_size'), figsize[1]
    fig = plt.figure(figsize=figsize)
    if close:
        plt.close(fig)
    padr = [pad[x] / figsize[x] for x in range(2)]
    rect = padr[0], padr[1], 1 - padr[0] * 2, 1 - padr[1] * 2
    grid = (ImageGrid if image_grid else Grid)(fig, rect, shape[::-1], axes_pad=pad, **kwargs)
    axs = np.asarray(grid.axes_row)
    for ax in axs.ravel():
        if xticks is not None:
            ax.set_xticks(xticks)
        if yticks is not None:
            ax.set_yticks(yticks)
        if frameon is not None:
            ax.set_frame_on(frameon)
    returned = fig, axs
    if return_grid:
        returned += grid,
    return returned


def imagegrid(*args, **kwargs):
    """Extend mpl_toolkits.axes_grid1.ImageGrid."""
    kwargs['image_grid'] = True
    kwargs.setdefault('xticks', ())
    kwargs.setdefault('yticks', ())
    return grid(*args, **kwargs)


def orthoview(axs, image, spacing=(1,1,1), xyz=None, ijk=None, slab_thickness=None, slab_func=np.mean, **kwargs):
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


def subplots(shape=1, size=3, pad=0, close=False, label_mode='L', squeeze=True, **kwargs):
    """Extend matplotlib.pyplot.subplots."""
    if np.isscalar(shape):
        shape = shape, 1
    if np.isscalar(size):
        size = np.repeat(size, 2)
    if np.isscalar(pad):
        pad = np.repeat(pad, 2)
    cbar_mode = kwargs.pop('cbar_mode', None)
    cbar_size = kwargs.pop('cbar_size', size[0] * 0.1)
    if cbar_mode == 'single':
        shape = shape[0] + 1, shape[1]
    figsize = [size[x] * shape[x] + pad[x] * (shape[x] + 1) for x in range(2)]
    fig = plt.figure(figsize=figsize)
    if close:
        plt.close(fig)
    axs = np.empty(shape[::-1], dtype=np.object)
    for i in range(shape[0]):
        for j in range(shape[1]):
            offset = [pad[x] + (i,j)[x] * (size[x] + pad[x]) for x in range(2)]
            axs[j,i] = _add_axes_inches(fig, size, offset, origin='top left', **kwargs)
    if label_mode == 'L':
        for ax in axs[:-1,:].ravel():
            ax.set_xticklabels(())
        for ax in axs[:,1:].ravel():
            ax.set_yticklabels(())
    elif label_mode:
        raise NotImplementedError(label_mode)
    if cbar_mode == 'single':
        axs, cax = axs[:,:-1], axs[0,-1]
        for ax in axs.ravel():
            ax.cax = cax
        cax.set_position([cbar_size / figsize[0] if i == 2 else x for i, x in enumerate(cax.get_position().bounds)])
    elif cbar_mode:
        raise NotImplementedError(cbar_mode)
    if squeeze:
        axs = axs[0,0] if axs.size == 1 else np.squeeze(axs)
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
