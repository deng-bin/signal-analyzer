"""单元测试 — 滤波器引擎"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signal_engine import SignalGenerator
from filter_engine import FIRFilter, IIRFilter, FilterBank, FilterResult


class TestFIRFilter:
    """FIR 滤波器测试"""

    def test_window_method_lowpass(self):
        flt = FIRFilter.window_method(cutoff=100, fs=1000, numtaps=51, window='hamming')
        assert isinstance(flt, FilterResult)
        assert flt.filter_type == "FIR"
        assert len(flt.b) == 51
        assert flt.freq is not None
        assert flt.mag is not None

    def test_window_method_highpass(self):
        flt = FIRFilter.window_method(
            cutoff=100, fs=1000, numtaps=51, window='hann', pass_zero=False
        )
        assert flt.filter_type == "FIR"

    def test_remez(self):
        flt = FIRFilter.remez(
            bands=[0, 80, 120, 400], desired=[1, 0], fs=1000, numtaps=51
        )
        assert flt.filter_type == "FIR"
        assert len(flt.b) == 51

    def test_impulse_response(self):
        flt = FIRFilter.window_method(cutoff=50, fs=1000, numtaps=21)
        n, ir = flt.impulse_response(100)
        assert len(n) == 100
        assert len(ir) == 100

    def test_step_response(self):
        flt = FIRFilter.window_method(cutoff=50, fs=1000, numtaps=21)
        n, sr = flt.step_response(100)
        assert len(sr) == 100

    def test_apply(self):
        flt = FIRFilter.window_method(cutoff=100, fs=1000, numtaps=31)
        sig = SignalGenerator.sine(freq=10, amp=1, duration=1, fs=1000)
        filtered = flt.apply(sig)
        assert filtered.n_samples == sig.n_samples

    def test_apply_filtfilt(self):
        flt = FIRFilter.window_method(cutoff=100, fs=1000, numtaps=31)
        sig = SignalGenerator.sine(freq=10, amp=1, duration=1, fs=1000)
        filtered = flt.apply_filtfilt(sig)
        assert filtered.n_samples == sig.n_samples


class TestIIRFilter:
    """IIR 滤波器测试"""

    def test_butterworth(self):
        flt = IIRFilter.butterworth(order=4, cutoff=100, fs=1000, btype='lowpass')
        assert flt.filter_type == "IIR"
        assert flt.order == 4
        assert len(flt.b) > 0
        assert len(flt.a) > 0

    def test_chebyshev1(self):
        flt = IIRFilter.chebyshev1(order=4, cutoff=100, rp=1, fs=1000)
        assert flt.filter_type == "IIR"

    def test_chebyshev2(self):
        flt = IIRFilter.chebyshev2(order=4, cutoff=100, rs=40, fs=1000)
        assert flt.filter_type == "IIR"

    def test_elliptic(self):
        flt = IIRFilter.elliptic(order=4, cutoff=100, rp=1, rs=40, fs=1000)
        assert flt.filter_type == "IIR"

    def test_bessel(self):
        flt = IIRFilter.bessel(order=4, cutoff=100, fs=1000)
        assert flt.filter_type == "IIR"

    def test_notch(self):
        flt = IIRFilter.iirnotch(w0=50, Q=30, fs=1000)
        assert flt.filter_type == "IIR"
        assert flt.order == 2

    def test_peak(self):
        flt = IIRFilter.iirpeak(w0=100, Q=10, fs=1000)
        assert flt.filter_type == "IIR"
        assert flt.order == 2

    def test_bandpass(self):
        flt = IIRFilter.butterworth(order=4, cutoff=[50, 200], fs=1000, btype='bandpass')
        assert flt.filter_type == "IIR"

    def test_poles_and_zeros(self):
        flt = IIRFilter.butterworth(order=4, cutoff=100, fs=1000)
        assert len(flt.poles) > 0
        assert len(flt.zeros) > 0


class TestFilterBank:
    """滤波器组测试"""

    def test_octave_analysis(self):
        sig = SignalGenerator.noise(duration=2, fs=1000, std=0.1)
        f_centers, band_power_db, band_power = FilterBank.octave_analysis(
            sig, n_bands=5, f_min=20, f_max=200
        )
        assert len(f_centers) == 5
        assert len(band_power) == 5
