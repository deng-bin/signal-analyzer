"""单元测试 — 信号引擎"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signal_engine import Signal, SignalGenerator, SignalOps


class TestSignal:
    """Signal 数据结构测试"""

    def test_creation(self):
        t = np.linspace(0, 2, 2000, endpoint=False)
        y = np.sin(2 * np.pi * 5 * t)
        sig = Signal(name="test", t=t, y=y, fs=1000)
        assert sig.name == "test"
        assert sig.n_samples == 2000
        assert abs(sig.duration - 2.0) < 0.01
        assert sig.fs == 1000.0

    def test_fs_inference(self):
        t = np.linspace(0, 1, 500, endpoint=False)
        y = np.sin(t)
        sig = Signal(name="inf", t=t, y=y)
        assert abs(sig.fs - 500.0) < 1.0

    def test_copy(self):
        t = np.linspace(0, 1, 100)
        y = t ** 2
        sig = Signal(name="orig", t=t, y=y)
        cp = sig.copy()
        assert cp.name == "orig_copy"
        assert np.array_equal(cp.y, sig.y)
        cp.y[0] = 999
        assert sig.y[0] != 999

    def test_dt(self):
        sig = Signal(name="dt", t=np.arange(10) / 500, y=np.ones(10), fs=500)
        assert abs(sig.dt - 0.002) < 1e-9


class TestSignalGenerator:
    """信号生成器测试"""

    def test_sine(self):
        sig = SignalGenerator.sine(freq=5, amp=2, duration=1, fs=1000)
        assert len(sig.y) == 1000
        assert abs(sig.y.max() - 2.0) < 0.01
        assert abs(sig.y.min() + 2.0) < 0.01

    def test_cosine(self):
        sig = SignalGenerator.cosine(freq=0, amp=1, duration=1, fs=100)
        assert np.allclose(sig.y, 1.0)

    def test_square(self):
        sig = SignalGenerator.square(freq=10, amp=1, duration=0.5, fs=10000)
        vals = set(np.round(sig.y, 1))
        assert 1.0 in vals or -1.0 in vals

    def test_impulse(self):
        sig = SignalGenerator.impulse(duration=1, fs=1000)
        assert sig.y[0] == 1.0
        assert np.all(sig.y[1:] == 0)

    def test_step(self):
        sig = SignalGenerator.step(duration=1, fs=1000)
        assert np.all(sig.y == 1.0)

    def test_noise(self):
        sig = SignalGenerator.noise(duration=2, fs=1000, std=0.5, color='white')
        assert len(sig.y) == 2000
        assert 0.3 < sig.y.std() < 0.7

    def test_gaussian_pulse(self):
        sig = SignalGenerator.gaussian_pulse(center=0.5, sigma=0.05, duration=1, fs=1000)
        peak_idx = np.argmax(sig.y)
        assert abs(sig.t[peak_idx] - 0.5) < 0.02

    def test_multi_tone(self):
        sig = SignalGenerator.multi_tone([5, 15], [1, 0.5], duration=2, fs=1000)
        assert sig.n_samples == 2000

    def test_harmonic_series(self):
        sig = SignalGenerator.harmonic_series(f0=50, n_harmonics=3, duration=0.5, fs=1000)
        assert len(sig.y) == 500

    def test_custom_expression(self):
        sig = SignalGenerator.custom_expression("sin(2*pi*5*t)", duration=1, fs=500)
        assert sig.n_samples == 500
        assert abs(sig.y.max() - 1.0) < 0.01

    def test_custom_expression_complex(self):
        sig = SignalGenerator.custom_expression(
            "exp(-2*t) * sin(2*pi*10*t)", duration=1, fs=1000
        )
        assert abs(sig.y[0]) < 0.1
        assert abs(sig.y[-1]) < 0.2

    def test_discrete_mode(self):
        sig = SignalGenerator.sine(freq=5, duration=1, fs=100, discrete=True)
        assert sig.signal_type == "discrete"

    def test_ecg_like(self):
        sig = SignalGenerator.ecg_like(duration=2, fs=500, bpm=60)
        assert sig.n_samples == 1000
        assert sig.y.max() > 0.5

    def test_from_arrays(self):
        t = np.arange(0, 1, 0.001)
        y = np.sin(2 * np.pi * 10 * t)
        sig = SignalGenerator.from_arrays(t, y, name="test")
        assert sig.name == "test"
        assert len(sig.y) == len(t)


class TestSignalOps:
    """信号运算测试"""

    def setup_method(self):
        self.s1 = SignalGenerator.sine(freq=5, amp=2, duration=1, fs=1000)
        self.s2 = SignalGenerator.sine(freq=10, amp=1, duration=1, fs=1000)

    def test_scale(self):
        res = SignalOps.scale(self.s1, 3.0)
        assert np.allclose(res.y, self.s1.y * 3)

    def test_derivative(self):
        sig = SignalGenerator.sine(freq=1, amp=1, duration=2, fs=1000)
        deriv = SignalOps.derivative(sig)
        assert len(deriv.y) == len(sig.y)

    def test_integral(self):
        sig = SignalGenerator.step(duration=1, fs=1000)
        integ = SignalOps.integral(sig)
        assert integ.y[-1] > 0.9

    def test_normalize(self):
        sig = SignalGenerator.sine(freq=5, amp=3, duration=1, fs=1000)
        norm = SignalOps.normalize(sig)
        assert abs(norm.y.max() - 1.0) < 0.01

    def test_rect(self):
        sig = SignalGenerator.sine(freq=5, amp=1, duration=1, fs=1000)
        rect = SignalOps.rect(sig)
        assert np.all(rect.y >= 0)

    def test_half_rect(self):
        sig = SignalGenerator.sine(freq=5, amp=1, duration=1, fs=1000)
        half = SignalOps.half_rect(sig)
        assert np.all(half.y >= 0)
        zeros = np.sum(half.y == 0)
        assert zeros > 100

    def test_convolve(self):
        s1 = SignalGenerator.impulse(duration=1, fs=1000)
        s2 = SignalGenerator.sine(freq=5, duration=1, fs=1000)
        conv = SignalOps.convolve(s1, s2)
        assert len(conv.y) == len(s1.y) + len(s2.y) - 1

    def test_correlate(self):
        s1 = SignalGenerator.sine(freq=5, duration=1, fs=1000)
        corr = SignalOps.correlate(s1, s1)
        mid = len(corr.y) // 2
        assert corr.y[mid] == corr.y.max()
