#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动为 CLion STM32 工程生成 .clangd 配置文件
适用于：Trae IDE 打开 CLion STM32 工程
"""

import os
import sys
import glob
import argparse
import json
from pathlib import Path


def find_arm_toolchain():
    """查找 ARM GCC 工具链"""
    possible_paths = [
        # CLion 常见路径
        r"D:\CLion\DevEnv\GNU-tools-for-STM32",
        r"C:\CLion\DevEnv\GNU-tools-for-STM32",
        r"C:\Program Files\JetBrains\CLion\plugins\embedded\tools\GNU-tools-for-STM32",
        r"D:\Program Files\JetBrains\CLion\plugins\embedded\tools\GNU-tools-for-STM32",
        os.path.expanduser(r"~\.CLion*\plugins\embedded\tools\GNU-tools-for-STM32"),
        # Arm GNU Toolchain 常见安装路径
        r"C:\Program Files\Arm GNU Toolchain arm-none-eabi",
        r"D:\Program Files\Arm GNU Toolchain arm-none-eabi",
        r"C:\gcc-arm-none-eabi",
        r"D:\gcc-arm-none-eabi",
    ]
    
    for path_pattern in possible_paths:
        matches = glob.glob(path_pattern)
        for match in matches:
            if os.path.isdir(match):
                return Path(match)
    
    return None


def find_gcc_version(toolchain_path):
    """查找 GCC 版本号"""
    gcc_lib_path = toolchain_path / "arm-none-eabi" / "lib" / "gcc" / "arm-none-eabi"
    if not gcc_lib_path.exists():
        gcc_lib_path = toolchain_path / "lib" / "gcc" / "arm-none-eabi"
    
    if not gcc_lib_path.exists():
        return None
    
    versions = []
    for item in gcc_lib_path.iterdir():
        if item.is_dir() and item.name[0].isdigit():
            versions.append(item.name)
    
    if versions:
        return sorted(versions, reverse=True)[0]
    return None


def find_compile_commands(project_dir):
    """自动查找 compile_commands.json 文件"""
    possible_paths = [
        project_dir / "build" / "Release" / "compile_commands.json",
        project_dir / "build" / "Debug" / "compile_commands.json",
        project_dir / "build" / "compile_commands.json",
        project_dir / "cmake-build-release" / "compile_commands.json",
        project_dir / "cmake-build-debug" / "compile_commands.json",
        project_dir / "compile_commands.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def generate_clangd_config(toolchain_path, gcc_version, compile_commands_path=None):
    """生成 .clangd 配置内容"""
    config_lines = []
    config_lines.append("CompileFlags:")
    
    if compile_commands_path:
        build_dir = compile_commands_path.parent.relative_to(Path.cwd())
        config_lines.append(f"  CompilationDatabase: {build_dir.as_posix()}")
    
    config_lines.append("  Add:")
    config_lines.append(f"    - --sysroot={toolchain_path.as_posix()}/arm-none-eabi")
    config_lines.append("    - -isystem")
    config_lines.append(f"    - {toolchain_path.as_posix()}/arm-none-eabi/include")
    config_lines.append("    - -isystem")
    config_lines.append(f"    - {toolchain_path.as_posix()}/arm-none-eabi/lib/gcc/arm-none-eabi/{gcc_version}/include")
    config_lines.append("    - -isystem")
    config_lines.append(f"    - {toolchain_path.as_posix()}/arm-none-eabi/lib/gcc/arm-none-eabi/{gcc_version}/include-fixed")
    config_lines.append("    - -Wno-format")
    config_lines.append("    - -Wno-format-extra-args")
    config_lines.append("    - -Wno-format-security")
    config_lines.append("    - -Wno-format-nonliteral")
    config_lines.append("    - -Wno-format-zero-length")
    
    config_lines.append("")
    config_lines.append("Diagnostics:")
    config_lines.append("  UnusedIncludes: None")
    config_lines.append("  MissingIncludes: None")
    config_lines.append("  ClangTidy:")
    config_lines.append("    Remove:")
    config_lines.append("      - '*'")
    config_lines.append("  Suppress:")
    config_lines.append("    - 'unused_include'")
    config_lines.append("    - 'pp_file_not_found'")
    
    return "\n".join(config_lines)


def main():
    parser = argparse.ArgumentParser(description="为 CLion STM32 工程生成 .clangd 配置文件（适用于 Trae IDE）")
    parser.add_argument(
        "--toolchain",
        type=str,
        help="ARM 工具链路径 (例如: D:/CLion/DevEnv/GNU-tools-for-STM32)"
    )
    parser.add_argument(
        "--compile-commands",
        type=str,
        help="compile_commands.json 路径 (例如: build/Debug/compile_commands.json)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".clangd",
        help="输出配置文件路径 (默认: .clangd)"
    )
    
    args = parser.parse_args()
    
    project_dir = Path.cwd()
    output_file = project_dir / args.output
    
    print("=" * 70)
    print("CLion STM32 工程 clangd 自动配置工具（适用于 Trae IDE）")
    print("=" * 70)
    
    compile_commands_path = None
    if args.compile_commands:
        compile_commands_path = Path(args.compile_commands)
        if not compile_commands_path.is_absolute():
            compile_commands_path = project_dir / compile_commands_path
        print(f"\n使用指定的 compile_commands.json: {compile_commands_path}")
    else:
        print("\n正在自动查找 compile_commands.json...")
        compile_commands_path = find_compile_commands(project_dir)
        if compile_commands_path:
            print(f"✅ 找到: {compile_commands_path.relative_to(project_dir)}")
        else:
            print("⚠️ 未找到 compile_commands.json")
    
    if args.toolchain:
        toolchain_path = Path(args.toolchain)
        print(f"\n使用指定的工具链: {toolchain_path}")
    else:
        print("\n正在自动查找 ARM GCC 工具链...")
        toolchain_path = find_arm_toolchain()
        if not toolchain_path:
            print("❌ 未找到工具链！请使用 --toolchain 参数指定路径")
            return 1
        print(f"✅ 找到工具链: {toolchain_path}")
    
    print("\n正在查找 GCC 版本...")
    gcc_version = find_gcc_version(toolchain_path)
    if not gcc_version:
        print("❌ 未找到 GCC 版本！")
        return 1
    print(f"✅ 找到 GCC 版本: {gcc_version}")
    
    print(f"\n正在生成配置文件: {output_file}")
    config_content = generate_clangd_config(
        toolchain_path,
        gcc_version,
        compile_commands_path
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("\n" + "=" * 70)
    print("✅ 配置文件生成成功！")
    print("=" * 70)
    print(f"\n配置文件位置: {output_file}")
    
    print("\n下一步:")
    print("  1. 在 Trae IDE 中按 Ctrl+Shift+P")
    print("  2. 输入 'clangd' 并选择 'clangd: Restart language server'")
    print("  3. 或选择 'Developer: Reload Window'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
