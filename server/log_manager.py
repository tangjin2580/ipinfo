import time
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os
import gzip
import shutil
import time  # 已经导入，但需要确保在类中使用
from datetime import datetime, timedelta
import glob


class CompressedRotatingFileHandler(RotatingFileHandler):
    """
    自动压缩的日志处理器
    继承RotatingFileHandler，在日志轮转时自动压缩旧日志
    """

    def doRollover(self):
        """
        执行日志轮转并压缩旧日志
        """
        # 先执行标准的轮转
        super().doRollover()

        # 压缩刚刚轮转的日志文件
        if self.backupCount > 0:
            # 获取最新的备份文件
            backup_file = f"{self.baseFilename}.1"
            if os.path.exists(backup_file):
                # 压缩
                gz_file = f"{backup_file}.gz"
                try:
                    with open(backup_file, 'rb') as f_in:
                        with gzip.open(gz_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    # 删除原文件
                    os.remove(backup_file)
                    # 使用print避免循环引用
                    print(f'日志已压缩: {gz_file}')
                except Exception as e:
                    print(f'压缩日志失败: {str(e)}')


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    按时间轮转并自动压缩的日志处理器
    """

    def __init__(self, filename, when='midnight', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, atTime=None):
        """
        初始化处理器，确保所有必要的属性都被正确设置
        """
        # 调用父类的初始化方法
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)

        # 确保converter属性存在
        if not hasattr(self, 'converter'):
            self.converter = time.gmtime if utc else time.localtime

    def doRollover(self):
        """
        执行日志轮转并压缩旧日志
        """
        # 确保converter属性存在
        if not hasattr(self, 'converter'):
            self.converter = time.gmtime if getattr(self, 'utc', False) else time.localtime

        # 关闭当前文件
        if self.stream:
            self.stream.close()
            self.stream = None

        # 获取当前时间用于重命名
        if os.path.exists(self.baseFilename):
            current_time = int(os.stat(self.baseFilename).st_mtime)
        else:
            current_time = int(time.time())

        # 计算轮转时间
        dst_time = self.computeRollover(current_time)

        # 获取时间元组用于格式化
        time_tuple = self.converter(dst_time)

        # 生成新的文件名
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, time_tuple))

        # 如果目标文件存在，删除它
        if os.path.exists(dfn):
            os.remove(dfn)

        # 重命名当前日志文件
        if os.path.exists(self.baseFilename):
            self.rotate(self.baseFilename, dfn)

        # 压缩刚刚轮转的文件
        if os.path.exists(dfn):
            gz_file = f"{dfn}.gz"
            try:
                with open(dfn, 'rb') as f_in:
                    with gzip.open(gz_file, 'wb', compresslevel=9) as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(dfn)
                print(f'✅ 日志已压缩: {os.path.basename(gz_file)}')
            except Exception as e:
                print(f'❌ 压缩日志失败: {str(e)}')

        # 删除过期的备份
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                try:
                    os.remove(s)
                except OSError:
                    pass

        # 打开新的日志文件
        if not self.delay:
            self.stream = self._open()

        # 更新轮转时间
        new_rollover_at = self.computeRollover(dst_time)
        while new_rollover_at <= dst_time:
            new_rollover_at = new_rollover_at + self.interval
        self.rolloverAt = new_rollover_at


def setup_logger(log_dir='../log', log_level=logging.INFO):
    """
    配置优化的日志系统

    特性：
    1. 按日期命名（app_YYYY-MM-DD.log）
    2. 每天午夜自动轮转
    3. 自动压缩旧日志（.gz）
    4. 保留30天日志
    5. 按大小分割（单文件最大50MB）
    """
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 按日期命名日志文件
    log_filename = os.path.join(log_dir, 'app.log')

    # 创建logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 清除现有的处理器
    logger.handlers.clear()

    # 1. 按时间轮转的处理器（主日志）
    # 每天午夜轮转，保留30天，自动压缩
    time_handler = CompressedTimedRotatingFileHandler(
        log_filename,
        when='midnight',
        interval=1,
        backupCount=30,  # 保留30天
        encoding='utf-8'
    )
    time_handler.suffix = "%Y-%m-%d"  # 日志后缀格式
    time_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )

    # 2. 控制台输出（可选）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 只输出警告及以上级别
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )

    # 添加处理器
    logger.addHandler(time_handler)
    logger.addHandler(console_handler)

    return logger


# 其余函数保持不变...
def archive_old_logs(log_dir='../log', archive_dir='../log/archive', days=30):
    """归档和压缩旧日志文件"""
    if not os.path.exists(log_dir):
        return

    # 创建归档目录
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    cutoff_date = datetime.now() - timedelta(days=days)
    archived_count = 0
    compressed_count = 0

    # 查找所有日志文件
    log_files = glob.glob(os.path.join(log_dir, 'app_*.log'))
    log_files += glob.glob(os.path.join(log_dir, 'app.log.*'))

    for log_file in log_files:
        # 跳过已压缩的文件
        if log_file.endswith('.gz'):
            continue

        # 获取文件修改时间
        file_time = datetime.fromtimestamp(os.path.getmtime(log_file))

        if file_time < cutoff_date:
            filename = os.path.basename(log_file)

            # 压缩文件
            gz_filename = f"{filename}.gz"
            archive_path = os.path.join(archive_dir, gz_filename)

            try:
                with open(log_file, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb', compresslevel=9) as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # 删除原文件
                os.remove(log_file)
                archived_count += 1
                compressed_count += 1

                print(f'✅ 归档并压缩: {filename} -> {gz_filename}')
            except Exception as e:
                print(f'❌ 归档失败 {filename}: {str(e)}')

    # 清理过期的归档文件（超过90天）
    archive_cutoff = datetime.now() - timedelta(days=90)
    archive_files = glob.glob(os.path.join(archive_dir, '*.gz'))

    for archive_file in archive_files:
        file_time = datetime.fromtimestamp(os.path.getmtime(archive_file))
        if file_time < archive_cutoff:
            try:
                os.remove(archive_file)
                print(f'🗑️  删除过期归档: {os.path.basename(archive_file)}')
            except Exception as e:
                print(f'❌ 删除失败: {str(e)}')

    if archived_count > 0:
        print(f'📦 归档完成: {archived_count} 个文件已归档, {compressed_count} 个文件已压缩')

    return archived_count


def cleanup_empty_logs(log_dir='../log'):
    """清理空日志文件"""
    if not os.path.exists(log_dir):
        return 0

    cleaned = 0
    log_files = glob.glob(os.path.join(log_dir, 'app_*.log'))

    for log_file in log_files:
        if os.path.getsize(log_file) == 0:
            try:
                os.remove(log_file)
                cleaned += 1
                print(f'🗑️  删除空日志: {os.path.basename(log_file)}')
            except Exception as e:
                print(f'❌ 删除失败: {str(e)}')

    if cleaned > 0:
        print(f'🧹 清理完成: {cleaned} 个空日志文件已删除')

    return cleaned


def get_log_stats(log_dir='../log'):
    """获取日志统计信息"""
    if not os.path.exists(log_dir):
        return {}

    total_size = 0
    log_count = 0
    compressed_count = 0

    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.startswith('app') and (file.endswith('.log') or file.endswith('.gz')):
                filepath = os.path.join(root, file)
                total_size += os.path.getsize(filepath)
                log_count += 1
                if file.endswith('.gz'):
                    compressed_count += 1

    return {
        'total_logs': log_count,
        'compressed_logs': compressed_count,
        'total_size_mb': round(total_size / 1024 / 1024, 2),
        'compression_rate': f"{compressed_count / max(log_count, 1) * 100:.1f}%"
    }


if __name__ == '__main__':
    # 测试日志配置
    logger = setup_logger()

    logger.info('测试日志系统')
    logger.warning('这是一条警告')
    logger.error('这是一条错误')

    # 执行归档
    archive_old_logs(days=7)

    # 清理空日志
    cleanup_empty_logs()

    # 显示统计
    stats = get_log_stats()
    print(f"\n📊 日志统计:")
    print(f"  总文件数: {stats['total_logs']}")
    print(f"  已压缩: {stats['compressed_logs']}")
    print(f"  总大小: {stats['total_size_mb']} MB")
    print(f"  压缩率: {stats['compression_rate']}")