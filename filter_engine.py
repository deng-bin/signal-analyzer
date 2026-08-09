"""滤波器设计引擎 v2.0 — FIR/IIR + 滤波器组 + 实时滤波"""
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple, List


@dataclass
class FilterResult:
    name: str
    b: np.ndarray
    a: np.ndarray
    order: int
    filter_type: str
    design_method: str
    cutoff_info: str
    freq: np.ndarray = None
    mag: np.ndarray = None
    phase: np.ndarray = None
    zeros: np.ndarray = None
    poles: np.ndarray = None
    group_delay: np.ndarray = None
    gd_freq: np.ndarray = None
    params: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.freq is None:
            self._compute_response()

    def _compute_response(self):
        from scipy.signal import freqz, group_delay
        w, h = freqz(self.b, self.a, worN=2048)
        self.freq = w / np.pi * 500
        self.mag = 20 * np.log10(np.abs(h) + 1e-15)
        self.phase = np.unwrap(np.angle(h))
        self.zeros = np.roots(self.b)
        self.poles = np.roots(self.a)
        try:
            self.gd_freq, self.group_delay = group_delay((self.b, self.a), worN=2048)
        except Exception:
            self.gd_freq, self.group_delay = None, None

    def apply(self, signal) -> "Signal":
        from scipy.signal import lfilter, filtfilt
        from signal_engine import Signal
        y = lfilter(self.b, self.a, signal.y)
        return Signal(name=f"filtered({signal.name})", t=signal.t.copy(), y=y,
                      fs=signal.fs, signal_type=signal.signal_type,
                      params={"filter": self.name})

    def apply_filtfilt(self, signal) -> "Signal":
        """零相位滤波"""
        from scipy.signal import filtfilt
        from signal_engine import Signal
        y = filtfilt(self.b, self.a, signal.y)
        return Signal(name=f"filtfilt({signal.name})", t=signal.t.copy(), y=y,
                      fs=signal.fs, signal_type=signal.signal_type)

    def impulse_response(self, n=100):
        from scipy.signal import lfilter
        imp = np.zeros(n)
        imp[0] = 1.0
        return np.arange(n), lfilter(self.b, self.a, imp)

    def step_response(self, n=100):
        from scipy.signal import lfilter
        return np.arange(n), lfilter(self.b, self.a, np.ones(n))


class FIRFilter:
    """FIR 滤波器设计 — 窗函数 + Remez"""

    WINDOWS = ['hamming', 'hann', 'blackman', 'bartlett', 'kaiser', 'rectangular',
               'flattop', 'nuttall', 'barthann', 'lanczos', 'tukey', 'chebwin']

    @staticmethod
    def window_method(cutoff, fs, numtaps=101, window='hamming', pass_zero=True) -> FilterResult:
        from scipy.signal import firwin
        nyq = fs / 2
        cutoff_norm = cutoff / nyq if isinstance(cutoff, (int, float)) else [c/nyq for c in cutoff]
        if window == 'kaiser':
            w = ('kaiser', 14)
        elif window == 'chebwin':
            w = ('chebwin', 60)
        elif window == 'tukey':
            w = ('tukey', 0.5)
        else:
            w = window
        b = firwin(numtaps, cutoff_norm, window=w, pass_zero=pass_zero)
        return FilterResult(
            name=f"FIR_{window}(fc={cutoff}Hz)", b=b, a=[1.0], order=numtaps-1,
            filter_type="FIR", design_method=f"窗函数法({window})",
            cutoff_info=f"截止={cutoff}Hz, 阶数={numtaps-1}",
            params={"cutoff": cutoff, "fs": fs, "numtaps": numtaps, "window": window}
        )

    @staticmethod
    def remez(bands, desired, fs, numtaps=101, weight=None) -> FilterResult:
        from scipy.signal import remez as scipy_remez
        nyq = fs / 2
        bands_norm = [b/nyq for b in bands]
        b = scipy_remez(numtaps, bands_norm, desired, weight=weight, fs=2)
        return FilterResult(
            name=f"FIR_Remez(N={numtaps-1})", b=b, a=[1.0], order=numtaps-1,
            filter_type="FIR", design_method="Parks-McClellan (Remez)",
            cutoff_info=f"频带={bands}, 阶数={numtaps-1}"
        )


class IIRFilter:
    """IIR 滤波器设计 — Butterworth, Chebyshev I/II, Elliptic, Bessel"""

    @staticmethod
    def butterworth(order, cutoff, fs, btype='lowpass') -> FilterResult:
        from scipy.signal import butter
        nyq = fs / 2
        b, a = butter(order, cutoff/nyq if isinstance(cutoff, (int, float))
                      else [c/nyq for c in cutoff], btype=btype)
        return FilterResult(
            name=f"Butter_{btype}(N={order})", b=b, a=a, order=order,
            filter_type="IIR", design_method="Butterworth",
            cutoff_info=f"截止={cutoff}Hz, 阶数={order}"
        )

    @staticmethod
    def chebyshev1(order, cutoff, rp, fs, btype='lowpass') -> FilterResult:
        from scipy.signal import cheby1
        nyq = fs / 2
        b, a = cheby1(order, rp, cutoff/nyq if isinstance(cutoff, (int, float))
                      else [c/nyq for c in cutoff], btype=btype)
        return FilterResult(
            name=f"ChebyI_{btype}(N={order})", b=b, a=a, order=order,
            filter_type="IIR", design_method=f"Chebyshev I (rp={rp}dB)",
            cutoff_info=f"截止={cutoff}Hz, 阶数={order}, 波纹={rp}dB"
        )

    @staticmethod
    def chebyshev2(order, cutoff, rs, fs, btype='lowpass') -> FilterResult:
        from scipy.signal import cheby2
        nyq = fs / 2
        b, a = cheby2(order, rs, cutoff/nyq if isinstance(cutoff, (int, float))
                      else [c/nyq for c in cutoff], btype=btype)
        return FilterResult(
            name=f"ChebyII_{btype}(N={order})", b=b, a=a, order=order,
            filter_type="IIR", design_method=f"Chebyshev II (rs={rs}dB)",
            cutoff_info=f"截止={cutoff}Hz, 阶数={order}, 阻带衰减={rs}dB"
        )

    @staticmethod
    def elliptic(order, cutoff, rp, rs, fs, btype='lowpass') -> FilterResult:
        from scipy.signal import ellip
        nyq = fs / 2
        b, a = ellip(order, rp, rs, cutoff/nyq if isinstance(cutoff, (int, float))
                     else [c/nyq for c in cutoff], btype=btype)
        return FilterResult(
            name=f"Elliptic_{btype}(N={order})", b=b, a=a, order=order,
            filter_type="IIR", design_method=f"Elliptic (rp={rp}dB,rs={rs}dB)",
            cutoff_info=f"截止={cutoff}Hz, 阶数={order}"
        )

    @staticmethod
    def bessel(order, cutoff, fs, btype='lowpass') -> FilterResult:
        from scipy.signal import bessel
        nyq = fs / 2
        b, a = bessel(order, cutoff/nyq if isinstance(cutoff, (int, float))
                      else [c/nyq for c in cutoff], btype=btype)
        return FilterResult(
            name=f"Bessel_{btype}(N={order})", b=b, a=a, order=order,
            filter_type="IIR", design_method="Bessel (线性相位)",
            cutoff_info=f"截止={cutoff}Hz, 阶数={order}"
        )

    @staticmethod
    def iirnotch(w0, Q, fs) -> FilterResult:
        from scipy.signal import iirnotch
        b, a = iirnotch(w0/fs*2, Q)
        return FilterResult(
            name=f"Notch({w0}Hz,Q={Q})", b=b, a=a, order=2,
            filter_type="IIR", design_method="Notch",
            cutoff_info=f"陷波={w0}Hz, Q={Q}"
        )

    @staticmethod
    def iirpeak(w0, Q, fs) -> FilterResult:
        from scipy.signal import iirpeak
        b, a = iirpeak(w0/fs*2, Q)
        return FilterResult(
            name=f"Peak({w0}Hz,Q={Q})", b=b, a=a, order=2,
            filter_type="IIR", design_method="Peak",
            cutoff_info=f"峰值={w0}Hz, Q={Q}"
        )


class FilterBank:
    """滤波器组 — 倍频程/分数倍频程分析"""

    @staticmethod
    def octave_analysis(signal, n_bands=10, f_min=20, f_max=None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """倍频程分析"""
        from scipy.signal import butter, lfilter
        if f_max is None:
            f_max = signal.fs / 2.5
        f_centers = np.geomspace(f_min, f_max, n_bands)
        band_power = np.zeros(n_bands)
        for i, fc in enumerate(f_centers):
            f_low = fc / np.sqrt(2)
            f_high = fc * np.sqrt(2)
            b, a = butter(4, [f_low/(signal.fs/2), f_high/(signal.fs/2)], 'bandpass')
            filtered = lfilter(b, a, signal.y)
            band_power[i] = np.mean(filtered**2)
        return f_centers, 10*np.log10(band_power+1e-15), band_power
