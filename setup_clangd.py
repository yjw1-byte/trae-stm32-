#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keil STM32工程clangd自动配置脚本（优化版）
使用方法：在Keil工程根目录下运行此脚本
优化建议来源：基于 .clangd 与 Project.uvprojx 的实际内容分析
"""

import os
import json
import glob
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def find_keil_project():
    """查找Keil工程文件"""
    uvprojx_files = glob.glob("*.uvprojx")
    if uvprojx_files:
        return uvprojx_files[0]
    return None


def get_project_dir():
    """获取项目根目录绝对路径"""
    return os.path.abspath(os.getcwd())


def parse_uvprojx(uvprojx_file):
    """解析Keil工程文件，提取配置"""
    result = {
        "include_paths": [],
        "defines": [],
        "cpu_type": "cortex-m3",
        "device": ""
    }
    
    if not uvprojx_file or not os.path.exists(uvprojx_file):
        return result
    
    try:
        tree = ET.parse(uvprojx_file)
        root = tree.getroot()
        
        ns = ""
        if "}" in root.tag:
            ns = root.tag.split("}")[0] + "}"
        
        def find_text(elem, path):
            found = elem.find(path)
            return found.text if found is not None else ""
        
        for target in root.findall(f".//{ns}Target"):
            target_option = target.find(f".//{ns}TargetOption")
            if target_option is None:
                continue
            
            target_common = target_option.find(f".//{ns}TargetCommonOption")
            if target_common is not None:
                result["device"] = find_text(target_common, f".//{ns}Device")
                cpu_str = find_text(target_common, f".//{ns}Cpu")
                if "Cortex-M3" in cpu_str:
                    result["cpu_type"] = "cortex-m3"
                elif "Cortex-M4" in cpu_str:
                    result["cpu_type"] = "cortex-m4"
            
            target_arm_ads = target_option.find(f".//{ns}TargetArmAds")
            if target_arm_ads is None:
                continue
            
            cads = target_arm_ads.find(f".//{ns}Cads")
            if cads is None:
                continue
            
            various_controls = cads.find(f".//{ns}VariousControls")
            if various_controls is not None:
                include_path_str = find_text(various_controls, f".//{ns}IncludePath")
                define_str = find_text(various_controls, f".//{ns}Define")
                
                if include_path_str:
                    paths = [p.strip() for p in include_path_str.split(";") if p.strip()]
                    result["include_paths"] = paths
                
                if define_str:
                    defs = [d.strip() for d in define_str.split(",") if d.strip()]
                    result["defines"] = defs
            break
        
    except Exception as e:
        print(f"警告: 解析工程文件时出错: {e}")
    
    return result


def check_use_full_assert():
    """检查stm32f10x_conf.h中是否启用了USE_FULL_ASSERT"""
    conf_files = glob.glob("**/stm32f10x_conf.h", recursive=True)
    for conf_file in conf_files:
        try:
            with open(conf_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if re.search(r'#define\s+USE_FULL_ASSERT', content):
                    return True
        except Exception:
            pass
    return False


def detect_stm32_type_from_uvprojx_content(uvprojx_file):
    """从Keil工程文件中检测STM32类型"""
    if not uvprojx_file or not os.path.exists(uvprojx_file):
        return None, "F1"
    
    try:
        with open(uvprojx_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'startup_stm32(f[0-9])([0-9x]+)_([a-z0-9_]+)\.s', content, re.IGNORECASE)
        if match:
            family_match = match.group(1).upper()
            suffix = match.group(3).upper()
            
            if family_match == "F1":
                type_map = {
                    "LD": "STM32F10X_LD",
                    "LD_VL": "STM32F10X_LD_VL",
                    "MD": "STM32F10X_MD",
                    "MD_VL": "STM32F10X_MD_VL",
                    "HD": "STM32F10X_HD",
                    "HD_VL": "STM32F10X_HD_VL",
                    "XL": "STM32F10X_XL",
                    "CL": "STM32F10X_CL",
                }
                return type_map.get(suffix, "STM32F10X_MD"), "F1"
            elif family_match == "F4":
                type_map = {
                    "40X": "STM32F40_41xxx",
                    "41X": "STM32F40_41xxx",
                    "427X": "STM32F427_437xx",
                    "437X": "STM32F427_437xx",
                    "429X": "STM32F429_439xx",
                    "439X": "STM32F429_439xx",
                    "446X": "STM32F446xx",
                    "469X": "STM32F469_479xx",
                    "479X": "STM32F469_479xx",
                }
                return type_map.get(suffix, "STM32F40_41xxx"), "F4"
        
        if not match:
            match = re.search(r'startup_stm32f4([0-9x]+)_([a-z0-9_]+)\.s', content, re.IGNORECASE)
            if match:
                return "STM32F40_41xxx", "F4"
            
    except Exception:
        pass
    
    return None, "F1"


def detect_stm32_family_and_type(uvprojx_file):
    """综合检测STM32系列和类型"""
    stm32_type, family = detect_stm32_type_from_uvprojx_content(uvprojx_file)
    
    if stm32_type:
        return stm32_type, family
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith("startup") and file.endswith(".s"):
                if "stm32f4" in file.lower():
                    return "STM32F40_41xxx", "F4"
                elif "stm32f1" in file.lower():
                    return "STM32F10X_MD", "F1"
    
    return "STM32F10X_MD", "F1"


def find_c_files():
    """查找所有C源文件"""
    c_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".c"):
                rel_path = os.path.relpath(os.path.join(root, file))
                c_files.append(rel_path.replace("\\", "/"))
    return c_files


def generate_clangd_config(project_dir, include_paths_keil, defines_keil, stm32_type, cpu_type, use_full_assert):
    """生成.clangd配置文件（优化版）"""
    project_dir_slash = project_dir.replace("\\", "/")
    
    include_flags = []
    include_flags.append(f'-I{project_dir_slash}')
    
    seen_paths = set()
    for path in include_paths_keil:
        path = path.strip()
        if not path:
            continue
        
        path_abs = path
        if path.startswith(".\\"):
            path_abs = path[2:]
        elif path.startswith("./"):
            path_abs = path[2:]
        
        path_key = path_abs.lower()
        if path_key not in seen_paths:
            include_flags.append(f'-I{project_dir_slash}/{path_abs}')
            seen_paths.add(path_key)
    
    define_flags = []
    define_flags.append(f'-D{stm32_type}')
    for d in defines_keil:
        d = d.strip()
        if d:
            define_flags.append(f'-D{d}')
    
    if use_full_assert and "USE_FULL_ASSERT" not in [d.upper() for d in defines_keil]:
        define_flags.append('-DUSE_FULL_ASSERT')
    
    float_abi_flag = "-mfloat-abi=soft"
    if cpu_type == "cortex-m4":
        float_abi_flag = "-mfloat-abi=softfp"
    
    config = f"""CompileFlags:
  Add:
    - "-target"
    - "arm-none-eabi"
    - "-mcpu={cpu_type}"
    - "-mthumb"
    - "{float_abi_flag}"
    - "-ffreestanding"
    - "-std=c99"
"""
    for d in define_flags:
        config += f'    - "{d}"\n'
    for inc in include_flags:
        config += f'    - "{inc}"\n'
    
    config += """  Remove:
    - "-std=c++17"
Diagnostics:
  UnusedIncludes: None
  Suppress:
    - "implicit-function-declaration"
    - "unused-parameter"
    - "undeclared_var_use"
    - "unknown_typename"
    - "unused-include"
"""
    return config


def generate_compile_commands(project_dir, include_paths_keil, defines_keil, c_files, stm32_type, cpu_type, use_full_assert):
    """生成compile_commands.json（优化版）"""
    
    include_flags_list = []
    include_flags_list.append("-I.")
    
    seen_paths = set()
    for path in include_paths_keil:
        path = path.strip()
        if not path:
            continue
        
        path_abs = path
        if path.startswith(".\\"):
            path_abs = path[2:]
        elif path.startswith("./"):
            path_abs = path[2:]
        
        path_key = path_abs.lower()
        if path_key not in seen_paths:
            include_flags_list.append(f'-I{path_abs}')
            seen_paths.add(path_key)
    
    define_flags_list = []
    define_flags_list.append(f'-D{stm32_type}')
    for d in defines_keil:
        d = d.strip()
        if d:
            define_flags_list.append(f'-D{d}')
    
    if use_full_assert and "USE_FULL_ASSERT" not in [d.upper() for d in defines_keil]:
        define_flags_list.append('-DUSE_FULL_ASSERT')
    
    float_abi_flag = "-mfloat-abi=soft"
    if cpu_type == "cortex-m4":
        float_abi_flag = "-mfloat-abi=softfp"
    
    include_flags = " ".join(include_flags_list)
    define_flags = " ".join(define_flags_list)
    
    commands = []
    for c_file in c_files:
        command = f'arm-none-eabi-gcc -c -mcpu={cpu_type} -mthumb {float_abi_flag} -ffreestanding -std=c99 {define_flags} {include_flags} {c_file}'
        commands.append({
            "directory": project_dir,
            "command": command,
            "file": c_file
        })
    return commands


def main():
    print("=" * 70)
    print("Keil STM32工程clangd自动配置工具（优化版）")
    print("=" * 70)
    
    project_dir = get_project_dir()
    print(f"\n项目目录: {project_dir}")
    
    uvprojx_file = find_keil_project()
    if uvprojx_file:
        print(f"找到Keil工程: {uvprojx_file}")
    else:
        print("警告: 未找到.uvprojx工程文件，将使用默认配置")
    
    print("\n正在解析工程配置...")
    uvprojx_config = parse_uvprojx(uvprojx_file)
    
    stm32_type, family = detect_stm32_family_and_type(uvprojx_file)
    cpu_type = uvprojx_config.get("cpu_type", "cortex-m3")
    include_paths_keil = uvprojx_config.get("include_paths", [".\\Start", ".\\Library", ".\\User", ".\\System", ".\\Hardware"])
    defines_keil = uvprojx_config.get("defines", ["USE_STDPERIPH_DRIVER"])
    
    use_full_assert = check_use_full_assert()
    
    source_dirs_display = []
    for p in include_paths_keil:
        p = p.replace(".\\", "").replace("./", "")
        if p and p not in source_dirs_display:
            source_dirs_display.append(p)
    
    c_files = find_c_files()
    
    print(f"\n检测结果:")
    print(f"  STM32系列: STM32{family}")
    print(f"  STM32类型: {stm32_type}")
    print(f"  CPU内核: {cpu_type}")
    print(f"  芯片型号: {uvprojx_config.get('device', 'N/A')}")
    print(f"  源代码目录: {source_dirs_display}")
    print(f"  C源文件数: {len(c_files)}")
    print(f"  宏定义: {defines_keil}")
    print(f"  USE_FULL_ASSERT: {'启用' if use_full_assert else '未启用'}")
    
    print("\n正在生成配置文件...")
    
    clangd_content = generate_clangd_config(project_dir, include_paths_keil, defines_keil, stm32_type, cpu_type, use_full_assert)
    with open(".clangd", "w", encoding="utf-8") as f:
        f.write(clangd_content)
    print("✓ 已生成: .clangd")
    
    compile_commands = generate_compile_commands(project_dir, include_paths_keil, defines_keil, c_files, stm32_type, cpu_type, use_full_assert)
    with open("compile_commands.json", "w", encoding="utf-8") as f:
        json.dump(compile_commands, f, indent=2, ensure_ascii=False)
    print("✓ 已生成: compile_commands.json")
    
    print("\n" + "=" * 70)
    print("优化配置完成！")
    print("\n应用的优化:")
    print("  ✓ 从 Project.uvprojx 读取 IncludePath 和 Define")
    print("  ✓ 从 <Cpu> 标签提取 CPU 类型")
    print("  ✓ 添加 -mfloat-abi 和 -ffreestanding")
    print("  ✓ 检查并同步 USE_FULL_ASSERT")
    print("  ✓ 添加 -I. 提升鲁棒性")
    print("  ✓ 去重并保持 Keil 一致的顺序")
    print("\n请按以下步骤操作:")
    print("  1. 在Trae IDE中按 Ctrl+Shift+P")
    print("  2. 输入 'clangd' 并选择 'clangd: Restart language server'")
    print("  3. 或选择 'Developer: Reload Window'")
    print("\n💡 提示: 添加新文件/文件夹后，请重新运行此脚本！")
    print("\n✨ 支持STM32F1和STM32F4系列自动识别")
    print("=" * 70)


if __name__ == "__main__":
    main()
