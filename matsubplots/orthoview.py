import numpy as np


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
