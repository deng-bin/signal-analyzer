"""信号生成、导入导出引擎 v2.0 — 20+ 信号类型"""
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Callable
import uuid
import csv
import os


@dataclass
class Signal:
    """信号数据结构"""
    name: str
    t: np.ndarray
    y: np.ndarray
    signal_type: str = "continuous"
    params: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    fs: float = 1000.0
    description: str = ""

    def __post_init__(self):
        if self.fs == 1000.0 and len(self.t) > 1:
            self.fs = 1.0 / (self.t[1] - self.t[0])
        if not self.description:
            self.description = self.name

    @property
    def dt(self) -> float:
        return 1.0 / self.fs if self.fs > 0 else 0.001

    @property
    def duration(self) -> float:
        return float(self.t[-1] - self.t[0]) if len(self.t) > 0 else 0

    @property
    def n_samples(self) -> int:
        return len(self.y)

    def copy(self) -> "Signal":
        return Signal(name=self.name + "_copy", t=self.t.copy(), y=self.y.copy(),
                      signal_type=self.signal_type, params=self.params.copy(),
                      fs=self.fs, description=self.description)


class SignalGenerator:
    """信号生成器 — 20+ 种信号类型"""

    @staticmethod
    def _make_time(duration: float, fs: float, discrete: bool) -> np.ndarray:
        n = int(duration * fs)
        return np.arange(n) / fs if discrete else np.linspace(0, duration, n, endpoint=False)

    @staticmethod
    def sine(freq=1.0, amp=1.0, phase=0.0, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * np.sin(2 * np.pi * freq * t + phase)
        return Signal(name=f"sin({freq}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"freq": freq, "amp": amp, "phase": phase},
                      description=f"正弦波 {freq}Hz")

    @staticmethod
    def cosine(freq=1.0, amp=1.0, phase=0.0, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * np.cos(2 * np.pi * freq * t + phase)
        return Signal(name=f"cos({freq}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"freq": freq, "amp": amp, "phase": phase})

    @staticmethod
    def square(freq=1.0, amp=1.0, duty=0.5, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        from scipy.signal import square as sq
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * sq(2 * np.pi * freq * t, duty)
        return Signal(name=f"square({freq}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"freq": freq, "amp": amp, "duty": duty})

    @staticmethod
    def sawtooth(freq=1.0, amp=1.0, width=1.0, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        from scipy.signal import sawtooth as sw
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * sw(2 * np.pi * freq * t, width)
        return Signal(name=f"sawtooth({freq}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"freq": freq, "amp": amp, "width": width})

    @staticmethod
    def triangle(freq=1.0, amp=1.0, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        period = 1.0 / freq
        y = amp * (2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1)
        return Signal(name=f"triangle({freq}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"freq": freq, "amp": amp})

    @staticmethod
    def chirp(f0=1.0, f1=100.0, amp=1.0, duration=2.0, fs=1000.0,
              method='linear', discrete=False) -> Signal:
        from scipy.signal import chirp as scipy_chirp
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * scipy_chirp(t, f0=f0, f1=f1, t1=duration, method=method)
        return Signal(name=f"chirp({f0}-{f1}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"f0": f0, "f1": f1, "amp": amp, "method": method})

    @staticmethod
    def impulse(duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = np.zeros_like(t)
        y[0] = 1.0
        return Signal(name="δ(t) impulse", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def step(duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = np.ones_like(t)
        return Signal(name="u(t) step", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def noise(duration=2.0, fs=1000.0, std=0.1, color='white', discrete=False) -> Signal:
        """白噪声/粉红噪声/布朗噪声"""
        t = SignalGenerator._make_time(duration, fs, discrete)
        n = len(t)
        if color == 'white':
            y = std * np.random.randn(n)
        elif color == 'pink':
            white = np.random.randn(n)
            pink = np.cumsum(white) / np.sqrt(np.arange(1, n + 1))
            y = std * pink / np.std(pink)
        elif color == 'brown':
            y = std * np.cumsum(np.random.randn(n)) / np.sqrt(n)
        else:
            y = std * np.random.randn(n)
        return Signal(name=f"{color} noise", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"std": std, "color": color})

    @staticmethod
    def gaussian_pulse(center=0.5, sigma=0.05, amp=1.0, duration=1.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * np.exp(-0.5 * ((t - center) / sigma) ** 2)
        return Signal(name=f"Gaussian(σ={sigma})", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def sinc_pulse(fc=10.0, amp=1.0, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        t_centered = t - duration / 2
        y = amp * np.sinc(2 * fc * t_centered)
        return Signal(name=f"sinc({fc}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def exponential_decay(tau=0.1, amp=1.0, duration=1.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * np.exp(-t / tau)
        return Signal(name=f"decay(τ={tau})", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def am_modulation(carrier=100.0, modulator=5.0, amp=1.0, depth=0.8,
                      duration=1.0, fs=2000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = amp * (1 + depth * np.sin(2 * np.pi * modulator * t)) * np.cos(2 * np.pi * carrier * t)
        return Signal(name=f"AM({carrier}Hz+{modulator}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def fm_modulation(carrier=100.0, modulator=5.0, amp=1.0, deviation=20.0,
                      duration=1.0, fs=2000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        integral = np.cumsum(np.sin(2 * np.pi * modulator * t)) / fs
        y = amp * np.cos(2 * np.pi * carrier * t + 2 * np.pi * deviation * integral)
        return Signal(name=f"FM({carrier}Hz+{modulator}Hz)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def multi_tone(freqs: list, amps: list = None, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        if amps is None:
            amps = [1.0] * len(freqs)
        y = np.zeros_like(t)
        for f, a in zip(freqs, amps):
            y += a * np.sin(2 * np.pi * f * t)
        return Signal(name=f"multi({len(freqs)} tones)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def harmonic_series(f0=50.0, n_harmonics=5, amp=1.0, decay=0.5,
                        duration=1.0, fs=1000.0, discrete=False) -> Signal:
        t = SignalGenerator._make_time(duration, fs, discrete)
        y = np.zeros_like(t)
        for k in range(1, n_harmonics + 1):
            y += amp * (decay ** (k - 1)) * np.sin(2 * np.pi * f0 * k * t)
        return Signal(name=f"harmonics({f0}Hz×{n_harmonics})", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def ecg_like(duration=2.0, fs=500.0, bpm=60.0, discrete=False) -> Signal:
        """模拟心电信号"""
        t = SignalGenerator._make_time(duration, fs, discrete)
        period = 60.0 / bpm
        y = np.zeros_like(t)
        for i in range(int(duration / period) + 1):
            t0 = i * period
            mask = (t >= t0) & (t < t0 + 0.4)
            if mask.any():
                tc = t[mask] - t0
                y[mask] += 0.1 * np.exp(-0.5 * ((tc - 0.05) / 0.01) ** 2)
                y[mask] += 1.0 * np.exp(-0.5 * ((tc - 0.08) / 0.008) ** 2)
                y[mask] += -0.3 * np.exp(-0.5 * ((tc - 0.12) / 0.01) ** 2)
                y[mask] += 0.3 * np.exp(-0.5 * ((tc - 0.2) / 0.03) ** 2)
        return Signal(name=f"ECG({bpm}bpm)", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous")

    @staticmethod
    def custom_expression(expr: str, duration=2.0, fs=1000.0, discrete=False) -> Signal:
        """自定义数学表达式，如 'sin(2*pi*5*t) * exp(-t)'"""
        t = SignalGenerator._make_time(duration, fs, discrete)
        safe = {"t": t, "pi": np.pi, "sin": np.sin, "cos": np.cos,
                "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs,
                "log": np.log, "tan": np.tan, "sinc": np.sinc,
                "sinh": np.sinh, "cosh": np.cosh}
        try:
            y = eval(expr, {"__builtins__": {}}, safe)
            y = np.atleast_1d(np.array(y, dtype=float))
            if len(y) == 1:
                y = np.full_like(t, y)
        except Exception as e:
            raise ValueError(f"表达式错误: {e}")
        return Signal(name=f"custom: {expr[:25]}", t=t, y=y, fs=fs,
                      signal_type="discrete" if discrete else "continuous",
                      params={"expr": expr})

    @staticmethod
    def from_arrays(t, y, name="imported", fs=None, discrete=False) -> Signal:
        t, y = np.array(t, dtype=float), np.array(y, dtype=float)
        if fs is None and len(t) > 1:
            fs = 1.0 / (t[1] - t[0])
        return Signal(name=name, t=t, y=y, fs=fs or 1000,
                      signal_type="discrete" if discrete else "continuous")

    # ---- 导入导出 ----
    @staticmethod
    def import_csv(path: str) -> Signal:
        data = np.loadtxt(path, delimiter=',', skiprows=1)
        if data.ndim == 1:
            t = np.arange(len(data))
            y = data
        else:
            t, y = data[:, 0], data[:, 1]
        name = os.path.splitext(os.path.basename(path))[0]
        return SignalGenerator.from_arrays(t, y, name=name)

    @staticmethod
    def import_wav(path: str) -> Signal:
        from scipy.io import wavfile
        fs, data = wavfile.read(path)
        if data.ndim > 1:
            data = data[:, 0]
        t = np.arange(len(data)) / fs
        name = os.path.splitext(os.path.basename(path))[0]
        return Signal(name=name, t=t, y=data.astype(float), fs=fs,
                      signal_type="discrete")

    @staticmethod
    def import_mat(path: str, varname: str = None) -> list[Signal]:
        from scipy.io import loadmat
        mat = loadmat(path)
        signals = []
        for key, val in mat.items():
            if key.startswith('__'):
                continue
            if isinstance(val, np.ndarray) and val.ndim <= 2:
                if varname and key != varname:
                    continue
                if val.ndim == 1:
                    t = np.arange(len(val))
                    y = val
                else:
                    t = np.arange(val.shape[0])
                    y = val[:, 0] if val.shape[1] > 0 else val
                signals.append(Signal(name=key, t=t, y=y.ravel(), fs=1000,
                                      signal_type="discrete"))
        return signals

    @staticmethod
    def export_csv(signal, path: str):
        np.savetxt(path, np.column_stack([signal.t, signal.y]),
                   delimiter=',', header='Time,Amplitude', comments='')

    @staticmethod
    def export_wav(signal, path: str):
        from scipy.io import wavfile
        y_int16 = np.int16(signal.y / np.max(np.abs(signal.y)) * 32767)
        wavfile.write(path, int(signal.fs), y_int16)


class SignalOps:
    """信号运算操作"""

    @staticmethod
    def add(s1: Signal, s2: Signal) -> Signal:
        t = np.linspace(0, min(s1.duration, s2.duration),
                        min(s1.n_samples, s2.n_samples), endpoint=False)
        y1 = np.interp(t, s1.t, s1.y)
        y2 = np.interp(t, s2.t, s2.y)
        fs = 1.0 / (t[1] - t[0]) if len(t) > 1 else 1000
        return Signal(name=f"({s1.name})+({s2.name})", t=t, y=y1+y2, fs=fs)

    @staticmethod
    def sub(s1: Signal, s2: Signal) -> Signal:
        t = np.linspace(0, min(s1.duration, s2.duration),
                        min(s1.n_samples, s2.n_samples), endpoint=False)
        y1 = np.interp(t, s1.t, s1.y)
        y2 = np.interp(t, s2.t, s2.y)
        fs = 1.0 / (t[1] - t[0]) if len(t) > 1 else 1000
        return Signal(name=f"({s1.name})-({s2.name})", t=t, y=y1-y2, fs=fs)

    @staticmethod
    def mul(s1: Signal, s2: Signal) -> Signal:
        t = np.linspace(0, min(s1.duration, s2.duration),
                        min(s1.n_samples, s2.n_samples), endpoint=False)
        y1 = np.interp(t, s1.t, s1.y)
        y2 = np.interp(t, s2.t, s2.y)
        fs = 1.0 / (t[1] - t[0]) if len(t) > 1 else 1000
        return Signal(name=f"({s1.name})·({s2.name})", t=t, y=y1*y2, fs=fs)

    @staticmethod
    def scale(s: Signal, factor: float) -> Signal:
        return Signal(name=f"{factor}·{s.name}", t=s.t.copy(), y=s.y*factor,
                      fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def derivative(s: Signal) -> Signal:
        return Signal(name=f"d/dt({s.name})", t=s.t.copy(),
                      y=np.gradient(s.y, s.t), fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def integral(s: Signal) -> Signal:
        from scipy.integrate import cumulative_trapezoid
        return Signal(name=f"∫({s.name})", t=s.t.copy(),
                      y=cumulative_trapezoid(s.y, s.t, initial=0),
                      fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def abs_value(s: Signal) -> Signal:
        return Signal(name=f"|{s.name}|", t=s.t.copy(), y=np.abs(s.y),
                      fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def normalize(s: Signal) -> Signal:
        mx = np.max(np.abs(s.y))
        return Signal(name=f"norm({s.name})", t=s.t.copy(),
                      y=s.y / mx if mx > 0 else s.y,
                      fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def rect(s: Signal) -> Signal:
        """全波整流"""
        return Signal(name=f"rect({s.name})", t=s.t.copy(), y=np.abs(s.y),
                      fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def half_rect(s: Signal) -> Signal:
        """半波整流"""
        return Signal(name=f"half_rect({s.name})", t=s.t.copy(),
                      y=np.maximum(s.y, 0), fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def clip(s: Signal, lo: float, hi: float) -> Signal:
        return Signal(name=f"clip({s.name})", t=s.t.copy(),
                      y=np.clip(s.y, lo, hi), fs=s.fs, signal_type=s.signal_type)

    @staticmethod
    def convolve(s1: Signal, s2: Signal) -> Signal:
        y = np.convolve(s1.y, s2.y, mode='full') / s1.fs
        t = np.arange(len(y)) / s1.fs
        return Signal(name=f"({s1.name})∗({s2.name})", t=t, y=y, fs=s1.fs)

    @staticmethod
    def correlate(s1: Signal, s2: Signal) -> Signal:
        y = np.correlate(s1.y, s2.y, mode='full')
        t = np.arange(len(y)) / s1.fs
        return Signal(name=f"corr({s1.name},{s2.name})", t=t, y=y, fs=s1.fs)
