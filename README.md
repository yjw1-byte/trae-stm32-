# STM32 Clangd 配置工具

在 Trae IDE 中为 Keil STM32 工程自动配置 clangd，实现代码跳转、补全和语法检查。

---

## ✨ 特性

- 🚀 **自动识别**：从 Keil 工程文件提取配置
- 🎯 **双脚本支持**：标准外设库和 CubeMX HAL 库
- 🔧 **全系列兼容**：STM32 F0/F1/F2/F3/F4/F7/H7/L0/L1/L4/G0/G4
- ⚡ **一键配置**：只需运行一个脚本

---

## 📋 脚本选择

| 特性 | setup_clangd.py | setup_clangd_cubemx.py |
|------|------------------|-------------------------|
| **适用工程** | 标准外设库工程（如江科大教程） | STM32CubeMX 生成的工程（HAL 库） |
| **目录结构** | Start、Library、User、System、Hardware | Core、Drivers、Middlewares |
| **驱动库** | 标准外设库 (StdPeriph) | HAL 库 |
| **宏定义** | USE_STDPERIPH_DRIVER | USE_HAL_DRIVER |
| **支持的系列** | F1、F4 | F0/F1/F2/F3/F4/F7/H7/L0/L1/L4/G0/G4 全系列 |

---

## 🚀 快速开始

### 1. 判断工程类型

- 有 `Start/`、`Library/` 目录 → 用 `setup_clangd.py`
- 有 `Core/`、`Drivers/` 目录 → 用 `setup_clangd_cubemx.py`

### 2. 复制脚本到工程根目录

### 3. 运行脚本

```bash
# 标准外设库工程
python setup_clangd.py

# CubeMX 工程
python setup_clangd_cubemx.py
```

### 4. 重启 clangd

- 按 `Ctrl+Shift+P`
- 输入 "clangd"
- 选择 **"clangd: Restart language server"**

---

## 📝 脚本功能

### setup_clangd.py（标准外设库）

- ✅ 从 Project.uvprojx 读取 IncludePath 和 Define
- ✅ 从 <Cpu> 标签提取 CPU 类型
- ✅ 自动识别 STM32 系列（F1/F4）和型号
- ✅ 添加 -mfloat-abi 和 -ffreestanding
- ✅ 检查并同步 USE_FULL_ASSERT
- ✅ 添加 -I. 提升鲁棒性
- ✅ 去重并保持 Keil 一致的顺序
- ✅ 生成 .clangd 和 compile_commands.json

### setup_clangd_cubemx.py（CubeMX HAL 库）

- ✅ 支持 CubeMX 典型目录结构（Core、Drivers、Middlewares）
- ✅ 自动识别 USE_HAL_DRIVER
- ✅ 支持 STM32 全系列
- ✅ 所有标准脚本功能

---

## 🔄 日常使用

### 添加新文件/文件夹后

每当添加了新的 C 源文件或源代码目录后：

1. 重新运行配置脚本
2. 重启 clangd

---

## 📂 文件说明

- `setup_clangd.py` - 标准外设库配置脚本
- `setup_clangd_cubemx.py` - CubeMX HAL 库配置脚本
- `.clangd` - clangd 配置文件（必需）
- `compile_commands.json` - 编译命令数据库（可选）

---

## 💡 提示词

### 标准外设库工程
> "帮我在这个 Keil STM32 工程目录下运行 setup_clangd.py 配置 clangd"

### CubeMX 工程
> "帮我在这个 STM32CubeMX 生成的工程目录下运行 setup_clangd_cubemx.py 配置 clangd"

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
