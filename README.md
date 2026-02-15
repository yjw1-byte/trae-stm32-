# STM32 Clangd 配置工具

在 Trae IDE 中为 STM32 工程自动配置 clangd，实现代码跳转、补全和语法检查。

支持 Keil 和 CLion 两种工程类型！

---

## ✨ 特性

- 🚀 **自动识别**：从工程文件提取配置
- 🎯 **三脚本支持**：Keil 标准库、Keil CubeMX、CLion
- 🔧 **全系列兼容**：STM32 F0/F1/F2/F3/F4/F7/H7/L0/L1/L4/G0/G4
- ⚡ **一键配置**：只需运行一个脚本

---

## 📋 脚本选择

| 特性 | setup_clangd.py | setup_clangd_cubemx.py | setup_clangd_clion.py |
|------|------------------|-------------------------|-----------------------|
| **适用工程** | Keil 标准外设库工程 | Keil CubeMX 生成的工程 | CLion (CMake) 工程 |
| **目录结构** | Start、Library、User | Core、Drivers、Middlewares | CMake build 目录 |
| **驱动库** | 标准外设库 (StdPeriph) | HAL 库 | HAL 库 |
| **宏定义** | USE_STDPERIPH_DRIVER | USE_HAL_DRIVER | - |
| **配置来源** | 解析 .uvprojx | 解析 .uvprojx | 使用 compile_commands.json |

---

## 🚀 快速开始

### 1. 判断工程类型

- Keil 工程 + `Start/`、`Library/` → 用 `setup_clangd.py`
- Keil 工程 + `Core/`、`Drivers/` → 用 `setup_clangd_cubemx.py`
- CLion (CMake) 工程 → 用 `setup_clangd_clion.py`

### 2. 复制脚本到工程根目录

### 3. 运行脚本

```bash
# Keil 标准外设库工程
python setup_clangd.py

# Keil CubeMX 工程
python setup_clangd_cubemx.py

# CLion 工程
python setup_clangd_clion.py
```

### 4. 重启 clangd

- 按 `Ctrl+Shift+P`
- 输入 "clangd"
- 选择 **"clangd: Restart language server"**

---

## 📝 脚本功能

### setup_clangd.py（Keil 标准外设库）

- ✅ 从 Project.uvprojx 读取 IncludePath 和 Define
- ✅ 从 <Cpu> 标签提取 CPU 类型
- ✅ 自动识别 STM32 系列（F1/F4）和型号
- ✅ 添加 -mfloat-abi 和 -ffreestanding
- ✅ 检查并同步 USE_FULL_ASSERT
- ✅ 添加 -I. 提升鲁棒性
- ✅ 去重并保持 Keil 一致的顺序
- ✅ 生成 .clangd 和 compile_commands.json

### setup_clangd_cubemx.py（Keil CubeMX HAL 库）

- ✅ 支持 CubeMX 典型目录结构（Core、Drivers、Middlewares）
- ✅ 自动识别 USE_HAL_DRIVER
- ✅ 支持 STM32 全系列
- ✅ 所有标准脚本功能

### setup_clangd_clion.py（CLion CMake 工程）

- ✅ 自动查找 compile_commands.json
- ✅ 自动查找 ARM GCC 工具链
- ✅ 配置 sysroot 和系统头文件路径
- ✅ 支持 CLion 内置工具链和独立工具链
- ✅ 生成 .clangd 配置文件

---

## 🔄 日常使用

### Keil 工程（添加新文件/文件夹后）

每当添加了新的 C 源文件或源代码目录后：

1. 重新运行配置脚本
2. 重启 clangd

### CLion 工程（添加新文件/文件夹后）

CLion 工程**不需要重新运行脚本**！因为 compile_commands.json 会在 CLion 编译时自动更新。你只需要：

1. 在 CLion 中重新编译项目（更新 compile_commands.json）
2. 重启 clangd

---

## 📂 文件说明

- `setup_clangd.py` - Keil 标准外设库配置脚本
- `setup_clangd_cubemx.py` - Keil CubeMX HAL 库配置脚本
- `setup_clangd_clion.py` - CLion (CMake) 工程配置脚本
- `.clangd` - clangd 配置文件（必需）
- `compile_commands.json` - 编译命令数据库（CLion 必需）

---

## 💡 提示词

### Keil 标准外设库工程
> "帮我在这个 Keil STM32 工程目录下运行 setup_clangd.py 配置 clangd"

### Keil CubeMX 工程
> "帮我在这个 STM32CubeMX 生成的工程目录下运行 setup_clangd_cubemx.py 配置 clangd"

### CLion 工程
> "帮我在这个 CLion STM32 工程目录下运行 setup_clangd_clion.py 配置 clangd"

---

## 🔧 STM32 型号参考

### F1 系列
- `STM32F10X_LD` - 小容量 (16-32KB Flash)
- `STM32F10X_MD` - 中等容量 (64-128KB Flash) ⭐ 常用
- `STM32F10X_HD` - 大容量 (256-512KB Flash)
- `STM32F10X_XL` - 超大容量 (512-1024KB Flash)
- `STM32F10X_CL` - 互联型

### F4 系列
- `STM32F40_41xxx` - STM32F40x/F41x
- `STM32F427_437xx` - STM32F427/F437
- `STM32F429_439xx` - STM32F429/F439
- `STM32F446xx` - STM32F446
- `STM32F469_479xx` - STM32F469/F479

---

## 📄 许可证

MIT License
