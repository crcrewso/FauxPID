
import numpy as np
import pydicom
import matplotlib.pyplot as plt
from numpy.fft import fft2, fftshift

def load_epid(dcm_path):
    ds = pydicom.dcmread(dcm_path)
    image = ds.pixel_array.astype(np.float64)
    # Apply rescale if present
    slope = getattr(ds, 'RescaleSlope', 1)
    intercept = getattr(ds, 'RescaleIntercept', 0)
    return image * slope + intercept


def measure_nps(image, roi_size=256, pixel_size_mm=0.336):
    """
    image       : 2D float array (1190x1190)
    roi_size    : size of square ROIs in pixels
    pixel_size_mm: physical pixel pitch in mm (check your EPID specs)
    """
    H, W = image.shape
    nps_accum = np.zeros((roi_size, roi_size))
    count = 0

    for y in range(0, H - roi_size, roi_size // 2):      # 50% overlap
        for x in range(0, W - roi_size, roi_size // 2):
            roi = image[y:y+roi_size, x:x+roi_size]

            # Detrend: subtract 2D plane fit to remove shading
            roi = detrend_roi(roi)

            # Windowing (reduces spectral leakage)
            window = np.outer(np.hanning(roi_size), np.hanning(roi_size))
            roi_w = roi * window

            # FFT and accumulate power
            F = fft2(roi_w)
            nps_accum += np.abs(fftshift(F))**2
            count += 1

    # Normalize
    nps_2d = nps_accum / count
    nps_2d *= (pixel_size_mm**2) / (roi_size**2)

    return nps_2d

def detrend_roi(roi):
    """Subtract a fitted 2D plane from a ROI."""
    n = roi.shape[0]
    x, y = np.meshgrid(np.arange(n), np.arange(n))
    A = np.column_stack([x.ravel(), y.ravel(), np.ones(n*n)])
    coeffs, _, _, _ = np.linalg.lstsq(A, roi.ravel(), rcond=None)
    plane = (A @ coeffs).reshape(n, n)
    return roi - plane

def radial_average_nps(nps_2d, pixel_size_mm):
    n = nps_2d.shape[0]
    center = n // 2
    y, x = np.indices(nps_2d.shape)
    r = np.sqrt((x - center)**2 + (y - center)**2).astype(int)

    # Spatial frequency axis
    df = 1.0 / (n * pixel_size_mm)   # cycles/mm per bin
    freq = np.arange(0, r.max()+1) * df

    nps_1d = np.array([nps_2d[r == i].mean() for i in range(r.max()+1)])
    return freq, nps_1d
def simulate_noise(nps_2d, image_shape=(1190, 1190)):
    """
    Generates a noise realization matching the spatial correlation of nps_2d.
    nps_2d should be fftshift-ed (DC at center) — we shift back before use.
    """
    from scipy.ndimage import zoom

    # Resize NPS to match full image if needed
    scale = image_shape[0] / nps_2d.shape[0]
    if scale != 1.0:
        nps_full = zoom(nps_2d, scale, order=1)
        nps_full = np.clip(nps_full, 0, None)
    else:
        nps_full = nps_2d.copy()

    # Shift DC back to corner for ifft2
    nps_ifft = np.fft.ifftshift(nps_full)

    # White noise in frequency domain
    white = fft2(np.random.randn(*image_shape))

    # Shape by sqrt(NPS)
    shaped = white * np.sqrt(nps_ifft)

    # Back to image space
    noise = np.fft.ifft2(shaped).real
    return noise

def add_noise_to_epid(clean_image, nps_2d, scale=1.0):
    noise = simulate_noise(nps_2d, image_shape=clean_image.shape)
    # scale lets you tune noise magnitude if needed
    return clean_image + noise * scale

def plot_nps_comparison(real_image, simulated_noisy_image, roi_size=256, pixel_size_mm=0.336):
    nps_real = measure_nps(real_image, roi_size, pixel_size_mm)
    nps_sim  = measure_nps(simulated_noisy_image, roi_size, pixel_size_mm)

    freq_r, nps1d_r = radial_average_nps(nps_real, pixel_size_mm)
    freq_s, nps1d_s = radial_average_nps(nps_sim,  pixel_size_mm)

    plt.figure(figsize=(8, 4))
    plt.plot(freq_r, nps1d_r, label='Real EPID')
    plt.plot(freq_s, nps1d_s, label='Simulated', linestyle='--')
    plt.xlabel('Spatial frequency (cycles/mm)')
    plt.ylabel('NPS (mm²)')
    plt.legend()
    plt.title('NPS comparison')
    plt.xlim(0, 1/(2*pixel_size_mm))   # Nyquist limit
    plt.tight_layout()
    plt.show()

sim_image = load_epid("test_images\cax_offset_10_mm_10x10.dcm")
real_image = load_epid("test_images\Solstice-m12_d18_2025-FS_EPID_Jaw 10x10.dcm")
nps = measure_nps(real_image, roi_size=256, pixel_size_mm=0.336)
