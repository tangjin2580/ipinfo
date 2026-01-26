#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志清理和归档脚本
可以手动执行或通过cron定时执行
"""

import sys
import os

# 添加server目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_manager import (
    setup_logger, 
    archive_old_logs, 
    cleanup_empty_logs, 
    get_log_stats
)
import argparse


def main():
    parser = argparse.ArgumentParser(description='日志清理和归档工具')
    parser.add_argument('--days', type=int, default=7, 
                        help='归档多少天前的日志 (默认: 7)')
    parser.add_argument('--log-dir', default='../log',
                        help='日志目录 (默认: ../log)')
    parser.add_argument('--archive-dir', default='../log/archive',
                        help='归档目录 (默认: ../log/archive)')
    parser.add_argument('--clean-only', action='store_true',
                        help='仅清理空日志，不归档')
    parser.add_argument('--stats-only', action='store_true',
                        help='仅显示统计信息')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(args.log_dir)
    
    print("\n" + "="*60)
    print("📦 日志清理和归档工具")
    print("="*60 + "\n")
    
    if args.stats_only:
        # 仅显示统计
        stats = get_log_stats(args.log_dir)
        print("📊 当前日志统计:")
        print(f"  📁 总文件数: {stats['total_logs']}")
        print(f"  📦 已压缩: {stats['compressed_logs']}")
        print(f"  💾 总大小: {stats['total_size_mb']} MB")
        print(f"  📈 压缩率: {stats['compression_rate']}")
        print()
        return
    
    # 清理空日志
    print("🧹 清理空日志文件...")
    cleaned = cleanup_empty_logs(args.log_dir)
    if cleaned > 0:
        print(f"  ✅ 已删除 {cleaned} 个空日志文件")
    else:
        print("  ℹ️  没有需要清理的空日志")
    print()
    
    if not args.clean_only:
        # 归档旧日志
        print(f"📦 归档 {args.days} 天前的日志...")
        archived = archive_old_logs(args.log_dir, args.archive_dir, args.days)
        if archived > 0:
            print(f"  ✅ 已归档并压缩 {archived} 个日志文件")
        else:
            print(f"  ℹ️  没有需要归档的日志")
        print()
    
    # 显示最终统计
    print("📊 清理后的统计:")
    stats = get_log_stats(args.log_dir)
    print(f"  📁 总文件数: {stats['total_logs']}")
    print(f"  📦 已压缩: {stats['compressed_logs']}")
    print(f"  💾 总大小: {stats['total_size_mb']} MB")
    print(f"  📈 压缩率: {stats['compression_rate']}")
    
    print("\n" + "="*60)
    print("✅ 清理完成")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
