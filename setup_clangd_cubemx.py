#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STM32CubeMX生成的Keil工程clangd自动配置脚本
使用方法：在STM32CubeMX生成的Keil工程根目录下运行此脚本
特点：
- 支持CubeMX典型目录结构（Core、Drivers、Middlewares等）
- 自动识别USE_HAL_DRIVER
- 支持STM32F0/F1/F2/F3/F4/F7/H7/L0/L1/L4/G0/G4等全系列
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
        "device": "",
        "is_cubemx": False
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
                if "Cortex-M0" in cpu_str:
                    result["cpu_type"] = "cortex-m0"
                elif "Cortex-M0+" in cpu_str:
                    result["cpu_type"] = "cortex-m0plus"
                elif "Cortex-M1" in cpu_str:
                    result["cpu_type"] = "cortex-m1"
                elif "Cortex-M3" in cpu_str:
                    result["cpu_type"] = "cortex-m3"
                elif "Cortex-M4" in cpu_str:
                    result["cpu_type"] = "cortex-m4"
                elif "Cortex-M7" in cpu_str:
                    result["cpu_type"] = "cortex-m7"
                elif "Cortex-M33" in cpu_str:
                    result["cpu_type"] = "cortex-m33"
            
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
                    
                    for d in defs:
                        if "USE_HAL_DRIVER" in d.upper():
                            result["is_cubemx"] = True
            break
        
    except Exception as e:
        print(f"警告: 解析工程文件时出错: {e}")
    
    return result


def detect_stm32_series_and_type(uvprojx_file):
    """检测STM32系列和类型"""
    series = "F1"
    stm32_type = "STM32F10X_MD"
    
    if uvprojx_file and os.path.exists(uvprojx_file):
        try:
            with open(uvprojx_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'startup_stm32(f[0-9])([0-9x]+)_([a-z0-9_]+)\.s', content, re.IGNORECASE)
            if match:
                series = match.group(1).upper()
                return series, f"STM32{series}xx"
            
            match = re.search(r'startup_stm32([fhlg][0-9])([0-9x]+)_([a-z0-9_]+)\.s', content, re.IGNORECASE)
            if match:
                series = match.group(1).upper()
                return series, f"STM32{series}xx"
            
            match = re.search(r'startup_([a-z0-9_]+)\.s', content, re.IGNORECASE)
            if match:
                startup_name = match.group(1).lower()
                if 'stm32f0' in startup_name:
                    return "F0", "STM32F0xx"
                elif 'stm32f1' in startup_name:
                    return "F1", "STM32F1xx"
                elif 'stm32f2' in startup_name:
                    return "F2", "STM32F2xx"
                elif 'stm32f3' in startup_name:
                    return "F3", "STM32F3xx"
                elif 'stm32f4' in startup_name:
                    return "F4", "STM32F4xx"
                elif 'stm32f7' in startup_name:
                    return "F7", "STM32F7xx"
                elif 'stm32h7' in startup_name:
                    return "H7", "STM32H7xx"
                elif 'stm32l0' in startup_name:
                    return "L0", "STM32L0xx"
                elif 'stm32l1' in startup_name:
                    return "L1", "STM32L1xx"
                elif 'stm32l4' in startup_name:
                    return "L4", "STM32L4xx"
                elif 'stm32g0' in startup_name:
                    return "G0", "STM32G0xx"
                elif 'stm32g4' in startup_name:
                    return "G4", "STM32G4xx"
            
        except Exception:
            pass
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith("startup") and file.endswith(".s"):
                file_lower = file.lower()
                if 'stm32f0' in file_lower:
                    return "F0", "STM32F0xx"
                elif 'stm32f1' in file_lower:
                    return "F1", "STM32F1xx"
                elif 'stm32f2' in file_lower:
                    return "F2", "STM32F2xx"
                elif 'stm32f3' in file_lower:
                    return "F3", "STM32F3xx"
                elif 'stm32f4' in file_lower:
                    return "F4", "STM32F4xx"
                elif 'stm32f7' in file_lower:
                    return "F7", "STM32F7xx"
                elif 'stm32h7' in file_lower:
                    return "H7", "STM32H7xx"
                elif 'stm32l0' in file_lower:
                    return "L0", "STM32L0xx"
                elif 'stm32l1' in file_lower:
                    return "L1", "STM32L1xx"
                elif 'stm32l4' in file_lower:
                    return "L4", "STM32L4xx"
                elif 'stm32g0' in file_lower:
                    return "G0", "STM32G0xx"
                elif 'stm32g4' in file_lower:
                    return "G4", "STM32G4xx"
    
    return series, stm32_type


def find_c_files():
    """查找所有C源文件"""
    c_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".c"):
                rel_path = os.path.relpath(os.path.join(root, file))
                c_files.append(rel_path.replace("\\", "/"))
    return c_files


def generate_clangd_config(project_dir, include_paths_keil, defines_keil, stm32_type, cpu_type):
    """生成.clangd配置文件"""
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
    
    float_abi_flag = "-mfloat-abi=soft"
    if cpu_type in ["cortex-m4", "cortex-m7", "cortex-m33"]:
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


def generate_compile_commands(project_dir, include_paths_keil, defines_keil, c_files, stm32_type, cpu_type):
    """生成compile_commands.json"""
    
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
    
    float_abi_flag = "-mfloat-abi=soft"
    if cpu_type in ["cortex-m4", "cortex-m7", "cortex-m33"]:
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
    print("STM32CubeMX工程clangd自动配置工具")
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
    
    series, stm32_type = detect_stm32_series_and_type(uvprojx_file)
    cpu_type = uvprojx_config.get("cpu_type", "cortex-m3")
    include_paths_keil = uvprojx_config.get("include_paths", [])
    defines_keil = uvprojx_config.get("defines", [])
    is_cubemx = uvprojx_config.get("is_cubemx", False)
    
    if not include_paths_keil:
        include_paths_keil = [".\\Core\\Inc", ".\\Drivers\\CMSIS\\Include", 
                             ".\\Drivers\\CMSIS\\Device\\ST\\STM32" + series + "xx\\Include",
                             ".\\Drivers\\STM32" + series + "xx_HAL_Driver\\Inc"]
    
    if not defines_keil:
        defines_keil = ["USE_HAL_DRIVER", "STM32" + series + "xx"]
        is_cubemx = True
    
    source_dirs_display = []
    for p in include_paths_keil:
        p = p.replace(".\\", "").replace("./", "")
        if p and p not in source_dirs_display:
            source_dirs_display.append(p)
    
    c_files = find_c_files()
    
    print(f"\n检测结果:")
    print(f"  工程类型: {'STM32CubeMX (HAL库)' if is_cubemx else '标准外设库'}")
    print(f"  STM32系列: STM32{series}")
    print(f"  STM32类型: {stm32_type}")
    print(f"  CPU内核: {cpu_type}")
    print(f"  芯片型号: {uvprojx_config.get('device', 'N/A')}")
    print(f"  源代码目录: {source_dirs_display[:5]}{'...' if len(source_dirs_display) > 5 else ''}")
    print(f"  C源文件数: {len(c_files)}")
    print(f"  宏定义: {defines_keil[:5]}{'...' if len(defines_keil) > 5 else ''}")
    
    print("\n正在生成配置文件...")
    
    clangd_content = generate_clangd_config(project_dir, include_paths_keil, defines_keil, stm32_type, cpu_type)
    with open(".clangd", "w", encoding="utf-8") as f:
        f.write(clangd_content)
    print("✓ 已生成: .clangd")
    
    compile_commands = generate_compile_commands(project_dir, include_paths_keil, defines_keil, c_files, stm32_type, cpu_type)
    with open("compile_commands.json", "w", encoding="utf-8") as f:
        json.dump(compile_commands, f, indent=2, ensure_ascii=False)
    print("✓ 已生成: compile_commands.json")
    
    print("\n" + "=" * 70)
    print("配置完成！")
    print("\n请按以下步骤操作:")
    print("  1. 在Trae IDE中按 Ctrl+Shift+P")
    print("  2. 输入 'clangd' 并选择 'clangd: Restart language server'")
    print("  3. 或选择 'Developer: Reload Window'")
    print("\n💡 提示: 添加新文件/文件夹后，请重新运行此脚本！")
    print("\n✨ 支持STM32全系列：F0/F1/F2/F3/F4/F7/H7/L0/L1/L4/G0/G4")
    print("=" * 70)


if __name__ == "__main__":
    main()
