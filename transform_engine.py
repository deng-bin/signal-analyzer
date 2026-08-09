"""变换引擎 v2.0 — FFT/DFT/STFT/CWT/Hilbert/Z/Cepstrum/Coherence + 符号变换"""
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
import sympy as sp


@dataclass
class TransformResult:
    name: str
    data_x: np.ndarray
    data_y: np.ndarray
    data_y2: Optional[np.ndarray] = None
    data_y3: Optional[np.ndarray] = None
    xlabel: str = "Frequency (Hz)"
    ylabel: str = "Magnitude"
    y2label: str = "Phase (rad)"
    y3label: str = ""
    extra: dict = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


class FourierTransform:
    """傅里叶变换族"""

    @staticmethod
    def fft(signal, n=None, window='none', detrend=False) -> TransformResult:
        """FFT with windowing and detrend"""
        y = signal.y.copy()
        if detrend:
            from scipy.signal import detrend as dt
            y = dt(y)
        n = n or len(y)
        if window != 'none':
            win_funcs = {
                'hamming': np.hamming, 'hann': np.hanning, 'blackman': np.blackman,
                'bartlett': np.bartlett, 'flattop': lambda n: np.kaiser(n, 0.5),
                'kaiser': lambda n: np.kaiser(n, 14)
            }
            w = win_funcs[window](min(len(y), n))
            y = y[:len(w)] * w
        Y = np.fft.fft(y, n=n)
        freqs = np.fft.fftfreq(n, d=1/signal.fs)
        half = n // 2
        mag = np.abs(Y[:half]) / n * 2
        mag[0] /= 2
        phase = np.angle(Y[:half])
        return TransformResult(
            name=f"FFT({signal.name})", data_x=freqs[:half],
            data_y=mag, data_y2=phase,
            xlabel="Frequency (Hz)", ylabel="Magnitude", y2label="Phase (rad)"
        )

    @staticmethod
    def ifft(magnitude, phase, fs=1000.0) -> np.ndarray:
        """逆 FFT"""
        Y = magnitude * np.exp(1j * phase)
        Y_full = np.concatenate([Y, np.conj(Y[-2:0:-1])])
        return np.fft.ifft(Y_full).real

    @staticmethod
    def dft(signal, N=None) -> TransformResult:
        """N 点 DFT"""
        y = signal.y
        N = N or len(y)
        y = y[:N] if len(y) >= N else np.pad(y, (0, N-len(y)))
        k = np.arange(N)
        n = k.reshape(-1, 1)
        Y = np.exp(-2j*np.pi*k*n/N) @ y
        freqs = np.arange(N) * signal.fs / N
        half = N // 2
        return TransformResult(
            name=f"DFT{N}({signal.name})",
            data_x=freqs[:half], data_y=np.abs(Y[:half])/N*2, data_y2=np.angle(Y[:half]),
            xlabel="Frequency (Hz)", ylabel="Magnitude", y2label="Phase (rad)"
        )

    @staticmethod
    def stft(signal, nperseg=256, noverlap=128, window='hann') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """短时傅里叶变换"""
        from scipy.signal import spectrogram
        f, t, Sxx = spectrogram(signal.y, fs=signal.fs,
                                nperseg=nperseg, noverlap=noverlap, window=window)
        return f, t, Sxx

    @staticmethod
    def power_spectrum(signal, method='periodogram') -> TransformResult:
        """功率谱密度估计"""
        from scipy.signal import periodogram, welch
        if method == 'welch':
            f, Pxx = welch(signal.y, fs=signal.fs, nperseg=256)
        else:
            f, Pxx = periodogram(signal.y, fs=signal.fs)
        return TransformResult(
            name=f"PSD({signal.name})", data_x=f, data_y=10*np.log10(Pxx+1e-15),
            xlabel="Frequency (Hz)", ylabel="Power/Freq (dB/Hz)"
        )

    @staticmethod
    def coherence(s1, s2, nperseg=256) -> TransformResult:
        """相干性估计"""
        from scipy.signal import coherence as coh
        f, Cxy = coh(s1.y, s2.y, fs=s1.fs, nperseg=nperseg)
        return TransformResult(
            name=f"Coherence({s1.name},{s2.name})",
            data_x=f, data_y=Cxy,
            xlabel="Frequency (Hz)", ylabel="Coherence γ²"
        )

    @staticmethod
    def cepstrum(signal) -> TransformResult:
        """倒谱分析"""
        Y = np.fft.fft(signal.y)
        log_spectrum = np.log(np.abs(Y) + 1e-15)
        ceps = np.fft.ifft(log_spectrum).real
        quefrency = np.arange(len(ceps)) / signal.fs
        return TransformResult(
            name=f"Cepstrum({signal.name})",
            data_x=quefrency[:len(quefrency)//2], data_y=ceps[:len(ceps)//2],
            xlabel="Quefrency (s)", ylabel="Amplitude"
        )

    # --- 符号 ---
    @staticmethod
    def symbolic_forward(expr_str: str) -> dict:
        t, omega = sp.symbols('t ω', real=True)
        try:
            f_expr = sp.sympify(expr_str, locals={
                "t": t, "sin": sp.sin, "cos": sp.cos, "exp": sp.exp,
                "Heaviside": sp.Heaviside, "DiracDelta": sp.DiracDelta, "pi": sp.pi
            })
            F = sp.fourier_transform(f_expr, t, omega)
            return {"input": sp.latex(f_expr), "result": sp.latex(sp.simplify(F)),
                    "raw": str(sp.simplify(F))}
        except Exception as e:
            return {"error": str(e)}


class HilbertTransform:
    """希尔伯特变换 — 包络、瞬时频率、瞬时相位"""

    @staticmethod
    def analytic_signal(signal) -> TransformResult:
        from scipy.signal import hilbert
        analytic = hilbert(signal.y)
        envelope = np.abs(analytic)
        phase = np.unwrap(np.angle(analytic))
        inst_freq = np.gradient(phase, signal.t) / (2 * np.pi)
        return TransformResult(
            name=f"Hilbert({signal.name})",
            data_x=signal.t, data_y=envelope, data_y2=phase, data_y3=inst_freq,
            xlabel="Time (s)", ylabel="Envelope", y2label="Phase (rad)",
            y3label="Inst. Freq (Hz)"
        )


class WaveletTransform:
    """连续小波变换 (CWT)"""

    # 可用小波映射: 优先 scipy.signal 小波, 否则用自定义实现
    _WAVELETS = {
        'morl': 'morlet',   # Morlet
        'ricker': 'ricker',  # Ricker (Mexican hat)
        'mexh': 'mexh',     # Mexican hat 别名
    }

    @staticmethod
    def cwt(signal, wavelet='morl', scales=None, n_scales=128) -> TransformResult:
        """
        连续小波变换。

        优先使用 scipy.signal.cwt (scipy < 1.15)，
        否则使用基于卷积的高效自定义实现。
        """
        if scales is None:
            scales = np.geomspace(1, max(signal.n_samples // 2, 2), n_scales)

        try:
            # scipy >= 1.6 提供 scipy.signal.cwt (scipy >= 1.15 已移除)
            cwt_matrix = WaveletTransform._scipy_cwt(signal, wavelet, scales)
        except Exception:
            cwt_matrix = WaveletTransform._manual_cwt(signal, scales)

        return TransformResult(
            name=f"CWT({signal.name})", data_x=signal.t,
            data_y=scales, data_y2=cwt_matrix,
            xlabel="Time (s)", ylabel="Scale",
            extra={"type": "cwt", "scales": scales}
        )

    @staticmethod
    def _scipy_cwt(signal, wavelet: str, scales: np.ndarray) -> np.ndarray:
        """使用 scipy.signal.cwt 计算（兼容旧版 scipy）"""
        from scipy.signal import cwt as scipy_cwt, ricker, morlet

        wavelet_map = {
            'morl': lambda: morlet,
            'ricker': lambda: ricker,
            'mexh': lambda: ricker,
        }
        wv = wavelet_map.get(wavelet, lambda: ricker)()
        widths = scales.astype(np.float64)
        return np.abs(scipy_cwt(signal.y, wv, widths))

    @staticmethod
    def _manual_cwt(signal, scales: np.ndarray) -> np.ndarray:
        """手动实现 Ricker 小波 CWT（卷积法，适用于 scipy >= 1.15）"""
        dt = signal.dt
        n = len(signal.y)
        cwt_matrix = np.zeros((len(scales), n))

        for i, scale in enumerate(scales):
            s = max(float(scale), 1.0)
            # Ricker (Mexican hat) wavelet: ψ(t) = 2/(√(3s)·π^1/4) · (1-(t/s)²) · exp(-t²/(2s²))
            tau = np.arange(-4 * s, 4 * s + dt, dt)
            wavelet_arr = (
                2 / (np.sqrt(3 * s) * np.pi ** 0.25)
                * (1 - (tau / s) ** 2)
                * np.exp(-tau ** 2 / (2 * s ** 2))
            )
            conv = np.convolve(signal.y, wavelet_arr, mode='same')
            if len(conv) > n:
                conv = conv[:n]
            elif len(conv) < n:
                conv = np.pad(conv, (0, n - len(conv)))
            cwt_matrix[i, :] = conv * np.sqrt(dt)

        return cwt_matrix


class LaplaceTransform:
    """拉普拉斯变换 — 符号正/逆 + 传递函数"""

    @staticmethod
    def forward(expr_str: str) -> dict:
        t, s = sp.symbols('t s', positive=True)
        try:
            loc = {"t": t, "s": s, "sin": sp.sin, "cos": sp.cos, "exp": sp.exp,
                   "Heaviside": sp.Heaviside, "DiracDelta": sp.DiracDelta,
                   "pi": sp.pi, "sinh": sp.sinh, "cosh": sp.cosh}
            f_expr = sp.sympify(expr_str, locals=loc)
            F = sp.laplace_transform(f_expr, t, s, noconds=True)
            F = sp.simplify(F)
            poles, zeros = LaplaceTransform._pz(F, s)
            return {"input": sp.latex(f_expr), "result": sp.latex(F),
                    "raw": str(F), "poles": poles, "zeros": zeros}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def inverse(expr_str: str) -> dict:
        t, s = sp.symbols('t s', positive=True)
        try:
            F_expr = sp.sympify(expr_str, locals={"t": t, "s": s, "pi": sp.pi})
            f = sp.inverse_laplace_transform(F_expr, s, t, noconds=True)
            return {"input": sp.latex(F_expr), "result": sp.latex(sp.simplify(f)),
                    "raw": str(sp.simplify(f))}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _pz(expr, s):
        try:
            num, den = sp.fraction(expr)
            poles = [complex(sp.N(p).evalf()) for p in sp.solve(den, s) if p.is_number]
            zeros = [complex(sp.N(z).evalf()) for z in sp.solve(num, s) if z.is_number]
            return poles, zeros
        except Exception:
            return [], []

    @staticmethod
    def transfer_response(num, den, f_range=(0.001, 1000), pts=1000) -> TransformResult:
        from scipy.signal import freqs
        w = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), pts)
        w, H = freqs(num, den, worN=w)
        return TransformResult(
            name="H(jω)", data_x=w,
            data_y=20*np.log10(np.abs(H)+1e-15), data_y2=np.unwrap(np.angle(H)),
            xlabel="Frequency (rad/s)", ylabel="Magnitude (dB)", y2label="Phase (rad)"
        )


class ZTransform:
    """Z 变换 — 数值"""

    @staticmethod
    def numeric(signal, n_pts=512) -> TransformResult:
        omega = np.linspace(0, np.pi, n_pts)
        z = np.exp(1j * omega)
        y = signal.y[:min(len(signal.y), 1000)]
        Y = np.array([np.sum(y * (zk ** (-np.arange(len(y))))) for zk in z])
        return TransformResult(
            name=f"Z({signal.name})", data_x=omega,
            data_y=np.abs(Y), data_y2=np.angle(Y),
            xlabel="ω (rad/sample)", ylabel="|H(e^{jω})|", y2label="Phase (rad)"
        )

    @staticmethod
    def zplane(b, a) -> Tuple[np.ndarray, np.ndarray]:
        """计算零极点（Z平面）"""
        return np.roots(b), np.roots(a)
