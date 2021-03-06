from . import funcs
import numpy as np


def compute_squared_bp(channels):
    """Compute band power estimates by squaring channel values."""
    squared_channels = dict()
    for channel in channels:
        if channel == "Time":
            squared_channels[channel] = channels[channel][:]
            continue
        squared_channel = [x**2 for x in channels[channel]]
        squared_channels[channel] = squared_channel

    return squared_channels


def compute_fft(data, sampling_freq):
    """Compute real part of FFT and return only the side > 0."""
    y = np.fft.fft(data)
    freq = np.fft.fftfreq(len(data), 1.0/sampling_freq)
    a = next(x[0] for x in enumerate(freq) if x[1] > 0)
    b = next(x[0] for x in enumerate(freq) if x[1] < 0)
    return freq[a:b].tolist(), np.abs(y)[a:b].tolist()


def epoched_fft(channels, sampling_freq, channel, begin, end,
                width, interval=0):
    """Compute frequency spectrum for arbitrary length using epoching."""
    spectra = list()
    if interval == 0:
        interval = width

    for timestamp in np.arange(begin, end, interval):
        start = timestamp
        stop = timestamp+width
        freq, y = get_epoch_bp(channels, sampling_freq, channel, start, stop)
        spectra.append(y)

    y = [float(sum(val))/len(val) for val in zip(*spectra)]
    return freq, y


def get_epoch_bp(channels, sampling_freq, channel, begin, end):
    """Compute block FFT bandpower of selected epoch."""
    if begin > end:
        begin, end = end, begin
    epoch = funcs.get_epoch(channels, begin, end)
    freq, y = compute_fft(epoch[channel], sampling_freq)

    return freq, y


def get_epoched_bandpowers(channels, width=1):
    """Compute average band power per epoch from squared channel values."""
    # this one is fast and a bit inaccurate
    avgs = dict((channel, []) for channel in channels)
    p = 0
    n = 500
    na = 499
    end = len(channels["Time"]) - n
    while True:
        for channel in channels:
            s = sum(channels[channel][p+0:p+(n-1)])/na
            avgs[channel].append(s)
        p += n
        if p > end:
            break
    return avgs


def get_epoched_bandpowers_orig(channels, width=1):
    if "Time" in channels:
        index = "Time"
    elif "Freq" in channels:
        index = "Freq"
    else:
        logging.error("get_epoched_bandpowers_orig: error, no index (Time/Freq)")
        return

    result = dict((channel, []) for channel in channels)
    for second in np.arange(channels[index][0],
                            channels[index][-1],
                            width):
        epoch = funcs.get_epoch(channels, second, second+width)
        if len(epoch[index]) != 0:
            epoch_avg = funcs.get_channels_avgs(epoch)
            for channel in epoch_avg:
                result[channel].append(epoch_avg[channel])

    return result


def slice_freqs(data, low, high):
    """Find indices for desired range of freqs in FFT output."""
    if low > high:
        low, high = high, low

    it = (x[0] for x in enumerate(data) if (x[1] > low and x[1] < high))
    a = next(it)
    b = a
    for b in it:
        pass
    return a, b
