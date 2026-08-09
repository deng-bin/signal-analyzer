"""
AI-First 日志系统 — JSON 结构化日志，便于 AI 解析和理解
格式: [LEVEL][TIME][MODULE] op=OPERATION | ...key=value pairs...
"""
import logging
import json
import sys
import traceback
import time
from pathlib import Path
from typing import Optional

LOG_FILE = Path(__file__).resolve().parent.parent / "app.log"


class AIFormatter(logging.Formatter):
    """AI 友好的结构化日志格式"""

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        return f"{ct.tm_hour:02d}:{ct.tm_min:02d}:{ct.tm_sec:02d}.{int(record.msecs):03d}"

    def format(self, record: logging.LogRecord) -> str:
        extra = getattr(record, 'extra_data', {})
        parts = {
            'ts': self.formatTime(record, '%H:%M:%S.%f')[:-3],
            'level': record.levelname,
            'module': record.name,
            'msg': record.getMessage(),
        }
        if extra:
            parts['data'] = extra
        if record.exc_info and record.exc_info[0]:
            parts['traceback'] = traceback.format_exception(*record.exc_info)

        return json.dumps(parts, ensure_ascii=False, default=str)


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("signal-analyzer")
    logger.setLevel(logging.DEBUG)

    # 控制台 handler — 简洁
    if not logger.handlers:
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.INFO)
        ch.setFormatter(AIFormatter())
        logger.addHandler(ch)

        # 文件 handler — 完整
        fh = logging.FileHandler(str(LOG_FILE), encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(AIFormatter())
        logger.addHandler(fh)

    return logger


log = _setup_logger()


def op(operation: str, **kwargs):
    """记录操作日志 — AI 友好结构"""
    extra = {'extra_data': {'op': operation, **kwargs}}
    log.info(f"[{operation}] " + " ".join(f"{k}={v}" for k, v in kwargs.items()), extra=extra)


def err(operation: str, exc: Exception, **kwargs):
    """记录错误日志"""
    extra = {'extra_data': {'op': operation, 'error_type': type(exc).__name__, **kwargs}}
    log.error(f"[{operation}] {type(exc).__name__}: {exc}", extra=extra, exc_info=True)


def warn(operation: str, message: str, **kwargs):
    """记录警告日志"""
    extra = {'extra_data': {'op': operation, **kwargs}}
    log.warning(f"[{operation}] {message}", extra=extra)


def debug(operation: str, **kwargs):
    """记录调试日志"""
    extra = {'extra_data': {'op': operation, **kwargs}}
    log.debug(f"[{operation}] " + " ".join(f"{k}={v}" for k, v in kwargs.items()), extra=extra)
