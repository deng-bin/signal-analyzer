"""单元测试 — 变换引擎"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signal_engine import SignalGenerator
from transform_engine import (
    FourierTransform, HilbertTransform, WaveletTransform,
    LaplaceTransform, ZTransform, TransformResult,
)


class TestFourierTransform:
    """傅里叶变换测试"""

    def setup_method(self):
        self.sig = SignalGenerator.sine(freq=10, amp=1, duration=1, fs=1000)

    def test_fft_basic(self):
        r = FourierTransform.fft(self.sig)
        assert isinstance(r, TransformResult)
        assert r.data_y is not None
        assert r.data_y2 is not None
        assert len(r.data_x) == len(r.data_y)

    def test_fft_peak_at_freq(self):
        r = FourierTransform.fft(self.sig)
        peak_idx = np.argmax(r.data_y)
        peak_freq = r.data_x[peak_idx]
        assert 9 < peak_freq < 11

    def test_fft_with_window(self):
        r = FourierTransform.fft(self.sig, n=2048, window='hamming')
        assert r.data_y is not None

    def test_dft(self):
        r = FourierTransform.dft(self.sig, N=1024)
        assert isinstance(r, TransformResult)

    def test_stft(self):
        f, t, Sxx = FourierTransform.stft(self.sig, nperseg=256, noverlap=128)
        assert len(f) > 0
        assert len(t) > 0
        assert Sxx.shape == (len(f), len(t))

    def test_power_spectrum(self):
        r = FourierTransform.power_spectrum(self.sig, method='periodogram')
        assert r.data_y is not None

    def test_cepstrum(self):
        r = FourierTransform.cepstrum(self.sig)
        assert len(r.data_x) == len(r.data_y)

    def test_coherence(self):
        s1 = SignalGenerator.sine(freq=10, duration=1, fs=1000)
        s2 = SignalGenerator.sine(freq=10, duration=1, fs=1000)
        r = FourierTransform.coherence(s1, s2)
        # 相同频率应产生高相干性
        peak_idx = np.argmax(r.data_x >= 10)
        if peak_idx < len(r.data_y):
            assert r.data_y[peak_idx] > 0.5

    def test_ifft(self):
        r = FourierTransform.fft(self.sig)
        recovered = FourierTransform.ifft(r.data_y, r.data_y2, fs=self.sig.fs)
        assert len(recovered) > 0


class TestHilbertTransform:
    """希尔伯特变换测试"""

    def test_analytic_signal(self):
        sig = SignalGenerator.sine(freq=5, amp=2, duration=1, fs=1000)
        r = HilbertTransform.analytic_signal(sig)
        # 包络应接近常数 2
        assert 1.8 < r.data_y.mean() < 2.2
        assert r.data_y2 is not None  # 相位
        assert r.data_y3 is not None  # 瞬时频率


class TestWaveletTransform:
    """小波变换测试"""

    def test_cwt_basic(self):
        sig = SignalGenerator.chirp(f0=5, f1=50, duration=1, fs=500)
        r = WaveletTransform.cwt(sig, n_scales=32)
        assert r.data_y2.shape[0] == 32
        assert r.data_y2.shape[1] == sig.n_samples

    def test_cwt_with_scales(self):
        sig = SignalGenerator.sine(freq=10, duration=1, fs=500)
        scales = np.array([2, 4, 8, 16, 32])
        r = WaveletTransform.cwt(sig, scales=scales)
        assert r.data_y2.shape[0] == len(scales)


class TestLaplaceTransform:
    """拉普拉斯变换测试"""

    def test_forward_sin(self):
        r = LaplaceTransform.forward("sin(2*t)")
        assert "error" not in r
        assert r["raw"] != ""

    def test_forward_exp(self):
        r = LaplaceTransform.forward("exp(-3*t)")
        assert "error" not in r

    def test_inverse(self):
        r = LaplaceTransform.inverse("1/(s**2 + 1)")
        assert "error" not in r
        assert "sin" in r["raw"].lower()

    def test_transfer_response(self):
        r = LaplaceTransform.transfer_response([1], [1, 1, 1])
        assert r.data_y is not None
        assert r.data_y2 is not None


class TestZTransform:
    """Z 变换测试"""

    def test_numeric(self):
        sig = SignalGenerator.sine(freq=10, duration=0.5, fs=500)
        r = ZTransform.numeric(sig, n_pts=64)
        assert r.data_y is not None
        assert r.data_y2 is not None
